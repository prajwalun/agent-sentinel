# Agent Sentinel - System Design

> **[README](./README.md)** — getting started, quick start, tests, config  
> **This file** — architecture, API reference, database schema, data flows, design decisions

## Overview

Agent Sentinel is a security monitoring platform for AI agents. It consists of three components that work independently or together:

1. **SDK** (`agent-sentinel-sdk/`) - Python library that instruments agent code via decorators
2. **Intelligence API** (`agent-sentinel-intelligence/`) - FastAPI backend with LangGraph-powered multi-agent analysis
3. **Dashboard** (`agent-sentinel-dashboard/`) - Next.js frontend for visualization and management

```
┌─────────────────────────────────────────────────────────────────────┐
│                         User's Agent Code                          │
│   @monitor / @sentinel / @monitor_mcp                              │
└──────────────────────────┬──────────────────────────────────────────┘
                           │ events
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Agent Sentinel SDK                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────────────┐  │
│  │ AgentWrapper  │  │ MCPWrapper   │  │ GlobalEventRegistry       │  │
│  │ InputValidator│  │              │  │ (singleton, thread-safe)  │  │
│  └──────┬───────┘  └──────┬───────┘  └───────────┬───────────────┘  │
│         └─────────────────┴──────────────────────┘                   │
│                           │                                          │
│         ┌─────────────────┼──────────────────┐                       │
│         ▼                 ▼                  ▼                       │
│  Local JSON report   Log files       BackendEventSink (HTTP)         │
└──────────────────────────┬───────────────────────────────────────────┘
                           │ POST /api/events
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Intelligence API  (FastAPI + SQLite + LangGraph)                    │
│  ┌────────┐ ┌──────────┐ ┌────────────┐ ┌────────────┐ ┌────────┐  │
│  │Analyzer│→│Supervisor│→│ Researcher │→│  Reporter  │→│Validator│  │
│  └────────┘ └──────────┘ └────────────┘ └────────────┘ └────────┘  │
│                                                                      │
│  Auth: JWT + API keys    SSE: /api/events/stream                     │
└──────────────────────────┬───────────────────────────────────────────┘
                           │ REST / SSE
                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Dashboard  (Next.js + Tailwind + shadcn/ui)                         │
│  Pages: Dashboard · Agents · Reports · Settings                      │
│  Auth: JWT via localStorage, client-side routing                     │
└──────────────────────────────────────────────────────────────────────┘
```

---

## 1. SDK (`agent-sentinel-sdk/`)

### Purpose

Provides zero-friction security monitoring for any AI agent built in Python, including single-agent functions, multi-agent pipelines, entire agent classes, and MCP tool servers. A single decorator instruments the target with no changes to the agent's own code. All events from all decorated agents flow into one global registry, enabling unified reporting across multi-agent systems.

### Decorator API

| Decorator | Target | What it does |
|-----------|--------|-------------|
| `@monitor` | Function or method | Wraps with `AgentWrapper.monitor()` - validates inputs/outputs per call |
| `@sentinel` | Class | Creates one `AgentWrapper`, wraps every public method |
| `@monitor_mcp` | MCP tool function | Creates an `MCPWrapper`, validates tool I/O |

### Execution Flow

```
@monitor(agent_id="my_agent")
def my_func(query):
    return llm.invoke(query)

# On each call:
# 1. Build MethodCallInfo (method name, timestamp, sanitized args)
# 2. InputValidator.validate(args) → SecurityEvent if threat found
# 3. Execute the real function
# 4. Optionally validate output (if validate_outputs=True)
# 5. Record call stats, push event to GlobalEventRegistry
```

### Threat Detection

`InputValidator` runs a multi-stage validation pipeline with 60+ compiled regex patterns across 6 threat categories. All patterns are compiled at import time for zero-allocation matching.

