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

## Tests

```bash
pip install -e ".[test]"
python -m pytest tests/ -v
```

## Docs

- [Main README](../README.md): project overview, getting started, architecture
- [System Design](../SYSTEM_DESIGN.md): SDK internals, threat detection details, API reference
