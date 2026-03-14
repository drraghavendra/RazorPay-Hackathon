from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any, Dict, List
import uuid

from emergentintegrations.llm.openai import LlmChat, UserMessage


logger = logging.getLogger(__name__)


class AIIntelligenceGenerator:
    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        self.model = os.environ.get("OPENAI_MODEL", "gpt-5.2")
        self.provider = "openai"
        self.request_timeout_seconds = float(os.environ.get("OPENAI_REQUEST_TIMEOUT_SECONDS", "12"))
        self.daily_briefing_ai_enabled = (
            os.environ.get("OPENAI_DAILY_BRIEFING_ENABLED", "true").lower() == "true"
        )

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def _chat_json(self, system_prompt: str, user_prompt: str) -> Dict[str, Any] | None:
        if not self.api_key:
            return None
        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id=str(uuid.uuid4()),
                system_message=system_prompt,
            ).with_model(self.provider, self.model)
            content = await asyncio.wait_for(
                chat.send_message(UserMessage(text=user_prompt)),
                timeout=self.request_timeout_seconds,
            )
            content = content or "{}"
            content = content.strip().removeprefix("```json").removesuffix("```").strip()
            return json.loads(content)
        except Exception as exc:  # noqa: BLE001
            logger.warning("OpenAI JSON generation failed: %s", exc)
            return None

    async def _chat_text(self, system_prompt: str, user_prompt: str) -> str | None:
        if not self.api_key:
            return None
        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id=str(uuid.uuid4()),
                system_message=system_prompt,
            ).with_model(self.provider, self.model)
            response = await asyncio.wait_for(
                chat.send_message(UserMessage(text=user_prompt)),
                timeout=self.request_timeout_seconds,
            )
            return (response or "").strip()
        except Exception as exc:  # noqa: BLE001
            logger.warning("OpenAI text generation failed: %s", exc)
            return None

    async def generate_company_summary(self, company_data: Dict[str, Any]) -> str:
        metrics = company_data.get("company_metrics", {})
        hiring = company_data.get("hiring_signals", [])
        headcount_growth = metrics.get("headcount_growth_pct", 0)
        hiring_focus = ", ".join([item.get("job_title", "") for item in hiring[:2]])

        default_summary = (
            f"{company_data['company_name']} shows {headcount_growth}% headcount momentum. "
            f"Recent hiring focus includes {hiring_focus or 'platform and AI roles'}, "
            "indicating product and infrastructure investment."
        )

        prompt = f"""
        You are a competitive intelligence analyst. Summarize this competitor in 2 concise sentences.

        Company: {company_data['company_name']}
        Metrics: {json.dumps(metrics)}
        Hiring signals: {json.dumps(hiring[:3])}
        Social activity: {json.dumps(company_data.get('social_activity', [])[:2])}
        News: {json.dumps(company_data.get('news_coverage', [])[:2])}
        """

        generated = await self._chat_text(
            "You write strategic PM-focused summaries. Keep it clear and non-generic.",
            prompt,
        )
        return generated or default_summary

    async def generate_daily_insights(
        self,
        competitor_a: Dict[str, Any],
        competitor_b: Dict[str, Any],
    ) -> Dict[str, Any]:
        unavailable = self._unavailable_daily_insights()
        if not self.daily_briefing_ai_enabled or not self.is_configured:
            return unavailable

        prompt = f"""
        Generate strategic intelligence JSON with keys:
        daily_brief (string),
        risk_alerts (array of 3 strings),
        opportunity_signals (array of 3 strings),
        roadmap_inference (string).

        Focus on product managers and competitor strategy.
        Competitor A: {json.dumps(competitor_a)}
        Competitor B: {json.dumps(competitor_b)}
        """
        generated = await self._chat_json(
            "You are ShadowIntel AI strategist. Return strictly valid JSON.",
            prompt,
        )
        if not generated:
            return unavailable

        return {
            "daily_brief": str(generated.get("daily_brief") or "No live AI briefing returned."),
            "risk_alerts": [
                item
                for item in (generated.get("risk_alerts") if isinstance(generated.get("risk_alerts"), list) else [])
                if isinstance(item, str)
            ],
            "opportunity_signals": [
                item
                for item in (
                    generated.get("opportunity_signals")
                    if isinstance(generated.get("opportunity_signals"), list)
                    else []
                )
                if isinstance(item, str)
            ],
            "roadmap_inference": str(generated.get("roadmap_inference") or "No roadmap inference returned."),
        }

    async def answer_competitive_question(
        self,
        question: str,
        context_report: Dict[str, Any],
        history: List[Dict[str, str]],
    ) -> str:
        prompt = f"""
        Answer as ShadowIntel AI assistant for product managers.
        Question: {question}
        Recent conversation: {json.dumps(history[-6:])}
        Context report: {json.dumps(context_report)}

        Constraints:
        - 4 short bullet points max
        - highlight evidence from social/hiring/sentiment/news when possible
        """

        generated = await self._chat_text(
            "You are a strategic product intelligence analyst.",
            prompt,
        )
        return generated or "Live AI chat response unavailable right now."

    def _unavailable_daily_insights(self) -> Dict[str, Any]:
        return {
            "daily_brief": "Live AI briefing unavailable.",
            "risk_alerts": [],
            "opportunity_signals": [],
            "roadmap_inference": "Live AI roadmap inference unavailable.",
        }