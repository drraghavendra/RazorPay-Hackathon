# ShadowIntel PRD (Living Document)

## Original Problem Statement
Build a hackathon-ready MVP called **ShadowIntel**: an AI-native competitive intelligence platform for product managers.

Core ask:
- User enters two competitors (default demo: Stripe and Adyen)
- System gathers daily competitor signals (social, hiring, company metrics, sentiment, news, product changes, executive movements)
- Crustdata APIs should be the primary intelligence source
- AI layer generates strategic briefings and answers chat questions
- Modern SaaS dashboard UX with Home, Comparison, and AI Chat pages

User-confirmed choices:
- Use provided workspace stack: **React + FastAPI + MongoDB**
- Use **Emergent universal LLM key**
- Crustdata key deferred (placeholder for now)
- Slack integration skipped in v1 pass
- Prefill competitors: Stripe vs Adyen

## Architecture Decisions
- **Frontend:** React Router app with Tailwind + Shadcn UI + Recharts + Framer Motion
- **Backend:** FastAPI with modular services:
  - `crustdata_api_service.py`
  - `ai_intelligence_generator.py`
  - `intelligence_orchestrator.py`
  - `demo_data.py`
- **DB:** MongoDB collections:
  - `intelligence_reports`
  - `chat_messages`
- **AI Integration:** Emergent-compatible `emergentintegrations.llm.openai.LlmChat` (model `gpt-5.2`)
- **Fallback behavior:** if Crustdata key is placeholder/missing or returns no records, system provides deterministic fallback signals for demo continuity.

## User Personas
- **PM Lead (primary):** needs fast daily competitor briefing before planning meetings
- **Strategy Analyst:** compares expansion signals and market movement across competitors
- **Product Ops:** asks AI chat for “likely next product moves” and risk/opportunity snapshots

## Core Requirements (Static)
1. Two-competitor input and daily briefing generation
2. Dashboard sections for social, hiring, metrics, sentiment, news, AI insight
3. Side-by-side competitor comparison view
4. AI chat with report-aware answers
5. Crustdata-first integration architecture
6. Clean responsive SaaS UI suitable for hackathon demo

## What’s Implemented

### 2026-03-14
- Implemented FastAPI intelligence endpoints:
  - `GET /api/health`
  - `POST /api/intelligence/briefing`
  - `GET /api/intelligence/latest`
  - `GET /api/intelligence/comparison`
  - `POST /api/intelligence/chat`
  - `GET /api/intelligence/briefings`
  - `GET /api/intelligence/chat/history`
  - `GET /api/intelligence/source-status`
- Added orchestration layer for competitor signal collection and AI briefing generation
- Added Crustdata integration service across required API categories
- Added AI generation service for:
  - daily brief
  - risk alerts
  - opportunity signals
  - roadmap inference
  - conversational intelligence answers
- Built React frontend pages:
  - Dashboard
  - Comparison
  - AI Chat
- Added modern “Shadow Mode” UI implementation with bento-like data surface and charts
- Added persistent local state for selected competitors and latest report
- Added README with setup and endpoint documentation
- Added backend regression tests (`/app/backend/tests/test_intelligence_endpoints.py`)

## Prioritized Backlog

### P0 (Must do next)
- Replace placeholder `CRUSTDATA_API_KEY` with live key and validate all Crustdata endpoint mappings/field contracts
- Add explicit UI badge indicating live-source vs fallback-source mode
- Harden Crustdata endpoint-specific parameter mappings per production API contract

### P1 (Should do)
- Add background scheduler for automated morning briefing generation
- Add saved competitor watchlists and user-specific report history
- Add richer trend visualizations (weekly/monthly deltas, anomaly markers)

### P2 (Nice to have)
- Slack webhook delivery with formatted digest blocks
- Alert threshold configuration (e.g., sentiment drop >0.4)
- Export reports to PDF/email and share links for team collaboration

## Next Tasks List
1. Insert real `CRUSTDATA_API_KEY` and run live-data regression
2. Add source-mode UI indicator (Live vs Fallback)
3. Add scheduled daily report generation job
4. Implement Slack delivery for daily briefings
5. Expand AI chat with citations back to signal categories
