# Agent Sentinel

**Enterprise security monitoring for AI agents. One decorator. Real-time threat detection. Full-stack visibility.**

Agent Sentinel secures AI agents of any kind: single-agent functions, multi-agent pipelines, MCP tool servers, or entire agent classes. Add a decorator to your existing code and the SDK automatically validates inputs and outputs, detects security threats (prompt injection, SQL injection, XSS, command injection, data exfiltration, and more), records events in a thread-safe registry, and optionally streams them to a live dashboard backed by AI-powered analysis.

No changes to your agent code. No subclassing. No framework lock-in.

---

## Why I Built This

The rise of AI agents brought a wave of "vibe-coded" projects - agents built rapidly with AI assistance, published to GitHub, and deployed without any security review. The AI-generated code itself often introduced vulnerabilities (unsanitized inputs, hardcoded credentials, unsafe tool calls), and the agents themselves became a new attack surface that traditional security tools were never designed to handle. WAFs and SAST scanners do not understand prompt injection. Firewalls do not catch an agent being tricked into exfiltrating data through its own tool calls.

I saw two problems happening at the same time: agents were being deployed faster than teams could review them, and the tooling to secure them simply did not exist. The security tools that did start appearing required significant integration effort - SDKs that demanded you restructure your agent around their framework, or platforms that only worked with specific agent libraries.

I wanted to build something that a developer could adopt in 30 seconds. That is why Agent Sentinel uses decorators: you add one line to your existing agent and it is immediately monitored. No refactoring, no framework migration, no configuration files. The goal is to make the secure path the easy path.

---

## What It Monitors

Agent Sentinel is designed to work across the full spectrum of AI agent architectures:

| Agent Pattern | Decorator | How It Works |
|--------------|-----------|-------------|
| **Single agent function** | `@monitor` | Wraps any function or method. Validates inputs/outputs on every call. |
| **Agent class** (multi-method) | `@sentinel` | Wraps an entire class. Instruments all public methods with a single decorator. |
| **Multi-agent pipeline** | `@monitor` on each | Each agent in the pipeline gets its own decorator. Events from all agents aggregate into one global registry for unified reporting. |
| **MCP tool server** | `@monitor_mcp` | Wraps MCP tool functions. Validates tool inputs/outputs and monitors tool invocation patterns. |
| **Any combination** | Mix all three | Use `@sentinel` on your orchestrator class, `@monitor` on helper functions, and `@monitor_mcp` on tool endpoints. All events flow to the same registry. |

### Quick Start

```bash
pip install agent-sentinel
```

```python
from agent_sentinel import monitor, sentinel, monitor_mcp, AgentSentinel

# Single agent function
@monitor
def research_agent(query: str) -> str:
    return llm.invoke(query)

# Entire agent class - wraps all public methods automatically
@sentinel
class AnalysisAgent:
    def analyze(self, data: str) -> str:
        return self.llm.analyze(data)

    def summarize(self, report: str) -> str:
        return self.llm.summarize(report)

# MCP tool server
@monitor_mcp(agent_id="search_tools")
def web_search(query: str) -> str:
    return search_api.search(query)

# Multi-agent pipeline - each agent monitored independently
@monitor(agent_id="planner")
def planner(task: str) -> str:
    return llm.plan(task)

@monitor(agent_id="executor")
def executor(plan: str) -> str:
    return llm.execute(plan)

def run_pipeline(task):
    plan = planner(task)       # monitored
    result = executor(plan)    # monitored
    return result

# All events from all agents are in one registry
sentinel_instance = AgentSentinel()
sentinel_instance.generate_unified_report()  # single report across all agents
```

---

## Project Structure

```
agent-sentinel-sdk/            Python SDK: decorators, threat detection, event registry
agent-sentinel-intelligence/   FastAPI backend: auth, SQLite storage, LangGraph AI analysis
agent-sentinel-dashboard/      Next.js frontend: real-time dashboard, reports, settings
tests/                         E2E test suites with synthetic and real agent integrations
```

## Architecture

```
+------------------------------------------------------------------+
|  Your Agent Code                                                  |
|  @monitor / @sentinel / @monitor_mcp                              |
+-------------------------------+----------------------------------+
                                | events
                                v
+------------------------------------------------------------------+
|  Agent Sentinel SDK                                               |
|  AgentWrapper / MCPWrapper / InputValidator                       |
|  GlobalEventRegistry (singleton, thread-safe)                     |
|                                                                   |
|  Outputs:                                                         |
|    - Local JSON reports and log files                             |
|    - BackendEventSink -> POST /api/events (auto-push to backend)  |
+-------------------------------+----------------------------------+
                                | HTTP (API key auth)
                                v
+------------------------------------------------------------------+
|  Intelligence API  (FastAPI + SQLite + LangGraph)                 |
|  - 20+ REST endpoints (auth, agents, events, analysis, keys)     |
|  - SSE live event stream                                          |
|  - Async AI analysis: Analyzer > Supervisor > Researcher >        |
|    Reporter > Validator (iterative, max 3 refinement loops)       |
+-------------------------------+----------------------------------+
                                | REST + SSE
                                v
+------------------------------------------------------------------+
|  Dashboard  (Next.js + Tailwind + shadcn/ui)                      |
|  Pages: Dashboard, Agents, Reports, Settings                      |
|  Auth: JWT (email/password), client-side routing                  |
+------------------------------------------------------------------+
```

