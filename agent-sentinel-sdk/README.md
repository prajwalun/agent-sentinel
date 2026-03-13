# Agent Sentinel SDK

Security monitoring for AI agents via decorators. Validates inputs against SQL injection, XSS, prompt injection, command injection, path traversal, and data exfiltration.

**Two modes:** Connect to the backend (events stream to the dashboard) or run **standalone** (local reports only, no backend needed).

## Install

```bash
python3 -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install agent-sentinel
```

## Usage (with backend)

Set `SENTINEL_API_URL` and `SENTINEL_API_KEY`. Events stream to the dashboard.

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

## Standalone (no backend)

No `SENTINEL_API_URL` or `SENTINEL_API_KEY` needed. Local threat detection and reports only.

```python
from agent_sentinel import monitor, default_sentinel

@monitor
def my_agent(query: str) -> str:
    return llm.invoke(query)

my_agent("user input")

default_sentinel.generate_unified_report()       # JSON to logs/
default_sentinel.generate_security_report(file_path="report.md")  # Markdown
events = default_sentinel.get_events(include_all_agents=True)
```

**Outputs:** `logs/` in the current directory. Logs: `agent_sentinel_{agent_id}.log`. Reports: `{agent_id}_unified_report_{timestamp}.json`, `{agent_id}_security_report_{timestamp}.md`.

**Event structure:** Each `SecurityEvent` includes `threat_type`, `severity`, `message`, `confidence`, `agent_id`, `timestamp`, `context`. Example:

```json
{"threat_type": "prompt_injection", "severity": "HIGH", "confidence": 0.8, "agent_id": "..."}
```

## Tests

```bash
pip install -e ".[test]"
python -m pytest tests/ -v
```

## Docs

- [Main README](../README.md) — project overview, getting started
- [System Design](../SYSTEM_DESIGN.md) — internals, API reference
