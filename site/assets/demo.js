// The two committed evaluation runs (evidence/good and evidence/unsafe report.json), same 16-case dataset.
const $ = id => document.getElementById(id);
const runs = await (await fetch('assets/runs.json')).json();
const CHECKS = ['schema', 'answer_terms', 'citations', 'refusal', 'pii', 'no_forbidden_terms', 'tool_safety', 'latency', 'cost'];
const LABEL = { schema: 'schema', answer_terms: 'answer terms', citations: 'citations', refusal: 'refusal', pii: 'PII', no_forbidden_terms: 'canaries', tool_safety: 'tool args', latency: 'latency', cost: 'cost' };
function show(k) {
  const r = runs[k], s = r.summary;
  document.querySelectorAll('#eg-runs button').forEach(b => b.setAttribute('aria-selected', b.dataset.r === k));
  $('eg-verdict').innerHTML = `<span class="pill ${s.passed ? 'ok' : 'bad'}">${s.passed ? 'RELEASE GATE PASSED · exit 0' : 'RELEASE GATE FAILED · exit 1'}</span>`;
  const t = (v, l, c = '') => `<div class="kpi-tile ${c}"><div class="v">${v}</div><div class="l">${l}</div></div>`;
  $('eg-tiles').innerHTML = t(Math.round(s.pass_rate * 100) + '%', `pass rate over ${s.cases} cases (gate: ${r.thresholds.min_pass_rate * 100}%)`, 'big') +
    t(s.safety_failures, 'safety failures', s.safety_failures ? 'bad' : 'ok') +
    t(s.baseline_pass_rate == null ? '—' : Math.round(s.regression * 100) + ' pts', 'regression vs baseline', s.regression > 0 ? 'bad' : '') +
    t('$' + s.total_estimated_cost_usd.toFixed(4), 'estimated cost (budget $' + r.thresholds.max_cost_usd + ' per case)');
  $('eg-matrix').innerHTML = `<tr><th>Case</th><th>Category</th>${CHECKS.map(c => `<th>${LABEL[c]}</th>`).join('')}<th>Result</th></tr>` +
    r.results.map(x => `<tr class="${x.passed ? '' : 'eg-fail'}"><td class="mono">${x.id}</td><td>${x.category}</td>${CHECKS.map(c => `<td class="eg-c ${x.checks[c] ? 'y' : 'n'}">${x.checks[c] ? '✓' : '✗'}</td>`).join('')}<td><span class="pill ${x.passed ? 'ok' : 'bad'}">${x.passed ? 'pass' : 'fail'}</span></td></tr>`).join('');
}
$('eg-runs').addEventListener('click', e => { const b = e.target.closest('button'); if (b) show(b.dataset.r); });
show('unsafe');
