"""Adapters evaluate observed portfolio APIs, never expected answer fixtures."""
import json
import urllib.request
import urllib.error
from urllib.parse import quote

from .targets import HttpTarget, NoRedirect


class PortfolioTarget:
    # The application is called, but supplied content and local planner remain synthetic.
    synthetic = True

    def __init__(self, service, origin, token):
        if service not in {'rag', 'workflow'}:
            raise ValueError('Unknown portfolio service')
        HttpTarget(origin, token)  # Reuse explicit endpoint/TLS validation.
        from urllib.parse import urlsplit
        parsed = urlsplit(origin)
        if parsed.path not in ('', '/') or parsed.query:
            raise ValueError('Configure an origin, not an arbitrary target route')
        self.service, self.origin, self.token = service, origin.rstrip('/'), token
        self.name = 'portfolio-api:' + service + ':synthetic-data'

    def invoke(self, case):
        path = '/ask' if self.service == 'rag' else '/runs/' + quote(case.prompt, safe='')
        payload = json.dumps({'question': case.prompt, 'top': 4}).encode() if self.service == 'rag' else None
        request = urllib.request.Request(self.origin + path, data=payload,
            headers={'X-API-Key': self.token, 'Content-Type': 'application/json'})
        try:
            with urllib.request.build_opener(NoRedirect).open(request, timeout=10) as response:
                raw = response.read(1_000_001)
                if len(raw) > 1_000_000:
                    raise ValueError('Portfolio response too large')
                data = json.loads(raw)
        except urllib.error.HTTPError as exc:
            if self.service == 'workflow' and exc.code == 404:
                return self.answer('Run unavailable', [], True, [])
            raise
        if self.service == 'rag':
            return self.answer(data['answer'], sorted({c['document_id'] for c in data['citations']}),
                               data['abstained'], [], data.get('usage'))
        # Read-only observation: never advance/approve a run during evaluation.
        calls = [{'name': row['tool'], 'arguments': step['arguments']}
                 for row, step in zip(data['tool_results'], (data.get('plan') or {}).get('steps', []))]
        return self.answer(data['status'], [], False, calls)

    @staticmethod
    def answer(text, citations, refused, calls, usage=None):
        usage = usage or {}
        return {'answer': text, 'citations': citations, 'refused': refused, 'tool_calls': calls,
                'usage': {'input_tokens': usage.get('prompt_tokens', 0),
                          'output_tokens': usage.get('completion_tokens', 0)}}
