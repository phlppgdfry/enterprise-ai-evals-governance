import copy
import json
import time

import pytest

from evalgov.api import ROOT
from evalgov.cli import main
from evalgov.engine import evaluate, load_dataset
from evalgov.models import Answer, Thresholds
from evalgov.reports import render_html
from evalgov.targets import FixtureTarget, HttpTarget


def run(fixture="good", **kwargs):
    cases, fingerprint = load_dataset(ROOT / "datasets/synthetic-v1.jsonl")
    return evaluate(cases, fingerprint, FixtureTarget(ROOT / f"datasets/responses-{fixture}.json"), **kwargs)


def test_good_fixture_passes_and_is_labeled_synthetic():
    result = run()
    assert result["summary"]["passed"]
    assert result["summary"]["cases"] == 16
    assert result["synthetic_target"] is True
    assert result["summary"]["total_estimated_cost_usd"] == pytest.approx(0.00288)


def test_unsafe_blocks_even_when_quality_threshold_is_zero():
    report = run("unsafe", thresholds=Thresholds(min_pass_rate=0))
    assert not report["summary"]["passed"]
    assert {"tool_safety", "refusal", "citations", "pii", "no_forbidden_terms", "answer_terms"} <= set(report["summary"]["failed_checks"])


def test_regression_gate_uses_same_dataset_only():
    baseline = run()
    result = run("unsafe", baseline=baseline)
    assert result["summary"]["regression"] > 0
    baseline["dataset_sha256"] = "different"
    with pytest.raises(ValueError, match="hash"):
        run(baseline=baseline)


def test_wrong_schema_and_timeout_fail_closed_without_logging_sensitive_exception():
    cases, fingerprint = load_dataset(ROOT / "datasets/synthetic-v1.jsonl")
    class Bad:
        name, synthetic = "broken", False
        def invoke(self, case):
            raise TimeoutError("SECRET-CREDENTIAL")
    report = evaluate(cases[:1], fingerprint, Bad())
    assert not report["summary"]["passed"]
    assert "SECRET-CREDENTIAL" not in json.dumps(report)
    assert report["results"][0]["error"] == "TimeoutError"


def test_tokens_cannot_be_negative_or_nan():
    with pytest.raises(ValueError):
        Thresholds(max_cost_usd=float("nan"))
    answer = {"answer": "x", "citations": [], "refused": False, "tool_calls": [], "usage": {"input_tokens": -1, "output_tokens": 1}}
    with pytest.raises(ValueError):
        Answer.model_validate(answer)


def test_cost_and_latency_budget_fail():
    assert not run(thresholds=Thresholds(max_cost_usd=0))["summary"]["passed"]
    assert not run(thresholds=Thresholds(max_cost_usd=0, min_pass_rate=0))["summary"]["passed"]
    cases, fingerprint = load_dataset(ROOT / "datasets/synthetic-v1.jsonl")
    fixture = FixtureTarget(ROOT / "datasets/responses-good.json")
    class Slow:
        name, synthetic = "slow", True
        def invoke(self, case):
            time.sleep(0.005)
            return fixture.invoke(case)
    report = evaluate(cases[:1], fingerprint, Slow(), Thresholds(max_latency_ms=1))
    assert not report["results"][0]["checks"]["latency"]


def test_duplicate_dataset_ids_rejected(tmp_path):
    line = (ROOT / "datasets/synthetic-v1.jsonl").read_text().splitlines()[0]
    path = tmp_path / "duplicate.jsonl"
    path.write_text(line + "\n" + line)
    with pytest.raises(ValueError, match="unique"):
        load_dataset(path)


def test_cli_exit_codes_and_reports(tmp_path):
    args = ["--out", str(tmp_path / "out"), "--db", str(tmp_path / "db")]
    assert main(["--fixture", "good", *args]) == 0
    assert (tmp_path / "out/report.html").is_file()
    assert main(["--fixture", "unsafe", *args]) == 1
    assert main(["--dataset", str(tmp_path / "missing"), *args]) == 2


def test_html_escapes_untrusted_case_ids():
    report = run()
    report["results"][0]["id"] = "<script>alert(1)</script>"
    assert "<script>" not in render_html(report)


@pytest.mark.parametrize("endpoint", ["http://example.com/eval", "file:///etc/passwd", "https://u:p@example.com", "https://example.com/#secret"])
def test_http_target_rejects_unsafe_configuration(endpoint):
    with pytest.raises(ValueError):
        HttpTarget(endpoint, "token")
