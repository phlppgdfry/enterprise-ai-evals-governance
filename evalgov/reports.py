import html
import json
from pathlib import Path


def render_html(report: dict) -> str:
    def esc(value):
        return html.escape(str(value))
    rows = "".join("<tr><td>" + esc(row["id"]) + "</td><td>" + esc(row["category"])
                   + "</td><td>" + ("PASS" if row["passed"] else "FAIL")
                   + "</td><td>" + esc(", ".join(k for k, v in row["checks"].items() if not v))
                   + "</td><td>" + esc(row["latency_ms"]) + "</td><td>"
                   + esc(row["estimated_cost_usd"]) + "</td></tr>" for row in report["results"])
    return """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>AI evaluation evidence</title><style>body{font:16px system-ui;margin:3rem auto;max-width:1050px;padding:0 1rem;color:#183241;background:#f4f7f8}table{border-collapse:collapse;width:100%;background:white}td,th{text-align:left;padding:12px;border-bottom:1px solid #ccd7da}code{overflow-wrap:anywhere}.badge{font-weight:bold;color:#146453}h1{font-size:2.4rem}small{color:#52636a}</style>
<p>ENTERPRISE AI · EVALUATION EVIDENCE</p><h1>Release gate: """ + ("PASS" if report["summary"]["passed"] else "FAIL") + "</h1><p class=badge>" + esc(report["target"]) + " · " + ("SYNTHETIC FIXTURE — no model quality claim" if report["synthetic_target"] else "HTTP target — heuristic checks") + "</p><p>Run <code>" + esc(report["run_id"]) + "</code><br>Dataset <code>" + esc(report["dataset_sha256"]) + "</code></p><p>Pass rate: " + esc(round(report["summary"]["pass_rate"] * 100, 2)) + "% · Regression: " + esc(report["summary"]["regression"]) + "</p><table><thead><tr><th>Case</th><th>Category</th><th>Result</th><th>Failed checks</th><th>Latency ms</th><th>Estimated USD</th></tr></thead><tbody>" + rows + "</tbody></table><p><small>String/citation/contract assertions cannot establish factual truth, legal compliance, semantic groundedness or complete prompt-injection resistance. Costs use reported tokens and configured rates. Latency is measured by this runner.</small></p></html>"


def write_report(report: dict, directory: str | Path) -> None:
    destination = Path(directory)
    destination.mkdir(parents=True, exist_ok=True)
    # Constant filenames in caller-selected local directory; no paths from target input.
    (destination / "report.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    (destination / "report.html").write_text(render_html(report))
