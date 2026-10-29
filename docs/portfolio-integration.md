# Evaluate actual portfolio applications

The adapter in `evalgov/portfolio.py` calls existing RAG and workflow APIs. It does not send expected labels or supplied dataset documents to the application. RAG citations are normalized to document IDs; workflow evaluation observes persisted tool receipts and never advances/approves runs.

```bash
export EVALGOV_PORTFOLIO_ORIGIN=http://127.0.0.1:8084
# Set EVALGOV_TARGET_TOKEN locally to a finance-only RAG key.
.venv/bin/python -m evalgov.cli --portfolio rag --dataset evalgov/datasets/portfolio-rag-v1.jsonl --out reports/rag
```

The authored four-case dataset checks policy retrieval, abstention, a forbidden HR canary and an instruction attempting to change permissions. These are deterministic checks on a tiny synthetic corpus, not general prompt-injection protection or semantic groundedness. Local extractive mode makes no model calls; zero tokens means no reported model use in that execution. Azure usage, if supplied, is counted separately using configured illustrative tariffs.

For workflow, supply a versioned dataset whose prompt is a known run ID and whose expected calls match the intended plan. The adapter permits only `GET /runs/{id}`. A 404 is normalized to refusal. A caller with no access must not use an all-tenant/admin credential. The orchestrated [playbook runner](https://github.com/phlppgdfry/ai-transformation-playbook) generates the synthetic run IDs and evaluates both actual APIs; its report preserves the dataset SHA-256.

Open `/console` for saved executed runs, positive/negative controls and per-case failures. Dashboard figures come from stored reports. No invented model comparisons are shown. Fixture latency is lookup time, not inference latency; costs use fictional token usage. The application remains one organization with a process-local evaluation lock.

The RAG repository additionally measures document-level precision@k, recall@k, reciprocal rank and nDCG on its reproducible corpus. This evaluation framework does not certify deployment safety or grant execution rights.
