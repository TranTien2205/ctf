"""Guarded HTTP client: scope + rate limit + transcript recording.

Every tool sends through GuardedClient.send(); nothing else in the codebase
opens a socket to the target.
"""
from __future__ import annotations

import threading
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
        proxy: str = "",
    ):
        self.scope = scope
        self.session = session
        self.rate = rate_limiter
        self.max_requests = max_requests
        self.agent = agent
        self.sent = 0
        self._tls_verify = tls_verify
        # probe_race fires concurrent sends through one client - the budget
        # check+increment must be atomic or threads lose count
        self._sent_lock = threading.Lock()
        # Operator-level proxy (--proxy): routes target traffic through an
        # intercepting proxy such as Burp/ZAP for live inspection. This is
        # NOT reachable by the model - external-tool proxy flags stay
        # refused in the arg guards.
        self._client = httpx.Client(
            verify=tls_verify,
            follow_redirects=False,
            timeout=httpx.Timeout(15.0, connect=8.0),
            headers=default_headers or {},
            proxy=proxy or None,
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
        self.rate.wait()
        with self._sent_lock:
            if self.sent >= self.max_requests:
                raise RequestBudgetExhausted(
                    f"request budget exhausted ({self.max_requests}); "
                    "call finish"
                )
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
                with self._sent_lock:
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

    def send_raw(
        self,
        url: str,
        requests: list[dict],
        tool: str = "http_request",
        note: str = "",
    ) -> dict:
        """Raw HTTP/1.1 sends on ONE connection - for probes httpx cannot
        express (duplicate/conflicting headers like CL+TE). The socket,
        request budget, rate limiter and transcript all go through the same
        guards as send(); the URL's own Host is always emitted so headers
        cannot retarget the wire.

        requests: [{"method","headers":[[k,v],...],"body":bytes}, ...]"""
        import http.client
        parsed = self.scope.check(url)
        path = parsed.path or "/"
        if parsed.query:
            path += "?" + parsed.query
        host_port = f"{parsed.hostname}:{parsed.port}" if parsed.port \
            else parsed.hostname
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        if parsed.scheme == "https":
            import ssl
            sctx = ssl.create_default_context()
            if not self._tls_verify:
                sctx.check_hostname = False
                sctx.verify_mode = ssl.CERT_NONE
            conn: http.client.HTTPConnection = http.client.HTTPSConnection(
                parsed.hostname, port, timeout=15, context=sctx)
        else:
            conn = http.client.HTTPConnection(parsed.hostname, port,
                                              timeout=15)
        sends_out: list[dict] = []
        try:
            conn.connect()
            for spec in requests:
                method = (spec.get("method") or "GET").upper()
                lines = [f"{method} {path} HTTP/1.1",
                         f"Host: {host_port}",
                         "Connection: keep-alive",
                         f"User-Agent: argus-raw/1.0"]
                for k, v in spec.get("headers") or []:
                    if k.lower() in ("host",):
                        continue  # Host comes from the scoped URL only
                    lines.append(f"{k}: {v}")
                body = spec.get("body") or b""
                if isinstance(body, str):
                    body = body.encode()
                raw_req = ("\r\n".join(lines) + "\r\n\r\n").encode() + body
                self.rate.wait()
                with self._sent_lock:
                    if self.sent >= self.max_requests:
                        raise RequestBudgetExhausted(
                            f"request budget exhausted ({self.max_requests}); "
                            "call finish")
                    self.sent += 1
                started = time.monotonic()
                status, rheaders, rbody, error = 0, {}, "", None
                try:
                    # sock-level send + HTTPResponse: the connection's own
                    # state machine only understands well-formed requests
                    conn.sock.sendall(raw_req)
                    resp = http.client.HTTPResponse(
                        conn.sock, method=method)
                    resp.begin()
                    # the full body MUST be drained or its bytes corrupt
                    # the next response's parse on this reused connection
                    rbody = resp.read().decode("utf-8", "replace")[:BODY_CAP]
                    status = resp.status
                    rheaders = dict(resp.getheaders())
                except (http.client.HTTPException, OSError) as exc:
                    error = f"{type(exc).__name__}: {exc}"
                elapsed = round((time.monotonic() - started) * 1000, 1)
                rid = self.session.record_exchange(
                    tool=tool,
                    request={"method": method, "url": url,
                             # a dict collapses duplicate headers - and a
                             # duplicated/conflicting header pair IS the
                             # evidence here - so keep the wire text too
                             "headers": {l.split(": ", 1)[0]: l.split(": ", 1)[1]
                                         for l in lines[1:]},
                             "raw": True,
                             "request_text": raw_req.decode(
                                 "utf-8", "replace")[:4000],
                             "body": body.decode("utf-8", "replace")},
                    response={"status": status, "headers": rheaders,
                              "body": rbody, "elapsed_ms": elapsed},
                    note=note or "raw send", agent=self.agent)
                entry = {"request_id": rid, "status": status,
                         "elapsed_ms": elapsed, "body": rbody[:RETURN_CAP]}
                if error:
                    entry["error"] = error
                sends_out.append(entry)
                if error:
                    break
        finally:
            try:
                conn.close()
            except Exception:
                pass
        return {"sends": sends_out,
                "note": "raw sends share one connection - order matters" if len(sends_out) > 1 else ""}

    def close(self) -> None:
        self._client.close()