| Category | Patterns | Severity | Examples |
|----------|----------|----------|----------|
| SQL injection | 12 | CRITICAL | `UNION SELECT`, `DROP TABLE`, `INSERT INTO`, tautologies, comment injection |
| XSS | 11 | HIGH | `<script>`, `<iframe>`, `javascript:`, `data:base64`, event handlers |
| Prompt injection | 19 | HIGH | `ignore previous instructions`, `system prompt`, `jailbreak`, role manipulation |
| Command injection | 10 | CRITICAL | Shell metacharacters, `$(...)`, `rm -rf`, `wget`/`curl`, `sudo` |
| Path traversal | 8 | HIGH | `../`, `..\`, URL-encoded variants, `/etc/passwd` |
| Data exfiltration | Token analysis | CRITICAL | API key patterns, base64 credentials, suspicious outbound URLs |

The SDK defines 21 total `ThreatType` classifications. The 6 above are regex-detected on every call; the remaining 15 (privilege escalation, behavioral anomaly, cross-agent attack, timing attack, etc.) are used for risk scoring and report enrichment.

Each detection produces a `SecurityEvent` with `threat_type`, `severity` (LOW/MEDIUM/HIGH/CRITICAL), `confidence` (0.0–1.0), and full context.

### Event Storage

`GlobalEventRegistry` is a thread-safe singleton. Events are stored in memory and optionally:
- Written to per-agent JSON log files
- Pushed to the Intelligence API via `BackendEventSink`
- Exported via `AgentSentinel.generate_unified_report()`

### Key Files

| File | Responsibility |
|------|---------------|
| `wrappers/decorators.py` | `@monitor`, `@sentinel` entry points |
| `wrappers/agent_wrapper.py` | `AgentWrapper` - execution, validation, recording |
| `wrappers/mcp_wrapper.py` | `MCPWrapper`, `secure_mcp_method` (aliased as `monitor_mcp`) |
| `security/validators.py` | `InputValidator` - regex-based threat detection |
| `core/event_registry.py` | `GlobalEventRegistry` - singleton event store |
| `core/sentinel.py` | `AgentSentinel` - top-level API, report generation |
| `core/report_generator.py` | Unified JSON report builder |

---

## 2. Intelligence API (`agent-sentinel-intelligence/`)

### Purpose

Receives security events from the SDK, stores them in SQLite, and runs AI-powered multi-agent analysis using LangGraph to produce enriched threat intelligence reports.

### API Design

All endpoints are prefixed with `/api/`. Authentication is either JWT (for dashboard users) or API key (for SDK clients).

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | `/api/auth/signup` | None | Create user account |
| POST | `/api/auth/login` | None | Get JWT token |
| GET | `/api/auth/me` | JWT | Current user profile |
| POST | `/api/events` | API key | Ingest security event |
| GET | `/api/events/stream` | JWT (query param) | SSE live event stream |
| GET | `/api/agents` | JWT/Key | List agents (paginated) |
| POST | `/api/agents` | API key | Register agent |
| GET | `/api/agents/{id}/events` | JWT/Key | Events for agent |
| POST | `/api/analysis/start` | JWT | Start async AI analysis |
| GET | `/api/analysis/{run_id}/status` | JWT | Poll analysis status |
| POST | `/api/keys` | JWT | Create API key |
| DELETE | `/api/keys/{id}` | JWT | Revoke API key |
| GET | `/api/reports` | JWT | List analysis runs |
| GET | `/api/dashboard/stats` | JWT | Aggregate dashboard stats |

#### Key request/response examples

```http
POST /api/auth/login
{"email": "user@example.com", "password": "..."}

→ {"token": "<jwt>", "user": {"id": "...", "email": "...", "name": "..."}}
```

```http
POST /api/events
Authorization: Bearer <api-key>

{
  "agent_id": "my_agent",
  "threat_type": "sql_injection",
  "severity": "HIGH",
  "confidence": 0.95,
  "message": "UNION SELECT detected in query parameter",
  "context": {"method": "search", "arg": "' UNION SELECT ..."}
}

