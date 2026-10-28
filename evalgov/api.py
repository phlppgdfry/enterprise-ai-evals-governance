import hmac
import json
import os
import threading
from pathlib import Path
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.security import APIKeyHeader
from pydantic import Field

from .engine import evaluate, load_dataset
from .models import PolicyRequest, StrictModel, Thresholds
from .policy import decide
from .reports import render_html
from .store import Store
from .targets import FixtureTarget, HttpTarget

ROOT = Path(__file__).resolve().parent


class RunRequest(StrictModel):
    fixture: Literal["good", "unsafe", "http"] = "good"
    baseline_run_id: str | None = Field(default=None, max_length=100)
    thresholds: Thresholds = Field(default_factory=Thresholds)


def create_app(db_path: str | None = None, principals: dict | None = None) -> FastAPI:
    app = FastAPI(title="Enterprise AI Evaluation & Governance", version="0.1.0")
    store = Store(db_path or os.getenv("EVALGOV_DB", "var/evalgov.sqlite3"))
    configured = principals if principals is not None else json.loads(os.getenv("EVALGOV_PRINCIPALS", "{}"))
    if not isinstance(configured, dict) or any(
        not isinstance(key, str) or len(key) < 16 or not isinstance(value, dict)
        or value.get("role") not in {"reader", "evaluator", "governor"}
        or not isinstance(value.get("name"), str) for key, value in configured.items()
    ):
        raise ValueError("Principals require >=16-character tokens, a name and reader/evaluator/governor role")
    key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
    run_lock = threading.Lock()

    def authenticate(key: Annotated[str | None, Depends(key_header)]):
        for token, principal in configured.items():
            if key and hmac.compare_digest(key.encode("utf-8"), token.encode("utf-8")):
                return principal
        raise HTTPException(status_code=401, detail="Valid API key required", headers={"WWW-Authenticate": "APIKey"})

    def require(*roles):
        def check(principal: Annotated[dict, Depends(authenticate)]):
            if principal["role"] not in roles:
                raise HTTPException(status_code=403, detail="Role does not permit this operation")
            return principal
        return check

    @app.get("/health")
    def health():
        return {"status": "ok", "mode": "portfolio-reference", "auth_configured": bool(configured)}

    @app.post("/runs")
    def run(request: RunRequest, principal: Annotated[dict, Depends(require("evaluator", "governor"))]):
        # Single-process admission control. Production requires a durable distributed queue.
        if not run_lock.acquire(blocking=False):
            raise HTTPException(status_code=429, detail="An evaluation is already running")
        try:
            cases, fingerprint = load_dataset(ROOT / "datasets/synthetic-v1.jsonl")
            baseline = store.get(request.baseline_run_id) if request.baseline_run_id else None
            if request.baseline_run_id and baseline is None:
                raise HTTPException(status_code=404, detail="Baseline run not found")
            if request.fixture == "http":
                endpoint, token = os.getenv("EVALGOV_TARGET_URL"), os.getenv("EVALGOV_TARGET_TOKEN")
                if not endpoint or not token:
                    raise HTTPException(status_code=503, detail="HTTP target is not configured")
                try:
                    target = HttpTarget(endpoint, token)
                except ValueError:
                    raise HTTPException(status_code=503, detail="HTTP target configuration is invalid") from None
            else:
                target = FixtureTarget(ROOT / f"datasets/responses-{request.fixture}.json")
            try:
                report = evaluate(cases, fingerprint, target, request.thresholds, baseline)
            except ValueError:
                raise HTTPException(status_code=409, detail="Baseline cannot be compared with this dataset") from None
            store.save(report, principal["name"])
            return report
        finally:
            run_lock.release()

    @app.get("/runs")
    def list_runs(principal: Annotated[dict, Depends(authenticate)]):
        return store.list_runs()

    @app.get("/runs/{run_id}")
    def get_run(run_id: str, principal: Annotated[dict, Depends(authenticate)]):
        report = store.get(run_id)
        if report is None:
            raise HTTPException(status_code=404, detail="Run not found")
        return report

    @app.get("/runs/{run_id}/report", response_class=HTMLResponse)
    def html_report(run_id: str, principal: Annotated[dict, Depends(authenticate)]):
        return render_html(get_run(run_id, principal))

    @app.post("/policy/decide")
    def policy(request: PolicyRequest, principal: Annotated[dict, Depends(require("governor"))]):
        result = decide(request)
        # Do not log caller-supplied use-case text or owner fields, which may contain personal data.
        store.record(principal["name"], "policy_decision", result["decision"])
        return result

    @app.get("/audit")
    def audit(principal: Annotated[dict, Depends(require("governor"))]):
        return store.audit()

    return app
