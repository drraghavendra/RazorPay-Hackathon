import asyncio
import logging
import os
from typing import Any, Dict, List

import httpx


logger = logging.getLogger(__name__)


class CrustdataAPIService:
    def __init__(self):
        self.api_key = os.environ.get("CRUSTDATA_API_KEY")
        self.base_url = os.environ.get("CRUSTDATA_BASE_URL")
        self.timeout = float(os.environ.get("CRUSTDATA_TIMEOUT_SECONDS", "20"))

    @property
    def is_configured(self) -> bool:
        if not self.api_key or not self.base_url:
            return False
        return "placeholder" not in self.api_key.lower() and self.api_key.strip() != ""

    async def _request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any] | None:
        if not self.is_configured:
            return None

        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-API-Key": self.api_key,
            "Accept": "application/json",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params, headers=headers)
                response.raise_for_status()
                return response.json()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Crustdata request failed for %s: %s", endpoint, exc)
            return None

    @staticmethod
    def _extract_records(payload: Dict[str, Any] | None) -> List[Dict[str, Any]]:
        if not payload:
            return []
        for key in ["data", "results", "items", "records", "posts", "job_listings", "alerts"]:
            value = payload.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        return []

    async def fetch_company_intelligence(self, company: str, rival: str) -> Dict[str, Any]:
        endpoints = {
            "social_activity": (
                "/screener/linkedin_posts",
                {"query": company, "fields": "reactors,comments", "limit": 8},
            ),
            "keyword_trends": (
                "/screener/linkedin_posts/keyword_search",
                {
                    "keywords": f"{company} AI payments,{rival} fraud detection,OpenAI fintech",
                    "limit": 8,
                },
            ),
            "people_intelligence": (
                "/screener/persondb/search",
                {"query": company, "limit": 6},
            ),
            "company_health": (
                "/screener/company",
                {
                    "company": company,
                    "fields": "headcount,job_openings,web_traffic,glassdoor",
                },
            ),
            "hiring_signals": (
                "/data_lab/job_listings/Table",
                {"company": company, "limit": 8},
            ),
            "employee_sentiment": (
                "/data_lab/glassdoor_profile_metric",
                {"company": company, "metric": "overall_rating"},
            ),
            "news_coverage": (
                "/screener/web-search",
                {"query": f"{company} product announcement", "limit": 8},
            ),
            "product_changes": (
                "/screener/web-fetch",
                {"url": f"https://{company.lower()}.com/pricing"},
            ),
            "executive_movements": (
                "/watcher",
                {"query": f"{company} executive movement", "limit": 6},
            ),
        }

        async def fetch_with_name(name: str, spec: tuple[str, Dict[str, Any]]):
            endpoint, params = spec
            return name, await self._request(endpoint, params)

        tasks = [fetch_with_name(name, spec) for name, spec in endpoints.items()]
        results = await asyncio.gather(*tasks)
        payloads = {name: data for name, data in results}

        social_records = self._extract_records(payloads["social_activity"])
        keyword_records = self._extract_records(payloads["keyword_trends"])
        people_records = self._extract_records(payloads["people_intelligence"])
        hiring_records = self._extract_records(payloads["hiring_signals"])
        sentiment_records = self._extract_records(payloads["employee_sentiment"])
        news_records = self._extract_records(payloads["news_coverage"])
        product_records = self._extract_records(payloads["product_changes"])
        executive_records = self._extract_records(payloads["executive_movements"])

        company_health_payload = payloads.get("company_health") or {}
        company_health_records = self._extract_records(company_health_payload)
        company_health = company_health_records[0] if company_health_records else company_health_payload

        normalized = {
            "company_name": company,
            "social_activity": [
                {
                    "post_content": item.get("text") or item.get("content") or "LinkedIn post",
                    "reactor_count": item.get("reactors_count")
                    or item.get("num_reactors")
                    or len(item.get("reactors", []) if isinstance(item.get("reactors"), list) else []),
                    "top_reactors": [
                        {
                            "name": reactor.get("name", "Unknown"),
                            "title": reactor.get("title", "Unknown"),
                            "company": reactor.get("company", "Unknown"),
                        }
                        for reactor in (item.get("reactors", [])[:3] if isinstance(item.get("reactors"), list) else [])
                    ],
                }
                for item in social_records[:5]
            ],
            "keyword_trends": [
                {
                    "keyword": item.get("keyword") or item.get("query") or company,
                    "mentions": item.get("count") or item.get("mentions") or 0,
                }
                for item in keyword_records[:5]
            ],
            "people_intelligence": [
                {
                    "name": item.get("name", "Unknown"),
                    "current_company": item.get("current_company") or item.get("company") or "Unknown",
                    "previous_company": item.get("previous_company") or item.get("past_company") or company,
                    "title": item.get("title") or item.get("job_title") or "Unknown",
                }
                for item in people_records[:5]
            ],
            "company_metrics": {
                "headcount": company_health.get("headcount") or company_health.get("employee_count") or 0,
                "headcount_growth_pct": company_health.get("headcount_growth")
                or company_health.get("employee_growth_pct")
                or 0,
                "job_openings": company_health.get("job_openings") or company_health.get("open_roles") or 0,
                "web_traffic_index": company_health.get("web_traffic") or company_health.get("traffic_index") or 0,
                "glassdoor_rating": company_health.get("glassdoor") or company_health.get("glassdoor_rating") or 0,
            },
            "hiring_signals": [
                {
                    "job_title": item.get("title") or item.get("job_title") or "Unknown role",
                    "department": item.get("department") or item.get("team") or "General",
                    "location": item.get("location") or "Unknown",
                    "posting_date": item.get("date_posted") or item.get("posting_date") or "Unknown",
                }
                for item in hiring_records[:8]
            ],
            "sentiment_trend": [
                {
                    "month": item.get("month") or item.get("period") or f"M{idx+1}",
                    "rating": item.get("rating") or item.get("value") or 0,
                }
                for idx, item in enumerate(sentiment_records[:6])
            ],
            "news_coverage": [
                {
                    "title": item.get("title") or "News mention",
                    "source": item.get("source") or item.get("publisher") or "Web",
                    "published_at": item.get("published_at") or item.get("date") or "Unknown",
                    "url": item.get("url") or "",
                }
                for item in news_records[:6]
            ],
            "product_changes": [
                {
                    "page": item.get("page") or item.get("url") or "Product page",
                    "change_summary": item.get("summary") or item.get("change") or "Change detected",
                    "detected_at": item.get("detected_at") or item.get("timestamp") or "Unknown",
                }
                for item in product_records[:5]
            ],
            "executive_movements": [
                {
                    "name": item.get("name") or "Unknown executive",
                    "movement": item.get("movement") or item.get("description") or "Leadership signal detected",
                    "date": item.get("date") or item.get("detected_at") or "Unknown",
                }
                for item in executive_records[:4]
            ],
        }

        has_live_data = any(
            [
                normalized["social_activity"],
                normalized["hiring_signals"],
                normalized["news_coverage"],
                normalized["keyword_trends"],
            ]
        )

        normalized["source"] = "crustdata-live" if has_live_data else "crustdata-empty"
        normalized["has_live_data"] = has_live_data
        return normalized