→ {"status": "ok", "event_id": "my_agent_1234567890"}
```

```http
POST /api/analysis/start
Authorization: Bearer <jwt>
Content-Type: multipart/form-data  (report file)

→ {"run_id": "abc123", "status": "pending"}

GET /api/analysis/abc123/status
→ {"status": "running"}   (poll until complete)
→ {"status": "complete", "result": { ...UnifiedReport... }}
```

### Database (SQLite)

Key design decisions:
- Foreign keys enforced (`PRAGMA foreign_keys=ON`)
- WAL mode for concurrent reads during analysis
- Indexes on query-hot columns (agent+time, severity, status, created_at)
- API key hashes stored (never raw keys)
- In-memory shared connection for `:memory:` testing

#### Schema

```sql
-- Users created via /api/auth/signup
users (
    id            TEXT PRIMARY KEY,
    email         TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,          -- bcrypt
    name          TEXT NOT NULL DEFAULT '',
    created_at    TEXT NOT NULL,
    is_active     INTEGER NOT NULL DEFAULT 1
)

-- Agents registered by the SDK on first event
agents (
    id          TEXT PRIMARY KEY,         -- matches agent_id from decorator
    name        TEXT NOT NULL,
    type        TEXT NOT NULL DEFAULT 'generic',
    status      TEXT NOT NULL DEFAULT 'active',
    created_at  TEXT NOT NULL,
    last_seen   TEXT                      -- updated on every event
)

-- One row per detected threat
security_events (
    id               TEXT PRIMARY KEY,
    agent_id         TEXT NOT NULL REFERENCES agents(id),
    threat_type      TEXT NOT NULL,
    severity         TEXT NOT NULL CHECK (severity IN ('LOW','MEDIUM','HIGH','CRITICAL')),
    confidence       REAL NOT NULL CHECK (confidence BETWEEN 0.0 AND 1.0),
    message          TEXT NOT NULL,
    context_json     TEXT,               -- full call context as JSON
    detection_method TEXT,
    detected_at      TEXT NOT NULL
)

-- API keys for SDK → backend authentication
api_keys (
    id          TEXT PRIMARY KEY,
    key_hash    TEXT NOT NULL UNIQUE,    -- SHA-256; raw key shown once on creation
    user_id     TEXT NOT NULL REFERENCES users(id),
    description TEXT NOT NULL DEFAULT '',
    created_at  TEXT NOT NULL,
    last_used   TEXT,
    call_count  INTEGER NOT NULL DEFAULT 0,
    is_active   INTEGER NOT NULL DEFAULT 1
)

-- Rolling window for per-user rate limiting (100 req/hr)
request_log (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      TEXT NOT NULL REFERENCES users(id),
    requested_at TEXT NOT NULL
)

-- One row per AI analysis run (async background job)
analysis_runs (
    id           TEXT PRIMARY KEY,
    agent_id     TEXT NOT NULL REFERENCES agents(id),
    input_hash   TEXT NOT NULL,          -- dedup identical reports
    status       TEXT NOT NULL DEFAULT 'pending',  -- pending|running|complete|failed
    risk_level   TEXT,
    result_json  TEXT,                   -- full UnifiedReport JSON on completion
    created_at   TEXT NOT NULL,
    completed_at TEXT,
    duration_ms  INTEGER
)
```

Indexes: `idx_events_agent_time`, `idx_events_severity`, `idx_events_threat_type`, `idx_runs_status`, `idx_runs_created_at`, `idx_reqlog_user_time`, `idx_agents_last_seen`, `idx_keys_hash`

### Failure modes

| Condition | Behavior |
|-----------|----------|
| `OPENAI_API_KEY` not set | Backend starts normally; `POST /api/analysis/start` returns 503 |
| `EXA_API_KEY` not set | Researcher agent skips web lookup; report still generated |
| Database file missing | Created automatically on first startup |
| Rate limit exceeded (100 req/hr) | 429 returned; window resets on the hour |
| Analysis run evicted from memory | Status polled from `analysis_runs` table as fallback |
| JWT expired | 401 returned; client must re-authenticate |

### LangGraph Workflow

Analysis runs asynchronously in a background thread. The workflow is a directed graph with iterative refinement:

```
Analyzer → Supervisor → Researcher → Reporter → Validator
              ↑                                      │
              └──────── (feedback loop, max 3) ──────┘
