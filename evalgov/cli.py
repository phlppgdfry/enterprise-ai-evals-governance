import argparse
import json
import os
import sys
from pathlib import Path

from .api import ROOT
from .engine import evaluate, load_dataset
from .models import Thresholds
from .reports import write_report
from .store import Store
from .targets import FixtureTarget, HttpTarget
from .portfolio import PortfolioTarget


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run contract and safety checks; exit 1 means release blocked.")
    parser.add_argument("--dataset", type=Path, default=ROOT / "datasets/synthetic-v1.jsonl")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--fixture", choices=["good", "unsafe"], default=None)
    group.add_argument("--http", metavar="ENDPOINT", help="Explicit trusted target; token comes from EVALGOV_TARGET_TOKEN")
    group.add_argument("--portfolio", choices=["rag", "workflow"], help="Observe actual portfolio APIs with synthetic data")
    parser.add_argument("--baseline", type=Path)
    parser.add_argument("--thresholds", type=Path)
    parser.add_argument("--out", type=Path, default=Path("reports/latest"))
    parser.add_argument("--db", default="var/evalgov.sqlite3")
    args = parser.parse_args(argv)
    try:
        cases, fingerprint = load_dataset(args.dataset)
        limits = Thresholds.model_validate_json(args.thresholds.read_text()) if args.thresholds else Thresholds()
        baseline = json.loads(args.baseline.read_text()) if args.baseline else None
        if args.portfolio:
            target = PortfolioTarget(args.portfolio, os.environ['EVALGOV_PORTFOLIO_ORIGIN'],
                                     os.environ['EVALGOV_TARGET_TOKEN'])
        else:
            target = (HttpTarget(args.http, os.getenv("EVALGOV_TARGET_TOKEN", "")) if args.http
                      else FixtureTarget(ROOT / f"datasets/responses-{args.fixture or 'good'}.json"))
        report = evaluate(cases, fingerprint, target, limits, baseline)
        write_report(report, args.out)
        Store(args.db).save(report, "local-cli")
        print(json.dumps({"run_id": report["run_id"], "synthetic_target": report["synthetic_target"], **report["summary"]}, indent=2))
        return 0 if report["summary"]["passed"] else 1
    except Exception as exc:
        print("Configuration or execution failure: " + type(exc).__name__, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
