# Agent Sentinel SDK

Python library that adds security monitoring to AI agents via decorators. Validates inputs (and optionally outputs) against compiled regex patterns for SQL injection, XSS, prompt injection, command injection, path traversal, and data exfiltration.

## Install

```bash
pip install agent-sentinel
```

## Usage

```python
from agent_sentinel import monitor, sentinel, monitor_mcp

@monitor
def my_agent(query: str) -> str:
    return llm.invoke(query)

@sentinel
class Pipeline:
    def plan(self, task): ...
    def execute(self, plan): ...

@monitor_mcp(agent_id="tools")
def search(query): ...
```

Every decorated call is validated. Threats produce a `SecurityEvent` with type, severity, and confidence score. Events flow into a thread-safe `GlobalEventRegistry` for unified reporting across multi-agent pipelines.

## Standalone usage

Use the SDK without the backend or dashboard for local threat detection and report generation. No `SENTINEL_API_URL` or `SENTINEL_API_KEY` needed.

```python
from agent_sentinel import monitor, default_sentinel

@monitor
def my_agent(query: str) -> str:
    return llm.invoke(query)

my_agent("user input")  # run your agent

# Get reports locally
default_sentinel.generate_unified_report()  # JSON to logs/
default_sentinel.generate_security_report(file_path="report.md")  # Markdown
# Or get events programmatically:
events = default_sentinel.get_events(include_all_agents=True)
```

**Report outputs:**
- `generate_unified_report()` — JSON with events, metrics, recommendations
- `generate_security_report(file_path=...)` — Markdown summary (custom path optional)
- `get_all_events()` — list of `SecurityEvent` objects

**Where logs and reports go:**
- Default: `logs/` directory in the current working directory (where you run your script)
- Directory is created automatically; no need to create it or pass a path
- Log files: `logs/agent_sentinel_{agent_id}.log`
- Unified report: `logs/{agent_id}_unified_report_{timestamp}.json`
- Security report: `logs/{agent_id}_security_report_{timestamp}.md` (or custom path via `file_path=...`)

## Tests

```bash
pip install -e ".[test]"
python -m pytest tests/ -v
```

## Docs

- [Main README](../README.md): project overview, getting started, architecture
- [System Design](../SYSTEM_DESIGN.md): SDK internals, threat detection details, API reference
