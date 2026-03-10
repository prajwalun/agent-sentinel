# Agent Sentinel

**Security monitoring for AI agents — add one decorator, detect threats in real time.**

Agent Sentinel instruments any Python AI agent with a single decorator. It detects prompt injection, SQL injection, XSS, command injection, data exfiltration, and more — then surfaces findings through a live dashboard backed by AI-powered analysis.

## Quick Start

```bash
pip install agent-sentinel
```

```python
from agent_sentinel import monitor, AgentSentinel

@monitor
def my_agent(query: str) -> str:
    return llm.invoke(query)

# Run your agent as usual — threats are detected automatically
my_agent("What is the weather today?")

# Generate a report
sentinel = AgentSentinel()
sentinel.generate_unified_report()
```

Three decorators cover every agent pattern:

```python
@monitor                       # functions and methods
@sentinel                      # entire classes (wraps all public methods)
@monitor_mcp                   # MCP tool functions
```

No changes to agent code. No subclassing. No configuration required.

## Project Structure

```
agent-sentinel-sdk/            Python SDK — decorators, threat detection, event registry
agent-sentinel-intelligence/   FastAPI backend — auth, storage, LangGraph AI analysis
agent-sentinel-dashboard/      Next.js frontend — real-time dashboard, reports, settings
tests/                         E2E test suites with real agent integrations
```

## Architecture

The SDK detects threats locally and optionally streams events to the Intelligence API, which stores them in SQLite, runs multi-agent AI analysis (LangGraph), and serves the Dashboard via REST and SSE.

See [SYSTEM_DESIGN.md](./SYSTEM_DESIGN.md) for the full architecture, data flows, API reference, and database schema.

## Running the Full Stack

### 1. Backend

```bash
cd agent-sentinel-intelligence
pip install -r requirements.txt
cp ../.env.example .env        # add your OPENAI_API_KEY
uvicorn api_server:app --host 0.0.0.0 --port 8001
```

### 2. Dashboard

```bash
cd agent-sentinel-dashboard
npm install
echo 'NEXT_PUBLIC_API_URL=http://localhost:8001' > .env.local
npm run dev
```

### 3. SDK (connect to backend)

```python
from agent_sentinel import monitor

# Events are automatically sent when SENTINEL_API_URL and SENTINEL_API_KEY are set
# export SENTINEL_API_URL=http://localhost:8001
# export SENTINEL_API_KEY=<your key from the dashboard settings page>

@monitor
def my_agent(query):
    return process(query)
```

## Threat Detection

The SDK detects these threat categories in real time:

| Threat | Examples |
|--------|----------|
| SQL injection | `'; DROP TABLE users; --`, `OR 1=1` |
| XSS | `<script>alert('xss')</script>`, `onerror=` |
| Prompt injection | `ignore previous instructions`, `system prompt` |
| Command injection | `; rm -rf /`, `\| curl evil.com` |
| Path traversal | `../../etc/passwd` |
| Data exfiltration | Credential patterns, suspicious external URLs |

Each event includes `threat_type`, `severity` (LOW–CRITICAL), `confidence` (0.0–1.0), and the triggering context.

## Testing

```bash
# Backend API tests (39 tests)
cd agent-sentinel-intelligence && python -m pytest tests/ -v

# SDK unit tests (52 tests)
cd agent-sentinel-sdk && python -m pytest tests/ -v

# E2E with synthetic agents (6 scenarios)
python tests/test_agents_e2e.py

# E2E with real agents from extra/ (8 scenarios — A2A protocol, Agno + OpenAI)
python tests/test_real_agents_e2e.py
```

## Environment Variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `OPENAI_API_KEY` | For AI analysis | LangGraph workflow (GPT-4o) |
| `EXA_API_KEY` | Optional | External threat intelligence research |
| `SENTINEL_API_URL` | Optional | Backend URL for SDK event streaming |
| `SENTINEL_API_KEY` | Optional | API key for SDK authentication |
| `JWT_SECRET` | Backend | JWT signing secret (auto-generated if unset) |
| `ADMIN_SECRET` | Backend | Admin API key generation |

## License

MIT — see [LICENSE](./LICENSE).
