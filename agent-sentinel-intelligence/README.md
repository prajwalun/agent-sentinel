# Agent Sentinel Intelligence

FastAPI backend that receives security events from the SDK, stores them in SQLite, and runs AI-powered analysis using a LangGraph multi-agent workflow (Analyzer, Supervisor, Researcher, Reporter, Validator).

## Quick start

```bash
pip install -r requirements.txt
python -m uvicorn api_server:app --host 0.0.0.0 --port 8001
```

Check health: `curl http://localhost:8001/health`

## Environment variables

| Variable | Required | What it does |
|----------|----------|--------------|
| `OPENAI_API_KEY` | For AI analysis | Powers the LangGraph workflow |
| `JWT_SECRET` | No | Signs JWT tokens (auto-generated if missing) |
| `ADMIN_SECRET` | No | Admin-level API key generation |
| `EXA_API_KEY` | No | External threat intelligence via Exa.ai |

Copy `../.env.example` to `../.env` and fill in what you need.

## Tests

```bash
pip install pytest
python -m pytest tests/ -v
```

## Docs

- [Main README](../README.md) — project overview, getting started
- [System Design](../SYSTEM_DESIGN.md) — API reference, database schema, workflow details
