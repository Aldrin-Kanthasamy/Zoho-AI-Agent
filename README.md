# Zoho AI Agent (Sprint + Desk)

Backend: Python FastAPI
Frontend: AngularJS
Database: PostgreSQL
LLM: Anthropic (Claude) via API
Agent orchestration: Autogen (architecture-ready - manual integration as needed)

## Setup (Local, no Docker)

1. Start PostgreSQL service and create DB:
   - Windows: `net start postgresql-x64-14` (version-specific)
   - `createdb -h localhost -p 5432 -U postgres ai_agent_db`

2. Configure `.env`:
   - `DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_agent_db`
   - `ANTHROPIC_API_KEY=your_anthropic_api_key_here`
   - `ANTHROPIC_MODEL=claude-2.1`

3. Install backend dependencies:
   - `cd backend`
   - `pip install -r requirements.txt`

4. Run backend:
   - `uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000`

5. Serve frontend:
   - open `frontend/index.html` in browser
   - or run `python -m http.server 8080` from `frontend` and open `http://localhost:8080`

## Features

- Webhooks:
  - `/webhook/zohosprint`
  - `/webhook/zohodesk`
- Assignment logic by `skill_needed`, availability, workload
- Superadmin read dashboard: `/superadmin/dashboard`
- Natural language admin commands: `/admin/query`
- Daily standup consolidations (cron at 09:00, logs summary)

## Next steps

- Implement Autogen orchestration service and workflows
- Integrate with Zoho Sprint and Zoho Desk OAuth/webhook URL configuration
- Add access control and auth
- Add frontend login and per-user dashboards
