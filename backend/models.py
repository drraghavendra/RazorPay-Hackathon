from typing import Any, Dict, List

from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str
    content: str


class CompetitorPairRequest(BaseModel):
    competitor_a: str = Field(min_length=1)
    competitor_b: str = Field(min_length=1)


class AIChatRequest(BaseModel):
    competitor_a: str = Field(min_length=1)
    competitor_b: str = Field(min_length=1)
    question: str = Field(min_length=2)
    history: List[ChatMessage] = Field(default_factory=list)


class CompetitorIntelligence(BaseModel):
    company_name: str
    social_activity: List[Dict[str, Any]]
    keyword_trends: List[Dict[str, Any]]
    people_intelligence: List[Dict[str, Any]]
    company_metrics: Dict[str, Any]
    hiring_signals: List[Dict[str, Any]]
    sentiment_trend: List[Dict[str, Any]]
    news_coverage: List[Dict[str, Any]]
    product_changes: List[Dict[str, Any]]
    executive_movements: List[Dict[str, Any]]
    strategic_summary: str


class AIInsights(BaseModel):
    daily_brief: str
    risk_alerts: List[str]
    opportunity_signals: List[str]
    roadmap_inference: str


class DailyBriefingResponse(BaseModel):
    report_id: str
    generated_at: str
    competitor_a: CompetitorIntelligence
    competitor_b: CompetitorIntelligence
    comparison: Dict[str, Any]
    ai_insights: AIInsights
    source_status: Dict[str, str]


class ComparisonResponse(BaseModel):
    generated_at: str
    competitor_a: str
    competitor_b: str
    metrics: Dict[str, Any]
    source_status: Dict[str, str]


class AIChatResponse(BaseModel):
    answer: str
    competitor_a: str
    competitor_b: str
    timestamp: str