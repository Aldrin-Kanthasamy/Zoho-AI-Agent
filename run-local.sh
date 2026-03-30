#!/usr/bin/env bash
set -euo pipefail

echo "Starting helper: create DB, install deps, and optionally run backend/frontend"

if command -v pg_ctl >/dev/null 2>&1; then
  echo "pg_ctl found; attempting to start Postgres if PGDATA is set or default locations exist"
  if [ -z "${PGDATA:-}" ]; then
    if [ -d "/usr/local/var/postgres" ]; then
      export PGDATA="/usr/local/var/postgres"
    fi
  fi
  if [ -n "${PGDATA:-}" ]; then
    pg_ctl -D "$PGDATA" start || true
  fi
fi

echo "Creating database ai_agent_db if possible..."
if command -v createdb >/dev/null 2>&1; then
  createdb -h localhost -U postgres ai_agent_db || true
else
  echo "createdb not found; please create database manually if needed"
fi

echo "Installing backend dependencies..."
python -m pip install -r backend/requirements.txt

MODE=${1:-}
if [ "$MODE" = "backend" ] || [ "$MODE" = "all" ]; then
  echo "Starting uvicorn backend..."
  uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000 &
fi

if [ "$MODE" = "frontend" ] || [ "$MODE" = "all" ]; then
  echo "Starting static frontend server on port 8080..."
  (cd frontend && python -m http.server 8080) &
fi

echo "Done. Use 'bash run-local.sh all' to run both backend and frontend." 
