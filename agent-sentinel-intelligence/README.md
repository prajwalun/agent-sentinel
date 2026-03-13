# Agent Sentinel Intelligence

FastAPI backend: receives events from the SDK, stores in SQLite, runs AI analysis via LangGraph (Analyzer, Supervisor, Researcher, Reporter, Validator).

## Quick start

```bash
pip install -r requirements.txt
python -m uvicorn api_server:app --host 0.0.0.0 --port 8001
```

Check: `curl http://localhost:8001/health`

## Environment variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `OPENAI_API_KEY` | For AI analysis | Powers LangGraph workflow |
| `JWT_SECRET` | No | Signs JWT tokens (auto-generated if missing) |
| `JWT_EXPIRY_HOURS` | No | Session duration in hours (default 24). Dashboard logs out on 401 when expired. |
| `ADMIN_SECRET` | No | Admin-level API key generation |
| `EXA_API_KEY` | No | External threat intelligence (Exa.ai) |

Create `.env` at project root: `cp .env.example .env`

## Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

## Docs

- [Main README](../README.md) — project overview, getting started
- [System Design](../SYSTEM_DESIGN.md) — API reference, database schema, workflow details
