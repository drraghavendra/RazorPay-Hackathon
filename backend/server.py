from datetime import datetime, timezone
from pathlib import Path
from typing import List
import logging
import os

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI, Query
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.middleware.cors import CORSMiddleware

from models import (
    AIChatRequest,
    AIChatResponse,
    ComparisonResponse,
    CompetitorPairRequest,
    DailyBriefingResponse,
)
from services.intelligence_orchestrator import IntelligenceOrchestrator

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

mongo_url = os.environ["MONGO_URL"]
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ["DB_NAME"]]

app = FastAPI(title="ShadowIntel API", version="1.0.0")
api_router = APIRouter(prefix="/api")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

orchestrator = IntelligenceOrchestrator()


@api_router.get("/")
async def root():
    return {
        "message": "ShadowIntel API is running",
        "product": "AI-native competitive intelligence for product teams",
    }


@api_router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "shadowintel-backend",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@api_router.post("/intelligence/briefing", response_model=DailyBriefingResponse)
async def generate_daily_briefing(payload: CompetitorPairRequest):
    report = await orchestrator.build_daily_briefing(
        payload.competitor_a,
        payload.competitor_b,
    )
    stored_report = report.copy()
    await db.intelligence_reports.insert_one(stored_report)
    return report


@api_router.get("/intelligence/briefings", response_model=List[DailyBriefingResponse])
async def get_briefing_history(limit: int = Query(default=10, ge=1, le=30)):
    history = await (
        db.intelligence_reports.find({}, {"_id": 0})
        .sort("generated_at", -1)
        .limit(limit)
        .to_list(limit)
    )
    return history


@api_router.get("/intelligence/latest", response_model=DailyBriefingResponse)
async def get_or_generate_latest(
    competitor_a: str = Query(...),
    competitor_b: str = Query(...),
):
    existing = await db.intelligence_reports.find_one(
        {
            "competitor_a.company_name": competitor_a.strip(),
            "competitor_b.company_name": competitor_b.strip(),
        },
        {"_id": 0},
        sort=[("generated_at", -1)],
    )
    if existing:
        return existing

    report = await orchestrator.build_daily_briefing(competitor_a, competitor_b)
    stored_report = report.copy()
    await db.intelligence_reports.insert_one(stored_report)
    return report


@api_router.get("/intelligence/comparison", response_model=ComparisonResponse)
async def get_comparison(
    competitor_a: str = Query(...),
    competitor_b: str = Query(...),
):
    latest = await db.intelligence_reports.find_one(
        {
            "competitor_a.company_name": competitor_a.strip(),
            "competitor_b.company_name": competitor_b.strip(),
        },
        {"_id": 0},
        sort=[("generated_at", -1)],
    )

    if not latest:
        latest = await orchestrator.build_daily_briefing(competitor_a, competitor_b)
        stored_report = latest.copy()
        await db.intelligence_reports.insert_one(stored_report)

    return {
        "generated_at": latest["generated_at"],
        "competitor_a": latest["competitor_a"]["company_name"],
        "competitor_b": latest["competitor_b"]["company_name"],
        "metrics": latest["comparison"],
        "source_status": latest["source_status"],
    }


@api_router.post("/intelligence/chat", response_model=AIChatResponse)
async def intelligence_chat(payload: AIChatRequest):
    context_report = await db.intelligence_reports.find_one(
        {
            "competitor_a.company_name": payload.competitor_a.strip(),
            "competitor_b.company_name": payload.competitor_b.strip(),
        },
        {"_id": 0},
        sort=[("generated_at", -1)],
    )
    if not context_report:
        context_report = await orchestrator.build_daily_briefing(
            payload.competitor_a,
            payload.competitor_b,
        )
        stored_report = context_report.copy()
        await db.intelligence_reports.insert_one(stored_report)

    answer = await orchestrator.answer_question(
        question=payload.question,
        context_report=context_report,
        history=[msg.model_dump() for msg in payload.history],
    )

    response = {
        "answer": answer,
        "competitor_a": payload.competitor_a,
        "competitor_b": payload.competitor_b,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    stored_message = {
        "question": payload.question,
        **response,
    }
    await db.chat_messages.insert_one(stored_message)
    return response


@api_router.get("/intelligence/chat/history")
async def get_chat_history(limit: int = Query(default=20, ge=1, le=100)):
    history = await (
        db.chat_messages.find({}, {"_id": 0})
        .sort("timestamp", -1)
        .limit(limit)
        .to_list(limit)
    )
    return history


@api_router.get("/intelligence/source-status")
async def source_status():
    return {
        "crustdata_configured": orchestrator.crustdata_service.is_configured,
        "openai_configured": orchestrator.ai_service.is_configured,
        "note": "Set CRUSTDATA_API_KEY in backend/.env for live competitive intelligence.",
    }


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ["CORS_ORIGINS"].split(","),
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()