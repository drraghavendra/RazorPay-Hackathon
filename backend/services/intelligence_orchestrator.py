from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any, Dict, List
import uuid

from services.ai_intelligence_generator import AIIntelligenceGenerator
from services.crustdata_api_service import CrustdataAPIService


class IntelligenceOrchestrator:
    def __init__(self):
        self.crustdata_service = CrustdataAPIService()
        self.ai_service = AIIntelligenceGenerator()

    async def _resolve_company_data(self, company: str, rival: str) -> Dict[str, Any]:
        if not self.crustdata_service.is_configured:
            return self._empty_company_payload(company)

        live_data = await self.crustdata_service.fetch_company_intelligence(company, rival)
        if live_data.get("has_live_data"):
            return live_data
        return self._empty_company_payload(company)

    async def build_daily_briefing(self, competitor_a: str, competitor_b: str) -> Dict[str, Any]:
        normalized_a = competitor_a.strip()
        normalized_b = competitor_b.strip()

        company_a_data, company_b_data = await asyncio.gather(
            self._resolve_company_data(normalized_a, normalized_b),
            self._resolve_company_data(normalized_b, normalized_a),
        )

        company_a_data["strategic_summary"] = self._build_company_summary(company_a_data)
        company_b_data["strategic_summary"] = self._build_company_summary(company_b_data)

        ai_insights = await self.ai_service.generate_daily_insights(
            company_a_data,
            company_b_data,
        )

        return {
            "report_id": str(uuid.uuid4()),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "competitor_a": company_a_data,
            "competitor_b": company_b_data,
            "comparison": self._build_comparison(company_a_data, company_b_data),
            "ai_insights": ai_insights,
            "source_status": {
                "competitor_a": company_a_data.get("source", "unknown"),
                "competitor_b": company_b_data.get("source", "unknown"),
                "ai": (
                    "openai-live"
                    if self.ai_service.is_configured and self.ai_service.daily_briefing_ai_enabled
                    else "openai-unavailable"
                ),
            },
        }

    async def answer_question(
        self,
        question: str,
        context_report: Dict[str, Any],
        history: List[Dict[str, str]],
    ) -> str:
        return await self.ai_service.answer_competitive_question(
            question=question,
            context_report=context_report,
            history=history,
        )

    @staticmethod
    def _build_comparison(
        company_a_data: Dict[str, Any],
        company_b_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        a_metrics = company_a_data.get("company_metrics", {})
        b_metrics = company_b_data.get("company_metrics", {})

        return {
            "headcount": {
                "a": a_metrics.get("headcount", 0),
                "b": b_metrics.get("headcount", 0),
                "delta": a_metrics.get("headcount", 0) - b_metrics.get("headcount", 0),
            },
            "hiring_openings": {
                "a": a_metrics.get("job_openings", 0),
                "b": b_metrics.get("job_openings", 0),
                "delta": a_metrics.get("job_openings", 0) - b_metrics.get("job_openings", 0),
            },
            "sentiment": {
                "a": a_metrics.get("glassdoor_rating", 0),
                "b": b_metrics.get("glassdoor_rating", 0),
                "delta": round(
                    a_metrics.get("glassdoor_rating", 0)
                    - b_metrics.get("glassdoor_rating", 0),
                    2,
                ),
            },
            "social_engagement": {
                "a": sum(item.get("reactor_count", 0) for item in company_a_data.get("social_activity", [])),
                "b": sum(item.get("reactor_count", 0) for item in company_b_data.get("social_activity", [])),
            },
            "headcount_growth": {
                "a": a_metrics.get("headcount_growth_pct", 0),
                "b": b_metrics.get("headcount_growth_pct", 0),
            },
        }

    @staticmethod
    def _build_company_summary(company_data: Dict[str, Any]) -> str:
        metrics = company_data.get("company_metrics", {})
        top_jobs = [job.get("job_title", "") for job in company_data.get("hiring_signals", [])[:2] if job.get("job_title")]
        top_job_text = ", ".join(top_jobs) if top_jobs else "platform and product roles"

        return (
            f"{company_data.get('company_name', 'Competitor')} has headcount {metrics.get('headcount', 0)} "
            f"with {metrics.get('headcount_growth_pct', 0)}% growth and {metrics.get('job_openings', 0)} open roles. "
            f"Recent hiring focus includes {top_job_text}."
        )

    @staticmethod
    def _empty_company_payload(company: str) -> Dict[str, Any]:
        return {
            "company_name": company,
            "social_activity": [],
            "keyword_trends": [],
            "people_intelligence": [],
            "company_metrics": {
                "headcount": 0,
                "headcount_growth_pct": 0,
                "job_openings": 0,
                "web_traffic_index": 0,
                "glassdoor_rating": 0,
            },
            "hiring_signals": [],
            "sentiment_trend": [],
            "news_coverage": [],
            "product_changes": [],
            "executive_movements": [],
            "strategic_summary": "No live records returned for this company.",
            "source": "crustdata-empty",
            "has_live_data": False,
        }