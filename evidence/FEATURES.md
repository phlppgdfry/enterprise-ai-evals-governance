# Feature evidence matrix — 29 October 2026

Status vocabulary: **VERIFIED** means the stated local behavior was executed; **IMPLEMENTED BUT NOT VERIFIED** means code/artifacts exist without live acceptance; **MOCKED** means a deliberately substituted external effect; **DOCUMENTED ONLY** is a design/runbook; **PLANNED** is future work. Local tests do not prove production safety, real customer use or legal compliance.

Verification commands and results are in [verification-2026-10-29.json](verification-2026-10-29.json). Original 28 October evidence is retained as historical evidence. The pinned dependency audit reports no known advisories at scan time, not absence of all vulnerabilities. Request logs omit bodies, query strings and credentials.

| Feature | Status | Evidence / limitation |
|---|---|---|
| Strict checks, safety gates, compatible baselines, roles | VERIFIED | tests/test_engine.py; tests/test_api.py |
| RAG/workflow API adapters and four-case RAG dataset | VERIFIED | playbook portfolio/integration-result.json embeds actual evaluation reports |
| Evaluation dashboard/control runs | VERIFIED | playbook portfolio/browser-qa.json; screenshots/desktop.png |
| Good/unsafe response datasets and token usage | MOCKED | authored fixtures; not model benchmarks |
| HTTP target transport | VERIFIED | tests/test_http.py; explicit configured target protocol |
| Semantic groundedness, calibrated risk, live model comparison | PLANNED | substring/citation checks are deterministic heuristics |
| Governance policy advice | VERIFIED | policy API never grants execution authority |
| Multi-tenant evaluation service | PLANNED | current application intentionally single organization |
