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
    assert isinstance(data["source_status"], dict)

    # Strict live-only: no known fallback summary wording should be returned
    assert data["ai_insights"]["daily_brief"] != "No live AI briefing returned."
    assert data["ai_insights"]["roadmap_inference"] != "No roadmap inference returned."


def test_briefing_source_status_and_live_ai_indicator(api_base: str, api_client: requests.Session):
    """Briefing source status should be explicit, with AI marked live for dashboard insights."""
    payload = {"competitor_a": "Stripe", "competitor_b": "Adyen"}
    response = _request_with_retry("post", f"{api_base}/intelligence/briefing", json=payload)
    assert response.status_code == 200

    data = response.json()
    source_status = data["source_status"]
    assert source_status["competitor_a"] in {"crustdata-live", "crustdata-empty"}
    assert source_status["competitor_b"] in {"crustdata-live", "crustdata-empty"}
    assert source_status["ai"] == "openai-live"

    # If AI is marked live, unavailable placeholders should not be returned.
    assert data["ai_insights"]["daily_brief"] != "Live AI briefing unavailable."
    assert data["ai_insights"]["roadmap_inference"] != "Live AI roadmap inference unavailable."


def test_live_only_empty_channels_for_missing_companies(api_base: str, api_client: requests.Session):
    """Unknown competitors should return explicit empty live channels (no fabricated records)."""
    payload = {"competitor_a": "NoCompanyZXQK", "competitor_b": "NoCompanyYTRP"}
    response = _request_with_retry("post", f"{api_base}/intelligence/briefing", json=payload)
    assert response.status_code == 200

    data = response.json()
    comp_a = data["competitor_a"]
    comp_b = data["competitor_b"]
    source_status = data["source_status"]

    assert source_status["competitor_a"] == "crustdata-empty"
    assert source_status["competitor_b"] == "crustdata-empty"

    for company_data in [comp_a, comp_b]:
        assert company_data["social_activity"] == []
        assert company_data["hiring_signals"] == []
        assert company_data["news_coverage"] == []
        assert company_data["product_changes"] == []
        assert company_data["sentiment_trend"] == []


def test_empty_company_summary_not_overwritten_with_synthetic_text(api_base: str, api_client: requests.Session):
    """Empty competitors must keep explicit no-live-records summary text."""
    payload = {"competitor_a": "NoCompanyZXQK", "competitor_b": "NoCompanyYTRP"}
    response = _request_with_retry("post", f"{api_base}/intelligence/briefing", json=payload)
    assert response.status_code == 200

    data = response.json()
    for company_data in [data["competitor_a"], data["competitor_b"]]:
        assert company_data["strategic_summary"] == "No live records returned for this company."
        assert "hiring focus includes" not in company_data["strategic_summary"].lower()


def test_briefing_response_schema_includes_product_and_source_fields(api_base: str, api_client: requests.Session):
    """Briefing payload should expose required schema fields for dashboard rendering."""
    payload = {"competitor_a": "Stripe", "competitor_b": "Adyen"}
    response = _request_with_retry("post", f"{api_base}/intelligence/briefing", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert set(data["source_status"].keys()) == {"competitor_a", "competitor_b", "ai"}

    for company_data in [data["competitor_a"], data["competitor_b"]]:
        assert isinstance(company_data["news_coverage"], list)
        assert isinstance(company_data["product_changes"], list)
        assert isinstance(company_data["strategic_summary"], str)

        if company_data["product_changes"]:
            first_change = company_data["product_changes"][0]
            assert "change_summary" in first_change
            assert isinstance(first_change["change_summary"], str)


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
