# Agent Sentinel - System Design

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

`InputValidator` uses compiled regex patterns to detect:

- **SQL injection** - `DROP TABLE`, `UNION SELECT`, `' OR 1=1`, tautologies
- **XSS** - `<script>`, `onerror=`, `javascript:`, event handlers
- **Command injection** - `; rm`, `| curl`, backtick execution
- **Prompt injection** - `ignore previous instructions`, `system prompt`, role overrides
- **Path traversal** - `../../etc/passwd`, `..\\windows`
- **Data exfiltration** - suspicious URLs, credential patterns

Each detection produces a `SecurityEvent` with `threat_type`, `severity` (LOW/MEDIUM/HIGH/CRITICAL), and `confidence` (0.0–1.0).

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

### Database (SQLite)

Tables: `users`, `agents`, `security_events`, `api_keys`, `request_log`, `analysis_runs`

Key design decisions:
- Foreign keys enforced (`PRAGMA foreign_keys=ON`)
- WAL mode for concurrent reads during analysis
- Indexes on query-hot columns (agent+time, severity, status, created_at)
- API key hashes stored (never raw keys)
- In-memory shared connection for `:memory:` testing

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
- Export to PDF (`window.print()` with print stylesheet) and Share (clipboard)

### Key Files

| File | Responsibility |
|------|---------------|
| `contexts/AuthContext.tsx` | JWT auth state, login/logout, localStorage sync |
| `lib/api.ts` | `apiService` - typed HTTP client for all backend calls |
| `hooks/useLiveEvents.ts` | SSE hook for real-time event streaming |
| `components/dashboard/DashboardView.tsx` | Main dashboard layout |
| `components/reports/ReportVisualization.tsx` | Report renderer with PDF/share |
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

| Suite | Location | Count | What it covers |
|-------|----------|-------|----------------|
| Backend API | `agent-sentinel-intelligence/tests/test_api.py` | 39 | Auth, CRUD, key lifecycle, SSE, pagination, analysis |
| SDK unit | `agent-sentinel-sdk/tests/` | 52 | Core SDK, decorators, validators, wrappers |
| SDK E2E (synthetic) | `tests/test_agents_e2e.py` | 6 | Synthetic agents: single/multi/MCP, safe/malicious |
| Real agent E2E | `tests/test_real_agents_e2e.py` | 8 | A2A protocol agents, Agno HackerNews researcher |

### Running Tests

```bash
# Backend API tests
cd agent-sentinel-intelligence && python -m pytest tests/ -v

# SDK tests
cd agent-sentinel-sdk && python -m pytest tests/ -v

# E2E agent tests (from repo root)
python tests/test_agents_e2e.py
python tests/test_real_agents_e2e.py
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
