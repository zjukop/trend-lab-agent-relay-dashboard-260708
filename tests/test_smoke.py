from fastapi.testclient import TestClient

from agent_relay_dashboard.main import app, run_relay


def test_health() -> None:
    client = TestClient(app)
    assert client.get("/health").json() == {"status": "ok"}


def test_run_relay_returns_agents() -> None:
    runs = run_relay("write tests")
    assert len(runs) == 4
    assert {run.status for run in runs} == {"passed"}
