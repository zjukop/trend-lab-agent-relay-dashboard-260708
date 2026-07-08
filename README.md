# Agent Relay Dashboard

Tiny starter for a local CLI/web dashboard that runs the same coding task across multiple agent commands and compares results.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
agent-relay --task "add a health endpoint"
```

Open <http://127.0.0.1:8000> to view the report.

## Notes

This minimal version ships with mock shell adapters and a FastAPI dashboard. Extend `src/agent_relay_dashboard/main.py` to add real Claude, Gemini, Codex, or MCP integrations.

## Test

```bash
pytest
```
