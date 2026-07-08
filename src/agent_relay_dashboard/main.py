from __future__ import annotations

import subprocess
import time
from dataclasses import asdict, dataclass
from typing import Annotated

import typer
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

cli_app = typer.Typer(help="Race multiple coding agents and compare their output.")
app = FastAPI(title="Agent Relay Dashboard")


@dataclass(frozen=True)
class AgentRun:
    name: str
    command: str
    status: str
    duration_s: float
    notes: str


LAST_TASK = "No task submitted yet."
LAST_RUNS: list[AgentRun] = []


def run_agent(name: str, command: str, task: str, timeout: int = 10) -> AgentRun:
    start = time.perf_counter()
    try:
        result = subprocess.run(
            command.format(task=task),
            shell=True,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        status = "passed" if result.returncode == 0 else "failed"
        notes = (result.stdout or result.stderr or "no output").strip()[:400]
    except subprocess.TimeoutExpired:
        status = "timeout"
        notes = f"Exceeded {timeout}s budget"
    return AgentRun(name, command, status, round(time.perf_counter() - start, 2), notes)


def run_relay(task: str) -> list[AgentRun]:
    adapters = {
        "claude-code": "echo Claude would implement: {task}",
        "gemini-cli": "echo Gemini would implement: {task}",
        "codex-cli": "echo Codex would implement: {task}",
        "local-mcp": "echo MCP tool would inspect: {task}",
    }
    return [run_agent(name, command, task) for name, command in adapters.items()]


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/report")
def api_report() -> dict[str, object]:
    return {"task": LAST_TASK, "runs": [asdict(run) for run in LAST_RUNS]}


@app.get("/", response_class=HTMLResponse)
def dashboard() -> str:
    rows = "".join(
        f"<tr><td>{r.name}</td><td>{r.status}</td><td>{r.duration_s}s</td><td><pre>{r.notes}</pre></td></tr>"
        for r in LAST_RUNS
    )
    return f"""
    <html><head><title>Agent Relay Dashboard</title></head>
    <body>
      <h1>Agent Relay Dashboard</h1>
      <p><strong>Task:</strong> {LAST_TASK}</p>
      <table border="1" cellpadding="6">
        <thead><tr><th>Agent</th><th>Status</th><th>Duration</th><th>Notes</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </body></html>
    """


@cli_app.command()
def serve(
    task: Annotated[str, typer.Option(help="Coding task to relay")] = "compare agent patches",
    host: str = "127.0.0.1",
    port: int = 8000,
) -> None:
    global LAST_TASK, LAST_RUNS
    LAST_TASK = task
    LAST_RUNS = run_relay(task)
    typer.echo(f"Dashboard: http://{host}:{port}")
    uvicorn.run(app, host=host, port=port, log_level="warning")


def cli() -> None:
    cli_app()


if __name__ == "__main__":
    cli()