```

- **Analyzer**: Extracts threats, patterns, severity from raw event data
- **Supervisor**: Routes to research or reporting based on completeness
- **Researcher**: Queries Exa.ai for external threat intelligence
- **Reporter**: Generates markdown narrative with recommendations
- **Validator**: Checks report quality; can send back to Supervisor for refinement

### Security

- JWT tokens (HS256) for user sessions
- API keys with SHA-256 hashing, per-user ownership, revocation support
- Rate limiting (100 req/hr per user via `request_log`)
- Input sanitization on all string fields
- CORS restricted to dashboard origin
- SSE stream requires JWT token as query parameter

### Key Files

| File | Responsibility |
|------|---------------|
| `api_server.py` | FastAPI app, all endpoints, auth middleware |
| `src/database/connection.py` | SQLite connection management, schema DDL |
| `src/database/repository.py` | Data access layer (CRUD operations) |
| `src/workflow.py` | LangGraph workflow definition |
| `src/models/state.py` | `AgentState` TypedDict for workflow state |
| `src/models/config.py` | Pydantic settings with env var binding |

---

## 3. Dashboard (`agent-sentinel-dashboard/`)

### Purpose

A Next.js web application that provides real-time visibility into agent security posture, event history, AI-powered analysis reports, and system management.

### Architecture

- **Framework**: Next.js 14 (App Router)
- **Styling**: Tailwind CSS + shadcn/ui components
- **Auth**: JWT stored in `localStorage`, managed by `AuthContext`
- **Data fetching**: `apiService` wrapper with automatic 401 handling
- **Live events**: SSE via `useLiveEvents` hook with JWT auth

### Pages

| Page | Component | Description |
|------|-----------|-------------|
| `/` | `DashboardView` | System health, severity chart, recent events, quick actions |
| `/agents` | `AgentsView` | Agent list with event counts, detail view, trigger analysis |
| `/reports` | Upload + History tabs | File upload for SDK reports, async analysis with polling |
| `/settings` | `SettingsView` | API key management (create/revoke), notification preferences |
| `/login` | `LoginView` | Email/password authentication |

### Report Visualization

`ReportVisualization` renders AI analysis results with:
- Executive summary (risk level, threat count, confidence)
- Threat breakdown by type and severity
- AI Intelligence Insights (markdown prose from LLM)
- Recommendations list
- Export to PDF (`window.print()` with print stylesheet) and JSON

### Key Files

| File | Responsibility |
|------|---------------|
| `contexts/AuthContext.tsx` | JWT auth state, login/logout, localStorage sync |
| `lib/api.ts` | `apiService` - typed HTTP client for all backend calls |
| `hooks/useLiveEvents.ts` | SSE hook for real-time event streaming |
| `components/dashboard/DashboardView.tsx` | Main dashboard layout |
| `components/reports/ReportVisualization.tsx` | Report renderer with PDF/JSON export |
| `components/settings/SettingsView.tsx` | Key management, preferences |
| `middleware.ts` | Security headers (X-Frame-Options, Referrer-Policy) |

---

## 4. Data Flow

### SDK → Backend (Event Ingestion)

```
Agent call → @monitor detects threat → SecurityEvent created
    → GlobalEventRegistry.register_event()
    → BackendEventSink.send() → POST /api/events (API key auth)
    → SQLite: security_events table
    → SSE broadcast to connected dashboard clients
