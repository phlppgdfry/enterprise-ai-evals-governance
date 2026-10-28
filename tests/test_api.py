from fastapi.testclient import TestClient
import pytest

from evalgov.api import create_app
from evalgov.models import PolicyRequest
from evalgov.policy import decide

TOKENS = {"reader-token-for-tests": {"name": "reader", "role": "reader"},
          "evaluator-token-tests": {"name": "runner", "role": "evaluator"},
          "governor-token-tests": {"name": "owner", "role": "governor"}}


@pytest.fixture
def client(tmp_path):
    return TestClient(create_app(str(tmp_path / "state.sqlite3"), TOKENS))


def auth(role):
    return {"X-API-Key": next(key for key, principal in TOKENS.items() if principal["role"] == role)}


def test_authentication_and_role_cannot_be_spoofed(client):
    assert client.get("/runs").status_code == 401
    assert client.post("/runs", headers={**auth("reader"), "X-Role": "governor"}, json={}).status_code == 403
    assert client.post("/runs", headers=auth("evaluator"), json={"role": "governor"}).status_code == 422


def test_runs_persist_and_html_and_audit_work(client, tmp_path):
    response = client.post("/runs", headers=auth("evaluator"), json={})
    assert response.status_code == 200, response.text
    run_id = response.json()["run_id"]
    assert client.get(f"/runs/{run_id}", headers=auth("reader")).json()["summary"]["passed"]
    html = client.get(f"/runs/{run_id}/report", headers=auth("reader"))
    assert "SYNTHETIC FIXTURE" in html.text
    assert client.get("/audit", headers=auth("reader")).status_code == 403
    assert client.get("/audit", headers=auth("governor")).json()[0]["actor"] == "runner"


def test_missing_baseline_and_unconfigured_http_target(client, monkeypatch):
    monkeypatch.delenv("EVALGOV_TARGET_URL", raising=False)
    assert client.post("/runs", headers=auth("evaluator"), json={"baseline_run_id": "missing"}).status_code == 404
    assert client.post("/runs", headers=auth("evaluator"), json={"fixture": "http"}).status_code == 503


def test_baseline_gate_and_role_policy(client):
    baseline = client.post("/runs", headers=auth("evaluator"), json={}).json()
    unsafe = client.post("/runs", headers=auth("evaluator"), json={"fixture": "unsafe", "baseline_run_id": baseline["run_id"]}).json()
    assert not unsafe["summary"]["passed"]
    request = {"use_case": "invoice routing", "personal_data": True, "externally_visible_action": True,
               "financial_posting": True, "approved_data_source": True, "retention_days": 30, "owner": "finance"}
    assert client.post("/policy/decide", headers=auth("evaluator"), json=request).status_code == 403
    response = client.post("/policy/decide", headers=auth("governor"), json=request).json()
    assert response["human_approval_required"]
    assert not response["authorization_to_execute"]


def test_policy_blocks_unapproved_source_special_data_and_long_retention():
    result = decide(PolicyRequest(use_case="payroll demo", personal_data=True, special_category_data=True,
        externally_visible_action=False, approved_data_source=False, retention_days=100, owner="HR"))
    assert result["decision"] == "blocked"
    assert len(result["blockers"]) == 3


def test_default_empty_principals_fail_closed(tmp_path):
    client = TestClient(create_app(str(tmp_path / "empty.db"), {}))
    assert client.get("/health").json()["auth_configured"] is False
    assert client.get("/runs").status_code == 401


def test_no_short_or_misconfigured_api_keys(tmp_path):
    with pytest.raises(ValueError):
        create_app(str(tmp_path / "bad.db"), {"short": {"name": "root", "role": "governor"}})
