"""Guarded HTTP client: scope + rate limit + transcript recording.

Every tool sends through GuardedClient.send(); nothing else in the codebase
opens a socket to the target.
"""
from __future__ import annotations

import time
import urllib.parse

import httpx

from .ratelimit import RateLimiter
from .scope import ScopeGuard
from .session import Session

BODY_CAP = 200_000  # bytes stored in transcript
RETURN_CAP = 12_000  # chars returned to the model


def _headers_dict(resp) -> dict:
    """dict(headers) collapses multi-value headers; Set-Cookie is the one
    whose values must stay separate (Expires dates carry commas, and
    fingerprint parses each cookie's flags)."""
    hdrs = dict(resp.headers)
    sc = resp.headers.get_list("set-cookie")
    if len(sc) > 1:
        hdrs["set-cookie"] = sc
    return hdrs


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
        chain: list[dict] = []
        blocked_to = ""
        # passing timeout=None to httpx builds Timeout(None) - an INFINITE
        # wait that overrides the client default; only pass it when set.
        tkw = {} if timeout is None else {"timeout": timeout}
        try:
            resp = self._client.request(
                method.upper(),
                url,
                headers=req_headers,
                content=body,
                follow_redirects=False,
                **tkw,
            )
            # Manual redirect following: letting httpx follow automatically
            # would skip the scope check on each Location - a 302 to a
            # foreign host must be refused like any other out-of-scope URL.
            hops = 0
            while (follow_redirects and hops < 8 and resp.status_code
                   in (301, 302, 303, 307, 308)):
                loc = resp.headers.get("location", "")
                if not loc:
                    break
                nxt = urllib.parse.urljoin(str(resp.url), loc)
                blocked_to = nxt
                self.scope.check(nxt)  # ScopeError -> recorded then raised
                chain.append({"from": str(resp.url), "to": nxt,
                              "status": resp.status_code})
                m2 = "GET" if resp.status_code in (301, 302, 303) \
                    else method.upper()
                b2 = None if m2 == "GET" else body
                self.rate.wait()  # each hop is a real request on the wire
                if self.sent >= self.max_requests:
                    chain[-1]["budget_exhausted"] = True
                    break
                self.sent += 1
                resp = self._client.request(
                    m2, nxt, headers=req_headers, content=b2,
                    follow_redirects=False, **tkw)
                hops += 1
            elapsed_ms = round((time.monotonic() - started) * 1000, 1)
            raw = resp.content[:BODY_CAP]
            try:
                text = raw.decode(resp.encoding or "utf-8", errors="replace")
            except (LookupError, TypeError):
                text = raw.decode("utf-8", errors="replace")
            response_data = {
                "status": resp.status_code,
                "headers": _headers_dict(resp),
                "body": text,
                "elapsed_ms": elapsed_ms,
                "final_url": str(resp.url),
                "truncated": len(resp.content) > BODY_CAP,
            }
            if chain:
                response_data["redirects"] = chain
        except httpx.HTTPError as exc:
            elapsed_ms = round((time.monotonic() - started) * 1000, 1)
            error = f"{type(exc).__name__}: {exc}"
            response_data = {"status": 0, "headers": {}, "body": "",
                             "elapsed_ms": elapsed_ms, "error": error}
        except Exception:
            # A scope refusal mid-chain must still be auditable: record the
            # last in-scope response so the transcript shows where the app
            # tried to send us, then let the error propagate.
            if resp is not None:
                try:
                    self.session.record_exchange(
                        tool=tool,
                        request={"method": method.upper(), "url": url,
                                 "headers": dict(resp.request.headers),
                                 "body": body.decode("utf-8", "replace")
                                 if isinstance(body, bytes) else body},
                        response={"status": resp.status_code,
                                  "headers": _headers_dict(resp),
                                  "body": resp.text[:BODY_CAP],
                                  "redirects": chain,
                                  "blocked_redirect": True,
                                  "blocked_to": blocked_to},
                        note="redirect blocked by scope guard",
                        agent=self.agent)
                except Exception:
                    pass
            raise

        # Record what the wire actually carried: httpx merges client-level
        # default headers and the cookie jar silently, so req_headers alone
        # would hide e.g. Authorization or session cookies from the audit.
        sent_headers = req_headers
        if resp is not None:
            try:
                sent_headers = dict(resp.request.headers)
            except Exception:
                pass

        rid = self.session.record_exchange(
            tool=tool,
            request={"method": method.upper(), "url": url,
                     "headers": sent_headers,
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
