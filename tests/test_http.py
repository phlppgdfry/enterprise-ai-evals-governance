import json
import urllib.request

import pytest

from evalgov.api import ROOT
from evalgov.engine import evaluate, load_dataset
from evalgov.targets import FixtureTarget, HttpTarget, NoRedirect


def test_http_payload_does_not_include_expected_labels_and_uses_bearer(monkeypatch):
    cases, fingerprint = load_dataset(ROOT / "datasets/synthetic-v1.jsonl")
    fixture = FixtureTarget(ROOT / "datasets/responses-good.json")
    seen = []
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self, limit): return json.dumps(fixture.invoke(cases[0])).encode()
    class Opener:
        def open(self, request, timeout):
            seen.append((request, timeout))
            return Response()
    monkeypatch.setattr(urllib.request, "build_opener", lambda handler: Opener())
    target = HttpTarget("https://trusted.synthetic.invalid/evaluate", "test-token")
    report = evaluate(cases[:1], fingerprint, target)
    request, timeout = seen[0]
    payload = json.loads(request.data)
    assert set(payload) == {"case_id", "prompt", "documents"}
    assert "expected" not in payload
    assert request.get_header("Authorization") == "Bearer test-token"
    assert timeout == 15
    assert report["synthetic_target"] is False
    assert report["summary"]["passed"]


def test_redirect_and_oversized_response_fail_closed(monkeypatch):
    with pytest.raises(ValueError, match="redirect"):
        NoRedirect().redirect_request(None, None, 302, "", {}, "https://untrusted.invalid")
    cases, fingerprint = load_dataset(ROOT / "datasets/synthetic-v1.jsonl")
    class Response:
        def __enter__(self): return self
        def __exit__(self, *args): pass
        def read(self, limit): return b"x" * limit
    class Opener:
        def open(self, *args, **kwargs): return Response()
    monkeypatch.setattr(urllib.request, "build_opener", lambda handler: Opener())
    report = evaluate(cases[:1], fingerprint, HttpTarget("http://127.0.0.1:8080/eval", "test-token"))
    assert not report["summary"]["passed"]


def test_api_records_survive_recreating_application(tmp_path):
    from fastapi.testclient import TestClient
    from evalgov.api import create_app
    principals = {"long-enough-test-token": {"name": "test-runner", "role": "evaluator"}}
    headers = {"X-API-Key": "long-enough-test-token"}
    path = str(tmp_path / "persistent.db")
    run = TestClient(create_app(path, principals)).post("/runs", json={}, headers=headers).json()
    new_client = TestClient(create_app(path, principals))
    loaded = new_client.get("/runs/" + run["run_id"], headers=headers)
    assert loaded.json() == run
