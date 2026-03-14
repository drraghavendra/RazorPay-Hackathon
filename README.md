# ShadowIntel MVP

AI-native competitive intelligence platform for product managers.

## What this MVP includes

- Competitor intelligence dashboard for two companies (default: Stripe vs Adyen)
- Crustdata-powered backend service layer (with live API support via env key)
- AI-generated daily briefing, risk alerts, opportunities, and roadmap inference
- Side-by-side competitor comparison page
- AI intelligence chat for PM-style strategic Q&A

## Tech Stack in this workspace

- Frontend: React + TailwindCSS + Recharts + Shadcn UI
- Backend: FastAPI
- Database: MongoDB
- AI: OpenAI (configured with Emergent universal key)

## Environment Variables

Backend file: `/app/backend/.env`

- `MONGO_URL` (already configured)
- `DB_NAME` (already configured)
- `CORS_ORIGINS` (already configured)
- `OPENAI_API_KEY` (already configured)
- `OPENAI_MODEL` (default: gpt-5.2)
- `CRUSTDATA_API_KEY` (**add your real key for live Crustdata data**)
- `CRUSTDATA_BASE_URL` (default: https://api.crustdata.com)

Frontend file: `/app/frontend/.env`

- `REACT_APP_BACKEND_URL` (already configured, do not change)

## Run locally

### Backend

```bash
cd /app/backend
pip install -r requirements.txt
sudo supervisorctl restart backend
```

### Frontend

```bash
cd /app/frontend
yarn install
sudo supervisorctl restart frontend
```

## Main API endpoints

- `POST /api/intelligence/briefing` → generate latest daily briefing
- `GET /api/intelligence/latest` → latest report for selected pair
- `GET /api/intelligence/comparison` → side-by-side metrics
- `POST /api/intelligence/chat` → AI chat with competitive context
- `GET /api/intelligence/briefings` → report history

## Notes

- Add real `CRUSTDATA_API_KEY` to switch from fallback sample signals to live Crustdata signals.
- All frontend API calls use `REACT_APP_BACKEND_URL`.
