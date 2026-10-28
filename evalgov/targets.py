"""Targets return raw response dictionaries. The engine validates them independently."""
import ipaddress
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Protocol

from .models import Case


class Target(Protocol):
    name: str
    synthetic: bool

    def invoke(self, case: Case) -> dict[str, Any]: ...


class FixtureTarget:
    synthetic = True

    def __init__(self, path: str | Path):
        self.name = "fixture:" + Path(path).name
        self.answers = json.loads(Path(path).read_text())

    def invoke(self, case: Case) -> dict[str, Any]:
        # Expected labels never passed to producers. Fixtures are authored separately.
        return self.answers[case.id]


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("Target redirects are forbidden")


class HttpTarget:
    synthetic = False

    def __init__(self, endpoint: str, token: str, timeout: float = 15):
        parsed = urllib.parse.urlsplit(endpoint)
        if parsed.username or parsed.password or parsed.fragment or not parsed.hostname:
            raise ValueError("Invalid endpoint")
        loopback = parsed.hostname == "localhost"
        try:
            loopback = loopback or ipaddress.ip_address(parsed.hostname).is_loopback
        except ValueError:
            pass
        if parsed.scheme != "https" and not (parsed.scheme == "http" and loopback):
            raise ValueError("Use HTTPS or an explicitly configured loopback HTTP endpoint")
        if not token or timeout <= 0 or timeout > 60:
            raise ValueError("A token and timeout in (0, 60] are required")
        self.endpoint, self.token, self.timeout = endpoint, token, timeout
        # No host/query in report name; configuration URLs can contain sensitive data.
        self.name = "http:configured-target"

    def invoke(self, case: Case) -> dict[str, Any]:
        body = {"case_id": case.id, "prompt": case.prompt,
                "documents": [d.model_dump() for d in case.documents]}
        request = urllib.request.Request(self.endpoint, data=json.dumps(body).encode(),
            headers={"Authorization": "Bearer " + self.token,
                     "Content-Type": "application/json"}, method="POST")
        # No automatic retries: evaluation shouldn't hide target reliability failures.
        with urllib.request.build_opener(NoRedirect).open(request, timeout=self.timeout) as response:
            raw = response.read(1_000_001)
            if len(raw) > 1_000_000:
                raise ValueError("Target response exceeds 1 MB")
            return json.loads(raw)


class TimedTarget:
    """Utility for integrations that need timing outside of the evaluation loop."""
    @staticmethod
    def call(target: Target, case: Case):
        start = time.perf_counter()
        result = target.invoke(case)
        return result, (time.perf_counter() - start) * 1000