```

### Dashboard → Backend (Analysis)

```
User uploads report file → POST /api/analysis/start
    → Background thread: LangGraph workflow runs
    → Polls GET /api/analysis/{run_id}/status every 3s
    → On completion: renders ReportVisualization
```

### SDK Local (Standalone Mode)

```
Agent call → @monitor detects threat → SecurityEvent
    → AgentSentinel.generate_unified_report()
    → JSON file in logs/ directory
    → User uploads to dashboard for AI analysis
```

---

## 5. Testing

### Test Suites

| Suite | Location | What it covers |
|-------|----------|----------------|
| Backend API | `agent-sentinel-intelligence/tests/test_api.py` | Auth, CRUD, key lifecycle, SSE, pagination, analysis |
| SDK unit | `agent-sentinel-sdk/tests/` | Core SDK, decorators, validators, wrappers |
| Dashboard | `agent-sentinel-dashboard/__tests__/` | API service layer, auth context, localStorage handling |
| E2E synthetic | `tests/test_e2e_synthetic.py` | Inline agents: single/multi/MCP, safe and malicious |
| E2E integration | `tests/test_e2e_integration.py` | A2A protocol agents, Agno/OpenAI (optional setup) |

### Running Tests

```bash
# Backend API tests
cd agent-sentinel-intelligence && python -m pytest tests/ -v

# SDK tests
cd agent-sentinel-sdk && python -m pytest tests/ -v

# Dashboard tests
cd agent-sentinel-dashboard && npm test

# E2E synthetic tests (from repo root)
python tests/test_e2e_synthetic.py

# E2E integration tests (optional; requires A2A/Agno agents)
python tests/test_e2e_integration.py
```

---

## Future Improvements

### Short-term

- **Blocking / enforcement mode.** The SDK currently logs threats but never blocks execution. A planned `policy` parameter on the decorator (`@monitor(policy="block")`) will let developers enforce rules: block the call, return a sanitized fallback, or escalate to a human-in-the-loop review before the agent output reaches the caller.
- **Remediation suggestions.** When a threat is flagged, the analysis report should include actionable guidance: input parameterization for SQL injection, prompt hardening for injection attempts, URL allowlisting for exfiltration patterns.
- **Webhook / alerting integrations.** Push real-time notifications (Slack, PagerDuty, email) for CRITICAL-severity events so that security teams can react without polling the dashboard.

### Medium-term

- **Agent sandbox.** A dashboard feature where a developer uploads an agent and runs it against a curated attack suite (prompt injection variants, tool manipulation, data exfiltration probes) inside an isolated container. The output is a security scorecard with pass/fail per threat category, generated before the agent is deployed to production.
- **Advanced policy engine.** Per-agent or per-organization rules: "block all SQL-like patterns for this agent", "allow outbound URLs only from these domains", "flag any output exceeding N tokens." Policies are stored in the database and evaluated at the decorator layer for zero-latency enforcement.
- **Multi-tenant support.** Organization-scoped agents, API keys, and dashboards, enabling SaaS deployment where multiple teams share the backend without data leakage.

### Long-term / scaling

- **PostgreSQL migration.** Replace SQLite with PostgreSQL for horizontal read/write scaling, connection pooling (PgBouncer), and production-grade durability across multiple backend replicas.
- **Redis integration.** Shared rate-limiting counters, cross-instance event buffering, and pub/sub for real-time SSE fan-out to multiple dashboard instances.
- **Kubernetes-native deployment.** Helm charts with HPA for the backend and dashboard, persistent volume claims for the database, and network policies for security isolation.
- **SDK plugin architecture.** Allow third-party threat detectors (custom regex sets, ML-based classifiers, LLM-as-a-judge evaluators) to be plugged into the SDK validation pipeline without modifying core code.
