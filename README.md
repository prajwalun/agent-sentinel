# Agent Sentinel

Security monitoring for AI agents. Add a decorator, get threat detection.

```bash
pip install agent-sentinel
```

```python
from agent_sentinel import monitor

@monitor
def my_agent(query: str) -> str:
    return llm.invoke(query)
```

That's it. Every call to `my_agent` is now validated against 60+ compiled regex patterns for SQL injection, XSS, prompt injection, command injection, path traversal, and data exfiltration. Threats produce a `SecurityEvent` with type, severity, and confidence score. No changes to your agent code.

Works with single functions (`@monitor`), entire classes (`@sentinel`), and MCP tool servers (`@monitor_mcp`). All events flow into a thread-safe global registry for unified reporting across multi-agent pipelines.

---

## Getting Started

You need **Python 3.9+**, **Node.js 18+**, and an **OpenAI API key** (for AI analysis).

### Docker (fastest)

```bash
git clone https://github.com/prajwalun/agent-sentinel.git
cd agent-sentinel
cp .env.example .env   # add your OPENAI_API_KEY
docker-compose up --build
```

Backend runs at `http://localhost:8001`, dashboard at `http://localhost:3000`.

### Manual setup

**Backend:**

```bash
cd agent-sentinel-intelligence
pip install -r requirements.txt
cp ../.env.example ../.env   # add your OPENAI_API_KEY, JWT_SECRET, ADMIN_SECRET
python -m uvicorn api_server:app --host 0.0.0.0 --port 8001
```

**Dashboard:**

```bash
cd agent-sentinel-dashboard
npm install
echo 'NEXT_PUBLIC_API_URL=http://localhost:8001' > .env.local
npm run dev
```

Open `http://localhost:3000`, create an account, grab an API key from Settings.

**Connect the SDK:**

```bash
export SENTINEL_API_URL=http://localhost:8001
export SENTINEL_API_KEY=<key from dashboard>
```

Now any `@monitor`-decorated function streams events to the backend in real time. Open the dashboard to watch them come in.

The SDK also works standalone — no backend needed for local threat detection and report generation.

---

## What it does

Three decorators cover every agent pattern:

```python
from agent_sentinel import monitor, sentinel, monitor_mcp

@monitor                          # single function
def research(query): ...

@sentinel                         # entire class — wraps all public methods
class Pipeline:
    def plan(self, task): ...
    def execute(self, plan): ...

@monitor_mcp(agent_id="tools")   # MCP tool server
def search(query): ...
```

On every call, the SDK:
1. Validates inputs against compiled regex patterns (SQL injection, XSS, prompt injection, command injection, path traversal, data exfiltration)
2. Executes the function normally
3. Optionally validates outputs (`validate_outputs=True`)
4. Records a `SecurityEvent` if a threat is found (type, severity, confidence, context)
5. Pushes the event to the backend via `BackendEventSink` (if connected)

The backend stores events in SQLite, streams them to the dashboard via SSE, and runs AI-powered analysis using a LangGraph workflow with 5 agents (Analyzer, Supervisor, Researcher, Reporter, Validator) that can iteratively refine reports up to 3 times.

---

## Project layout

```
agent-sentinel-sdk/            Python SDK — decorators, validators, event registry
agent-sentinel-intelligence/   FastAPI backend — auth, database, LangGraph analysis
agent-sentinel-dashboard/      Next.js dashboard — real-time events, reports, settings
tests/                         E2E tests with synthetic and real agents
```

For architecture details, data flows, API reference, and database schema, see [SYSTEM_DESIGN.md](./SYSTEM_DESIGN.md).

---

## Tests

97+ tests across four suites:

```bash
cd agent-sentinel-sdk && python -m pytest tests/ -v            # 52 SDK tests
cd agent-sentinel-intelligence && python -m pytest tests/ -v   # 39 API tests
python tests/test_agents_e2e.py                                # 6 synthetic E2E
python tests/test_real_agents_e2e.py                           # 8 real agent E2E
```

The E2E tests run safe and malicious agents (single, multi-agent, MCP) and verify that threats are detected while clean agents produce zero false positives. Real agent tests use the A2A protocol and Agno/OpenAI frameworks.

CI runs three jobs on every push via GitHub Actions.

---

## Environment variables

| Variable | Required | Used by | Purpose |
|----------|----------|---------|---------|
| `OPENAI_API_KEY` | Yes | Backend | LangGraph AI analysis (GPT-4o) |
| `JWT_SECRET` | Recommended | Backend | JWT signing secret |
| `ADMIN_SECRET` | Recommended | Backend | Admin API key generation |
| `EXA_API_KEY` | No | Backend | External threat intelligence (Exa.ai) |
| `SENTINEL_API_URL` | No | SDK | Backend URL for event streaming |
| `SENTINEL_API_KEY` | No | SDK | API key for SDK-to-backend auth |
| `NEXT_PUBLIC_API_URL` | No | Dashboard | Backend URL (default `http://localhost:8001`) |

---

## Design decisions

- **Decorators for zero-friction adoption.** `@monitor`, `@sentinel`, `@monitor_mcp` — you don't change your agent code, you wrap it.
- **Thread-safe global registry.** All events from all decorated agents go into one `GlobalEventRegistry` (singleton, `threading.Lock`). Multi-agent pipelines get unified reporting for free.
- **Standalone or connected.** The SDK generates local JSON reports without a backend. Connect it to the Intelligence API and events stream automatically.
- **Iterative AI analysis.** LangGraph workflow with a Validator that can reject and retry up to 3 times. Better output than a single LLM call.
- **SQLite + WAL.** Zero-config deployment with concurrent read support. Foreign keys, indexes, and SHA-256 hashed API keys at the schema level.

---

## Why I built this

AI agents were being vibe-coded — built fast with AI assistance and shipped without security review. Traditional security tools don't understand agent-level threats. The tools that did appear required restructuring your agent around their framework.

I wanted to prove that developers will actually adopt a security tool if the cost is low enough: one decorator, zero code changes, you're monitored. The detection engine uses compiled regex patterns today — fast, deterministic, zero cost per call. The architecture is designed for pluggable detectors so ML classifiers or LLM-as-a-judge evaluators can be layered on top without touching the decorator code.

---

## Future roadmap

- **Blocking mode** — a `policy` parameter on the decorator (`log`, `warn`, `block`) to stop dangerous calls before they reach the agent
- **Agent sandbox** — run an agent against known attack vectors in isolation, get a security scorecard before deploying
- **Plugin architecture** — slot in ML classifiers, embedding-based detectors, or LLM-as-a-judge evaluators alongside regex patterns

---

## License

MIT
