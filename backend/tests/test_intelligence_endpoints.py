"""Core intelligence endpoint regression tests for ShadowIntel MVP."""

import os
from pathlib import Path
from typing import Any, Dict

import pytest
import requests
from dotenv import load_dotenv


load_dotenv("/app/frontend/.env")

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL")


def _require_base_url() -> str:
    if not BASE_URL:
        pytest.skip("REACT_APP_BACKEND_URL not set")
    return BASE_URL.rstrip("/")


@pytest.fixture(scope="session")
def api_base() -> str:
    return f"{_require_base_url()}/api"


@pytest.fixture(scope="session")
def api_client() -> requests.Session:
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json"})
    return session


def _request_with_retry(method: str, url: str, **kwargs) -> requests.Response:
    first = requests.request(method=method, url=url, timeout=60, **kwargs)
    if first.status_code >= 500:
        return requests.request(method=method, url=url, timeout=60, **kwargs)
    return first


def test_health_endpoint(api_base: str, api_client: requests.Session):
    """Health endpoint returns service status payload."""
    response = api_client.get(f"{api_base}/health", timeout=30)
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "shadowintel-backend"
    assert isinstance(data["timestamp"], str)


def test_generate_briefing_and_validate_schema(api_base: str, api_client: requests.Session):
    """Briefing generation returns persisted intelligence payload structure."""
    payload = {"competitor_a": "Stripe", "competitor_b": "Adyen"}
    response = _request_with_retry("post", f"{api_base}/intelligence/briefing", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["competitor_a"]["company_name"] == "Stripe"
    assert data["competitor_b"]["company_name"] == "Adyen"
    assert isinstance(data["report_id"], str) and len(data["report_id"]) > 0
    assert "daily_brief" in data["ai_insights"]
    assert isinstance(data["comparison"], dict)


def test_latest_briefing_returns_expected_competitors(api_base: str, api_client: requests.Session):
    """Latest endpoint returns last report for requested competitor pair."""
    params = {"competitor_a": "Stripe", "competitor_b": "Adyen"}
    response = _request_with_retry("get", f"{api_base}/intelligence/latest", params=params)
    assert response.status_code == 200

    data = response.json()
    assert data["competitor_a"]["company_name"] == "Stripe"
    assert data["competitor_b"]["company_name"] == "Adyen"
    assert isinstance(data["source_status"], dict)


def test_comparison_endpoint_returns_metrics(api_base: str, api_client: requests.Session):
    """Comparison endpoint exposes side-by-side numeric metrics for charting."""
    params = {"competitor_a": "Stripe", "competitor_b": "Adyen"}
    response = _request_with_retry("get", f"{api_base}/intelligence/comparison", params=params)
    assert response.status_code == 200

    data = response.json()
    assert data["competitor_a"] == "Stripe"
    assert data["competitor_b"] == "Adyen"
    assert isinstance(data["metrics"]["headcount"]["a"], int)
    assert isinstance(data["metrics"]["headcount"]["b"], int)
    assert "social_engagement" in data["metrics"]


def test_chat_endpoint_returns_answer(api_base: str, api_client: requests.Session):
    """Chat endpoint answers strategic question with timestamped response."""
    payload: Dict[str, Any] = {
        "competitor_a": "Stripe",
        "competitor_b": "Adyen",
        "question": "What signals indicate which competitor is accelerating in AI features?",
        "history": [{"role": "user", "content": "Compare recent signals"}],
    }

    response = _request_with_retry("post", f"{api_base}/intelligence/chat", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["competitor_a"] == "Stripe"
    assert data["competitor_b"] == "Adyen"
    assert isinstance(data["answer"], str) and len(data["answer"].strip()) > 0
    assert isinstance(data["timestamp"], str)