For the full architecture, data flows, API reference, and database schema, see [SYSTEM_DESIGN.md](./SYSTEM_DESIGN.md).

---

## Threat Detection

### Detection Pipeline

Every decorated call passes through a multi-stage validation pipeline before and (optionally) after execution:

```
Agent Input
  │
  ├─► InputValidator
  │     ├─ SQLInjectionValidator    (12 compiled regex patterns)
  │     ├─ XSSValidator             (11 compiled regex patterns)
  │     ├─ CommandInjectionValidator (10 compiled regex patterns)
  │     └─ PromptInjectionValidator (19 compiled regex patterns)
  │
  ├─► PathTraversalDetector          (8 compiled regex patterns)
  ├─► DataExfiltrationDetector       (sensitive token counting, URL analysis)
  │
  ▼
Execute Agent Function
  │
  ├─► OutputValidator (when validate_outputs=True)
  │     └─ Same pattern checks on agent response
  │
  ▼
SecurityEvent(threat_type, severity, confidence, context)
  └─► GlobalEventRegistry (thread-safe singleton)
```

### 60+ Compiled Regex Patterns Across 6 Threat Categories

All patterns are compiled at import time (`re.compile`) for zero-allocation matching at runtime.

| Threat | Patterns | Severity | What It Catches |
|--------|----------|----------|----------------|
| **SQL injection** | 12 | CRITICAL | `UNION SELECT`, `DROP TABLE`, `INSERT INTO`, `DELETE FROM`, tautologies (`' OR '1'='1'`), comment injection (`--`, `/* */`) |
| **XSS** | 11 | HIGH | `<script>`, `<iframe>`, `<embed>`, `<object>`, `javascript:`, `vbscript:`, `data:base64`, event handlers (`onerror=`, `onload=`) |
| **Prompt injection** | 19 | HIGH | `ignore previous instructions`, `forget all rules`, `pretend to be`, `system prompt`, `override instructions`, `jailbreak`, `reset conversation`, role manipulation |
| **Command injection** | 10 | CRITICAL | Shell metacharacters (`;`, `|`, `` ` ``), `$(...)` subshells, `rm -rf`, `wget`/`curl` to external hosts, `sudo`, `chmod`, `nc` |
| **Path traversal** | 8 | HIGH | `../`, `..\`, URL-encoded variants (`%2e%2e%2f`), `/etc/passwd`, `/windows/system32` |
| **Data exfiltration** | Token analysis | CRITICAL | API key patterns, base64-encoded credentials, high density of sensitive tokens, suspicious outbound URLs |

### 21 Threat Type Classifications

Beyond the 6 regex-detected categories, the SDK defines 21 total threat types used for risk scoring, report enrichment, and the enterprise detection engine:

`sql_injection` · `xss_attack` · `command_injection` · `path_traversal` · `prompt_injection` · `data_exfiltration` · `rate_limit_violation` · `resource_exhaustion` · `malicious_payload` · `unauthorized_access` · `behavioral_anomaly` · `communication_tampering` · `privilege_escalation` · `suspicious_tool_usage` · `unusual_data_access` · `timing_attack` · `frequency_attack` · `sequence_attack` · `parameter_manipulation` · `resource_abuse` · `cross_agent_attack`

### SecurityEvent Output

Each detection produces a `SecurityEvent` containing:
- `threat_type` — which of the 21 categories was triggered
- `severity` — rated LOW, MEDIUM, HIGH, or CRITICAL
- `confidence` — score from 0.0 to 1.0, based on pattern match strength
- `context` — the triggering input, matched pattern, and detection method
- `timestamp` — UTC time of detection

---

## Running the Full Stack

### 1. Backend (Intelligence API)

```bash
cd agent-sentinel-intelligence
pip install -r requirements.txt
```

Create a `.env` file (or copy from `.env.example`):

```
OPENAI_API_KEY=your_openai_key
JWT_SECRET=your_random_secret
```

Start the server:

```bash
uvicorn api_server:app --host 0.0.0.0 --port 8001
```

### 2. Dashboard

```bash
cd agent-sentinel-dashboard
npm install
echo 'NEXT_PUBLIC_API_URL=http://localhost:8001' > .env.local
npm run dev
```

Open `http://localhost:3000`, create an account, and generate an API key from the Settings page.

### 3. Connect the SDK to the Backend

Set two environment variables so the SDK automatically streams events to the backend:

```bash
export SENTINEL_API_URL=http://localhost:8001
export SENTINEL_API_KEY=<your API key from the dashboard>
```

Then use the SDK as normal:

```python
from agent_sentinel import monitor

@monitor
def my_agent(query):
    return process(query)

# Events are now sent to the backend in real time.
# Open the dashboard to see them appear on the Agents page
# and in the live event stream.
```

### 4. Docker (Full Stack)

```bash
docker-compose up --build
```

This starts the backend on port 8001 and the dashboard on port 3000.

---

## Testing

The project has 97+ automated tests across four suites:

```bash
# Backend API tests (39 tests)
cd agent-sentinel-intelligence && python -m pytest tests/ -v

# SDK unit tests (52 tests)
cd agent-sentinel-sdk && python -m pytest tests/ -v

# E2E with synthetic agents (6 scenarios: single/multi/MCP, safe/malicious)
python tests/test_agents_e2e.py

# E2E with real agents (8 scenarios: A2A protocol agents, Agno + OpenAI)
python tests/test_real_agents_e2e.py
```

The E2E tests verify that:
- Safe agents produce zero threat events
- Malicious agents (SQL injection, prompt injection, data exfiltration) are detected
- Multi-agent pipelines with a compromised agent in the chain are caught
- MCP tool servers with malicious tool I/O trigger security events
- Real-world agent frameworks (A2A protocol, Agno/OpenAI) work with the SDK decorators

---

## Environment Variables

| Variable | Used By | Purpose |
|----------|---------|---------|
| `OPENAI_API_KEY` | Backend | Powers the LangGraph AI analysis workflow (GPT-4o) |
| `EXA_API_KEY` | Backend (optional) | External threat intelligence research via Exa.ai |
| `SENTINEL_API_URL` | SDK (optional) | Backend URL for automatic event streaming |
| `SENTINEL_API_KEY` | SDK (optional) | API key for SDK-to-backend authentication |
| `JWT_SECRET` | Backend | Secret for signing JWT tokens (auto-generated if unset) |
| `ADMIN_SECRET` | Backend | Secret for admin-level API key generation |
| `NEXT_PUBLIC_API_URL` | Dashboard | Backend URL the dashboard connects to |

---

## Key Design Decisions

- **Decorator-based instrumentation.** The SDK uses Python decorators (`@monitor`, `@sentinel`, `@monitor_mcp`) so that securing an agent requires zero changes to the agent's own code. This works with any Python agent framework.
- **Thread-safe global event registry.** All decorators write to a singleton `GlobalEventRegistry` protected by `threading.Lock`. This allows multi-agent pipelines to aggregate events from independent agents into a single unified report.
- **Dual-mode operation.** The SDK works standalone (local reports and log files) or connected (auto-pushes events to the backend via `BackendEventSink`). No backend required for basic threat detection.
- **Async AI analysis.** The Intelligence API runs LangGraph workflows in background threads and returns a `run_id` for polling. The dashboard polls every 3 seconds and renders results when complete.
- **Iterative refinement.** The LangGraph workflow includes a Validator agent that can reject a report and send it back to the Supervisor for re-analysis, up to 3 times. This produces higher-quality threat intelligence.
- **SQLite with WAL mode.** The backend uses SQLite for zero-configuration deployment while supporting concurrent reads during long-running analysis. Foreign keys, indexes on hot columns, and SHA-256 hashed API keys are enforced at the schema level.

---

## Future Roadmap

Agent Sentinel currently operates in **detection mode** - it identifies and reports threats but does not block them. The next evolution is making it preventive:

- **Blocking mode.** Give the decorator a policy (log-only, warn, or block). In block mode, a function call that triggers a HIGH or CRITICAL threat is stopped before it reaches the agent, and the caller gets a safe error instead of a compromised response.
- **Agent sandbox.** A dashboard feature where you upload an agent and run it against a suite of known attack vectors (prompt injection, tool manipulation, data exfiltration attempts) in an isolated environment. You see a security scorecard before deploying the agent to production.
- **Remediation suggestions.** When a threat is detected, suggest a concrete fix: input sanitization for SQL injection, prompt hardening for prompt injection, URL allowlisting for exfiltration attempts.
- **Policy engine.** Configurable per-agent rules: "block all SQL patterns for this agent", "allow external URLs only from these domains", "flag any output longer than 10,000 characters."
- **Alerting integrations.** Push notifications to Slack, PagerDuty, or email when a critical threat is detected, so security teams can respond in real time.
- **PostgreSQL and Redis.** Replace SQLite for horizontal scaling across multiple backend instances, and add Redis for shared rate limiting and event buffering.

---

## License

MIT. See [LICENSE](./LICENSE).
