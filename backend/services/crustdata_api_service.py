import asyncio
import logging
import os
from typing import Any, Dict, List
from datetime import datetime

import httpx


logger = logging.getLogger(__name__)


class CrustdataAPIService:
    def __init__(self):
        self.api_key = os.environ.get("CRUSTDATA_API_KEY")
        self.base_url = os.environ.get("CRUSTDATA_BASE_URL")
        self.timeout = float(os.environ.get("CRUSTDATA_TIMEOUT_SECONDS", "20"))
        self.api_version = os.environ.get("CRUSTDATA_API_VERSION", "2025-11-01")

    @property
    def is_configured(self) -> bool:
        if not self.api_key or not self.base_url:
            return False
        return "placeholder" not in self.api_key.lower() and self.api_key.strip() != ""

    async def _request(
        self,
        endpoint: str,
        method: str = "GET",
        params: Dict[str, Any] | None = None,
        json_data: Dict[str, Any] | None = None,
    ) -> Dict[str, Any] | List[Any] | None:
        if not self.is_configured:
            return None

        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-API-Key": self.api_key,
            "Accept": "application/json",
            "x-api-version": self.api_version,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    headers=headers,
                )
                response.raise_for_status()
                return response.json()
        except Exception as exc:  # noqa: BLE001
            logger.warning("Crustdata request failed for %s [%s]: %s", endpoint, method, exc)
            return None

    @staticmethod
    def _extract_records(payload: Dict[str, Any] | List[Any] | None) -> List[Dict[str, Any]]:
        if not payload:
            return []
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        for key in ["data", "results", "items", "records", "posts", "job_listings", "alerts"]:
            value = payload.get(key)  # type: ignore[union-attr]
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        return []

    @staticmethod
    def _select_best_company_record(records: List[Dict[str, Any]], company: str) -> Dict[str, Any]:
        if not records:
            return {}
        exact = [
            item
            for item in records
            if str(item.get("company_name", "")).strip().lower() == company.strip().lower()
        ]
        if exact:
            return exact[0]
        return records[0]

    async def _keyword_mentions(self, keyword: str) -> int:
        payload = await self._request(
            "/screener/linkedin_posts/keyword_search",
            method="POST",
            json_data={"query": keyword, "limit": 12},
        )
        return len(self._extract_records(payload))

    async def fetch_company_intelligence(self, company: str, rival: str) -> Dict[str, Any]:
        company_payload_task = self._request(
            "/screener/company",
            method="GET",
            params={
                "company_name": company,
                "fields": (
                    "company_name,headcount.linkedin_headcount,"
                    "headcount.linkedin_headcount_total_growth_percent.qoq,"
                    "job_openings.job_openings_count,job_openings.recent_job_openings,"
                    "job_openings.job_openings_count_growth_percent.qoq,"
                    "web_traffic.monthly_visitors,"
                    "glassdoor.glassdoor_overall_rating,glassdoor.glassdoor_review_count"
                ),
                "limit": 5,
            },
        )

        social_payload_task = self._request(
            "/screener/linkedin_posts",
            method="GET",
            params={
                "company_name": company,
                "fields": "text,total_reactions,total_comments,actor_name,date_posted,num_shares",
                "limit": 5,
            },
        )

        people_payload_task = self._request(
            "/screener/persondb/search",
            method="POST",
            json_data={
                "filters": {
                    "column": "experience.all_employer",
                    "type": "in",
                    "value": [company],
                },
                "limit": 3,
            },
        )

        keyword_queries = [
            f"{company} AI payments",
            f"{rival} fraud detection",
            "OpenAI fintech",
        ]
        keyword_tasks = [self._keyword_mentions(query) for query in keyword_queries]

        news_task = self._request(
            "/screener/web-search",
            method="POST",
            json_data={"query": f"{company} product announcement", "limit": 6},
        )
        product_changes_task = self._request(
            "/screener/web-fetch",
            method="POST",
            json_data={"url": f"https://{company.lower()}.com/pricing"},
        )

        company_payload, social_payload, people_payload, keyword_counts, news_payload, product_payload = await asyncio.gather(
            company_payload_task,
            social_payload_task,
            people_payload_task,
            asyncio.gather(*keyword_tasks),
            news_task,
            product_changes_task,
        )

        company_records = self._extract_records(company_payload)
        company_health = self._select_best_company_record(company_records, company)
        social_records = self._extract_records(social_payload)
        news_records = self._extract_records(news_payload)
        product_records = self._extract_records(product_payload)
        people_records = self._extract_records(people_payload)

        if people_payload and isinstance(people_payload, dict) and not people_records:
            people_records = [item for item in people_payload.get("profiles", []) if isinstance(item, dict)]

        headcount_block = company_health.get("headcount") or {}
        job_block = company_health.get("job_openings") or {}
        web_traffic_block = company_health.get("web_traffic") or {}
        glassdoor_block = company_health.get("glassdoor") or {}

        glassdoor_rating = float(glassdoor_block.get("glassdoor_overall_rating") or 0)
        current_month = datetime.now().strftime("%b")
        sentiment_points = (
            [{"month": current_month, "rating": round(glassdoor_rating, 2)}]
            if glassdoor_rating > 0
            else []
        )

        hiring_signals = []
        for job in job_block.get("recent_job_openings", [])[:8]:
            if not isinstance(job, dict):
                continue
            hiring_signals.append(
                {
                    "job_title": job.get("job_title") or job.get("title") or "Unknown role",
                    "department": job.get("department") or job.get("job_function") or "General",
                    "location": job.get("location") or job.get("country") or "Unknown",
                    "posting_date": job.get("posted_at") or job.get("date_posted") or "Unknown",
                }
            )

        normalized = {
            "company_name": company,
            "social_activity": [
                {
                    "post_content": item.get("text") or "LinkedIn post",
                    "reactor_count": item.get("total_reactions") or 0,
                    "comment_count": item.get("total_comments") or 0,
                    "actor_name": item.get("actor_name") or company,
                    "posted_on": item.get("date_posted") or "",
                }
                for item in social_records[:5]
            ],
            "keyword_trends": [
                {
                    "keyword": keyword,
                    "mentions": keyword_counts[index] if index < len(keyword_counts) else 0,
                }
                for index, keyword in enumerate(keyword_queries)
            ],
            "people_intelligence": [
                {
                    "name": item.get("name") or item.get("person_name") or "Unknown",
                    "current_company": (
                        (item.get("current_employers") or [{}])[0].get("name")
                        if isinstance(item.get("current_employers"), list)
                        else "Unknown"
                    )
                    or "Unknown",
                    "previous_company": company,
                    "title": (
                        (item.get("past_employers") or [{}])[0].get("title")
                        if isinstance(item.get("past_employers"), list)
                        else item.get("headline")
                    )
                    or item.get("headline")
                    or "Unknown",
                }
                for item in people_records[:5]
            ],
            "company_metrics": {
                "headcount": headcount_block.get("linkedin_headcount") or 0,
                "headcount_growth_pct": headcount_block.get("linkedin_headcount_total_growth_percent", {}).get("qoq")
                or 0,
                "job_openings": job_block.get("job_openings_count") or 0,
                "web_traffic_index": web_traffic_block.get("monthly_visitors") or 0,
                "glassdoor_rating": glassdoor_rating,
            },
            "hiring_signals": hiring_signals,
            "sentiment_trend": sentiment_points,
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
                    "name": item.get("name") or "Unknown",
                    "movement": item.get("headline") or "Executive signal identified",
                    "date": item.get("updated_at") or item.get("created_at") or "Unknown",
                }
                for item in people_records[:5]
                if isinstance(item.get("headline"), str)
                and any(
                    keyword in item.get("headline", "").lower()
                    for keyword in ["chief", "ceo", "cto", "vp", "head", "director"]
                )
            ],
        }

        has_live_data = any(
            [
                normalized["social_activity"],
                normalized["hiring_signals"],
                normalized["news_coverage"],
                normalized["people_intelligence"],
                any(value for value in normalized["company_metrics"].values()),
            ]
        )

        normalized["source"] = "crustdata-live" if has_live_data else "crustdata-empty"
        normalized["has_live_data"] = has_live_data
        return normalized