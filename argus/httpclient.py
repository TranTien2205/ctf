"""Guarded HTTP client: scope + rate limit + transcript recording.

Every tool sends through GuardedClient.send(); nothing else in the codebase
opens a socket to the target.
"""
from __future__ import annotations

import time

import httpx

from .ratelimit import RateLimiter
from .scope import ScopeGuard
from .session import Session

BODY_CAP = 200_000  # bytes stored in transcript
RETURN_CAP = 12_000  # chars returned to the model


class RequestBudgetExhausted(RuntimeError):
    pass


class GuardedClient:
    def __init__(
        self,
        scope: ScopeGuard,
        session: Session,
        rate_limiter: RateLimiter,
        default_headers: dict[str, str] | None = None,
        tls_verify: bool = False,
        max_requests: int = 400,
        agent: str = "",
    ):
        self.scope = scope
        self.session = session
        self.rate = rate_limiter
        self.max_requests = max_requests
        self.agent = agent
        self.sent = 0
        self._client = httpx.Client(
            verify=tls_verify,
            follow_redirects=False,
            timeout=httpx.Timeout(15.0, connect=8.0),
            headers=default_headers or {},
        )

    def send(
        self,
        method: str,
        url: str,
        headers: dict[str, str] | None = None,
        body: str | bytes | None = None,
        follow_redirects: bool = False,
        tool: str = "http_request",
        note: str = "",
        timeout: float | None = None,
    ) -> dict:
        """Send one scoped request, record it, return a compact result."""
        self.scope.check(url)  # raises ScopeError before any byte is sent
        if self.sent >= self.max_requests:
            raise RequestBudgetExhausted(
                f"request budget exhausted ({self.max_requests}); call finish"
            )
        self.rate.wait()
        self.sent += 1

        req_headers = dict(headers or {})
        started = time.monotonic()
        error = None
        resp = None
        try:
            resp = self._client.request(
                method.upper(),
                url,
                headers=req_headers,
                content=body,
                follow_redirects=follow_redirects,
                timeout=timeout,
            )
            elapsed_ms = round((time.monotonic() - started) * 1000, 1)
            raw = resp.content[:BODY_CAP]
            try:
                text = raw.decode(resp.encoding or "utf-8", errors="replace")
            except (LookupError, TypeError):
                text = raw.decode("utf-8", errors="replace")
            response_data = {
                "status": resp.status_code,
                "headers": dict(resp.headers),
                "body": text,
                "elapsed_ms": elapsed_ms,
                "final_url": str(resp.url),
                "truncated": len(resp.content) > BODY_CAP,
            }
        except httpx.HTTPError as exc:
            elapsed_ms = round((time.monotonic() - started) * 1000, 1)
            error = f"{type(exc).__name__}: {exc}"
            response_data = {"status": 0, "headers": {}, "body": "",
                             "elapsed_ms": elapsed_ms, "error": error}

        rid = self.session.record_exchange(
            tool=tool,
            request={"method": method.upper(), "url": url,
                     "headers": req_headers,
                     "body": body.decode("utf-8", "replace") if isinstance(body, bytes) else body},
            response=response_data,
            note=note,
            agent=self.agent,
        )

        out = {
            "request_id": rid,
            "status": response_data["status"],
            "elapsed_ms": elapsed_ms,
            "headers": {k: v for k, v in response_data["headers"].items()},
            "body": response_data["body"][:RETURN_CAP],
        }
        if response_data.get("truncated"):
            out["body_truncated_at"] = BODY_CAP
        if response_data.get("final_url") and response_data["final_url"] != url:
            out["final_url"] = response_data["final_url"]
        if error:
            out["error"] = error
        return out

    def close(self) -> None:
        self._client.close()
