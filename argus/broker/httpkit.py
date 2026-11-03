"""One HTTP request, measured the way a differential needs it.

`curl` would do for a single request. What a tester actually needs is the same
request issued twice with one thing changed, and a comparison that says whether
the difference is real: status, length, timing, and how much of the body moved.
Those four together are what separates a SQL injection from a slow endpoint and
a WAF page from an error page, so they live in one place rather than being
re-derived in every tool.

Standard library only, deliberately: `requests` is not installed on a stock Kali
Python 3.14, and an engagement should not fail on a pip install.
"""
from __future__ import annotations

import difflib
import gzip
import json as jsonlib
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
import zlib
from dataclasses import dataclass, field

DEFAULT_UA = "argus/0.1 (authorized security testing)"
BODY_KEEP = 40_000


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class RedirectRefused(urllib.error.URLError):
    """A redirect pointed somewhere the caller does not allow."""


class _ScopedRedirect(urllib.request.HTTPRedirectHandler):
    """Follow redirects, but re-check every hop.

    A redirect is a NEW target. Following one without re-checking is a scope
    bypass with no exploit required: an in-scope host answers `302` to anywhere
    and the request goes there under the engagement's authority. So a caller that
    wants redirects followed must say which destinations are allowed, and the
    default allows none of them — `follow=True` with no `allow` predicate is
    refused rather than silently trusted.
    """

    def __init__(self, allow=None, limit: int = 5):
        self.allow = allow
        self.limit = limit
        self.followed: list[str] = []

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if len(self.followed) >= self.limit:
            raise RedirectRefused(f"redirect limit of {self.limit} reached at {newurl}")
        if self.allow is None or not self.allow(newurl):
            raise RedirectRefused(
                f"refused to follow a redirect to {newurl}: it is not in the engagement scope")
        self.followed.append(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


@dataclass
class HttpResponse:
    url: str
    method: str
    status: int | None
    headers: dict = field(default_factory=dict)
    body: str = ""
    length: int = 0
    time_ms: int = 0
    final_url: str = ""
    error: str | None = None
    request_headers: dict = field(default_factory=dict)
    request_body: str | None = None

    @property
    def ok(self) -> bool:
        return self.status is not None

    def header(self, name: str) -> str:
        return self.headers.get(name.lower(), "")

    def to_evidence(self, keep: int = 4000) -> dict:
        return {
            "request": {"method": self.method, "url": self.url,
                        "headers": self.request_headers, "body": self.request_body},
            "response": {"status": self.status, "headers": self.headers,
                         "body_span": self.body[:keep], "length": self.length,
                         "time_ms": self.time_ms, "final_url": self.final_url,
                         "error": self.error},
        }

    def summary(self) -> str:
        if self.error and self.status is None:
            return f"{self.method} {self.url} -> transport error: {self.error}"
        location = self.header("location")
        return (f"{self.method} {self.url} -> {self.status} {self.length}B {self.time_ms}ms"
                + (f" location={location}" if location else ""))


def _context(verify: bool) -> ssl.SSLContext:
    context = ssl.create_default_context()
    if not verify:
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
    return context


def _decode(raw: bytes, encoding: str) -> str:
    try:
        if encoding == "gzip":
            raw = gzip.decompress(raw)
        elif encoding == "deflate":
            raw = zlib.decompress(raw, -zlib.MAX_WBITS)
    except (OSError, zlib.error):
        pass
    return raw.decode("utf-8", "replace")


def request(method: str, url: str, headers: dict | None = None, params: dict | None = None,
            data: str | bytes | None = None, json_body: dict | None = None,
            cookies: str | None = None, timeout: int = 15, follow: bool = False,
            verify: bool = False, proxy: str | None = None,
            keep: int = BODY_KEEP, allow=None, max_redirects: int = 5) -> HttpResponse:
    method = method.upper()
    if params:
        split = urllib.parse.urlsplit(url)
        existing = urllib.parse.parse_qsl(split.query, keep_blank_values=True)
        merged = existing + [(k, str(v)) for k, v in params.items()]
        url = urllib.parse.urlunsplit(split._replace(
            query=urllib.parse.urlencode(merged, quote_via=urllib.parse.quote)))
    send_headers = {"User-Agent": DEFAULT_UA, "Accept": "*/*", "Connection": "close"}
    if cookies:
        send_headers["Cookie"] = cookies
    if json_body is not None:
        data = jsonlib.dumps(json_body)
        send_headers["Content-Type"] = "application/json"
    for key, value in (headers or {}).items():
        send_headers[str(key)] = str(value)
    payload = data.encode() if isinstance(data, str) else data

    handlers: list = [_NoRedirect()] if not follow else [_ScopedRedirect(allow, max_redirects)]
    handlers.append(urllib.request.HTTPSHandler(context=_context(verify)))
    if proxy:
        handlers.append(urllib.request.ProxyHandler({"http": proxy, "https": proxy}))
    else:
        handlers.append(urllib.request.ProxyHandler({}))
    opener = urllib.request.build_opener(*handlers)

    attempt = urllib.request.Request(url, data=payload, headers=send_headers, method=method)
    started = time.monotonic()
    try:
        with opener.open(attempt, timeout=timeout) as response:
            raw = response.read()
            elapsed = int((time.monotonic() - started) * 1000)
            head = {k.lower(): v for k, v in response.headers.items()}
            body = _decode(raw, head.get("content-encoding", ""))
            return HttpResponse(url, method, response.status, head, body[:keep], len(raw), elapsed,
                                response.geturl(), None, send_headers,
                                payload.decode("utf-8", "replace") if payload else None)
    except urllib.error.HTTPError as error:                 # 4xx/5xx and blocked redirects
        raw = error.read() if hasattr(error, "read") else b""
        elapsed = int((time.monotonic() - started) * 1000)
        head = {k.lower(): v for k, v in (error.headers or {}).items()}
        body = _decode(raw, head.get("content-encoding", ""))
        return HttpResponse(url, method, error.code, head, body[:keep], len(raw), elapsed,
                            error.geturl() if hasattr(error, "geturl") else url, None,
                            send_headers, payload.decode("utf-8", "replace") if payload else None)
    except urllib.error.URLError as error:
        elapsed = int((time.monotonic() - started) * 1000)
        reason = str(getattr(error, "reason", error))
        # A refused redirect is not an error: it is the measurement.
        return HttpResponse(url, method, None, {}, "", 0, elapsed, url, reason, send_headers,
                            payload.decode("utf-8", "replace") if payload else None)
    except (TimeoutError, OSError, ValueError) as error:
        elapsed = int((time.monotonic() - started) * 1000)
        return HttpResponse(url, method, None, {}, "", 0, elapsed, url, str(error), send_headers,
                            payload.decode("utf-8", "replace") if payload else None)


@dataclass
class Differential:
    status_changed: bool
    length_delta: int
    time_delta_ms: int
    body_similarity: float
    changed_lines: list[str] = field(default_factory=list)
    verdict: str = ""

    def to_dict(self) -> dict:
        return {"status_changed": self.status_changed, "length_delta": self.length_delta,
                "time_delta_ms": self.time_delta_ms,
                "body_similarity": round(self.body_similarity, 4),
                "changed_lines": self.changed_lines[:12], "verdict": self.verdict}


def compare(baseline: HttpResponse, variant: HttpResponse, similarity_floor: float = 0.98,
            length_floor: int = 24) -> Differential:
    """Is the difference between two responses real, or is it noise?

    The thresholds are deliberately conservative. A page with a CSRF token or a
    timestamp differs on every request, which is exactly how an automated tester
    talks itself into a finding, so a difference under the floors is reported as
    noise and the caller is told to take a second baseline.
    """
    similarity = difflib.SequenceMatcher(
        None, baseline.body[:20_000], variant.body[:20_000]).ratio() if (baseline.body or variant.body) else 1.0
    length_delta = (variant.length or 0) - (baseline.length or 0)
    status_changed = baseline.status != variant.status
    changed = [line for line in difflib.unified_diff(
        baseline.body.splitlines()[:400], variant.body.splitlines()[:400],
        lineterm="", n=0) if line.startswith(("+", "-")) and not line.startswith(("+++", "---"))]
    if status_changed:
        verdict = "status changed: a real difference"
    elif abs(length_delta) >= length_floor and similarity < similarity_floor:
        verdict = "body changed materially"
    elif similarity < similarity_floor:
        verdict = "body changed slightly; take a second baseline before believing it"
    else:
        verdict = "no material difference"
    return Differential(status_changed, length_delta,
                        (variant.time_ms or 0) - (baseline.time_ms or 0), similarity,
                        changed, verdict)


def reflection_context(body: str, token: str) -> list[str]:
    """Where a token landed, in parse-context terms. A payload list is useless
    without this: the characters that matter depend only on the context."""
    if not token or token not in body:
        return []
    contexts = []
    for index in _positions(body, token):
        window = body[max(0, index - 200): index + 200]
        before = body[:index]
        in_script = before.rfind("<script") > before.rfind("</script")
        in_comment = before.rfind("<!--") > before.rfind("-->")
        in_attr = False
        tag_open = before.rfind("<")
        if tag_open != -1 and before.rfind(">") < tag_open:
            in_attr = "=" in before[tag_open:]
        if in_script:
            quoted = (before.count("'") - before.count("\\'")) % 2 == 1 or \
                     (before.count('"') - before.count('\\"')) % 2 == 1
            contexts.append("script-string" if quoted else "script-body")
        elif in_comment:
            contexts.append("html-comment")
        elif in_attr:
            contexts.append("attribute-value")
        elif "href=" in window or "src=" in window:
            contexts.append("url-context")
        else:
            contexts.append("html-body")
    return sorted(set(contexts))


def _positions(text: str, token: str) -> list[int]:
    out, start = [], 0
    while len(out) < 8:
        index = text.find(token, start)
        if index == -1:
            break
        out.append(index)
        start = index + len(token)
    return out
