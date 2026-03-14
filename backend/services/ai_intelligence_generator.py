from __future__ import annotations

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
            content = await chat.send_message(UserMessage(text=user_prompt))
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
            response = await chat.send_message(UserMessage(text=user_prompt))
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
        default = self._fallback_daily_insights(competitor_a, competitor_b)

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
            return default

        return {
            "daily_brief": generated.get("daily_brief", default["daily_brief"]),
            "risk_alerts": generated.get("risk_alerts", default["risk_alerts"]),
            "opportunity_signals": generated.get(
                "opportunity_signals",
                default["opportunity_signals"],
            ),
            "roadmap_inference": generated.get(
                "roadmap_inference",
                default["roadmap_inference"],
            ),
        }

    async def answer_competitive_question(
        self,
        question: str,
        context_report: Dict[str, Any],
        history: List[Dict[str, str]],
    ) -> str:
        fallback = (
            "Signal check complete: both competitors show activity across hiring, social engagement, "
            "and market visibility. Ask about hiring, sentiment, or roadmap inference for a focused answer."
        )

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
        return generated or fallback

    def _fallback_daily_insights(
        self,
        competitor_a: Dict[str, Any],
        competitor_b: Dict[str, Any],
    ) -> Dict[str, Any]:
        a_metrics = competitor_a.get("company_metrics", {})
        b_metrics = competitor_b.get("company_metrics", {})

        daily_brief = (
            f"{competitor_a['company_name']} and {competitor_b['company_name']} both show sustained signal activity. "
            "Hiring and social engagement indicate continued investment in AI-enabled product capabilities."
        )
        risk_alerts = [
            (
                f"{competitor_a['company_name']} headcount growth at "
                f"{a_metrics.get('headcount_growth_pct', 0)}% can shorten enterprise sales cycles."
            ),
            (
                f"{competitor_b['company_name']} social engagement around AI themes suggests messaging momentum."
            ),
            "Executive movement signals indicate potential acceleration in roadmap execution.",
        ]
        opportunity_signals = [
            "Declining employee sentiment can open recruiting and partnership opportunities.",
            "Shared audience engagement creates room for targeted differentiation campaigns.",
            "Feature-change monitoring reveals openings for faster release velocity.",
        ]
        roadmap_inference = (
            "Both competitors are likely expanding AI-assisted risk workflows and enterprise controls. "
            "Prioritize roadmap bets on explainability, reliability, and integrations."
        )

        b_growth = b_metrics.get("headcount_growth_pct", 0)
        if b_growth > a_metrics.get("headcount_growth_pct", 0):
            daily_brief = (
                f"{competitor_b['company_name']} appears to be accelerating faster than "
                f"{competitor_a['company_name']} based on talent and coverage signals."
            )

        return {
            "daily_brief": daily_brief,
            "risk_alerts": risk_alerts,
            "opportunity_signals": opportunity_signals,
            "roadmap_inference": roadmap_inference,
        }