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
from .scope import ScopeGuard, ScopeError, _ip_private
import ipaddress as _ipaddress
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


class _NoCloseFile:
    """fp proxy that swallows close() - several HTTPResponse objects share
    one buffered reader on a kept-alive connection, but every response
    calls fp.close() once its body is fully read (_close_conn). Without
    this shim the FIRST response's read would kill the reader for the
    rest of the reads."""

    def __init__(self, real):
        self._real = real

    def __getattr__(self, name):
        return getattr(self._real, name)

    def close(self):
        pass


# Headers whose VALUES are operator secrets, not assessment evidence.
# They ride every request silently (--header/--header-file), so persisting
# them verbatim would leak live credentials into transcript.jsonl and the
# shareable report. Evidence only cites response bodies/event output, so
# redaction cannot break a finding. Names stay visible - the audit still
# shows the request was authenticated.
_SENSITIVE_REQ_HEADERS = {
    "authorization", "proxy-authorization", "cookie", "x-api-key",
    "x-auth-token", "x-access-token", "x-csrf-token", "x-xsrf-token",
    "x-session-token", "x-amz-security-token",
}
_SENSITIVE_RESP_HEADERS = {"set-cookie"}
_REDACTED = "•••redacted•••"


def _redact_header_value(name: str, value: str) -> str:
    """Keep structure, drop secrets: Bearer scheme, cookie pair names and
    set-cookie attributes survive - the credential does not."""
    ln = name.lower()
    if ln == "authorization" or ln == "proxy-authorization":
        scheme = value.split(" ", 1)[0]
        return f"{scheme} {_REDACTED}" if " " in value else _REDACTED
    if ln in ("cookie", "set-cookie"):
        return "; ".join(
            p if "=" not in p else p.split("=", 1)[0] + "=" + _REDACTED
            for p in value.split("; "))
    return _REDACTED


def _redact_headers(headers: dict, secret_values: set[str]) -> dict:
    out = {}
    for k, v in (headers or {}).items():
        # model-built header dicts can carry non-str values (JSON arrays
        # are legal tool input) - coerce so redaction cannot crash the
        # record path and mask the real httpx error
        ks = k if isinstance(k, str) else str(k)
        vs = v if isinstance(v, str) else str(v)
        if ks.lower() in _SENSITIVE_REQ_HEADERS \
                or ks.lower() in _SENSITIVE_RESP_HEADERS \
                or vs in secret_values:
            out[ks] = _redact_header_value(ks, vs)
        else:
            out[ks] = vs
    return out


def _redact_request_text(text: str, secret_values: set[str]) -> str:
    """Raw wire text (send_raw) carries secrets inline - redact sensitive
    header lines while preserving the line structure that IS the smuggle
    evidence (e.g. duplicated/conflicting headers)."""
    out = []
    for line in text.split("\r\n"):
        if ": " in line:
            name, _, val = line.partition(": ")
            if name.lower() in _SENSITIVE_REQ_HEADERS \
                    or val in secret_values:
                line = name + ": " + _REDACTED
        out.append(line)
    return "\r\n".join(out)


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
        secret_values: list[str] | None = None,
    ):
        self.scope = scope
        self.session = session
        self.rate = rate_limiter
        self.max_requests = max_requests
        self.agent = agent
        self.sent = 0
        self._tls_verify = tls_verify
        # send_raw builds its wire text by hand, so it cannot inherit
        # httpx's client-level merge - keep the operator headers for it.
        self._default_headers = default_headers or {}
        # values >=8 chars are treated as operator secrets wherever they
        # appear in recorded headers, even under a custom header name;
        # --secret adds operator-declared values (login passwords posted
        # in bodies, tokens the agent quotes). User-Agent is excepted: it
        # is a public banner sent on every request, not a credential - and
        # a target echoing it back must not turn the evidence into
        # redaction noise.
        self._secret_values = {
            v for k, v in self._default_headers.items()
            if isinstance(v, str) and len(v) >= 8
            and str(k).lower() != "user-agent"} | {
                v for v in (secret_values or []) if len(v) >= 4}
        # the session redacts these values inside every artifact write -
        # bodies, event output, notes - not just headers
        if self._secret_values:
            self.session.secret_values |= self._secret_values
        # probe_race fires concurrent sends through one client - the budget
        # check+increment must be atomic or threads lose count
        self._sent_lock = threading.Lock()
        # Operator-level proxy (--proxy): routes target traffic through an
        # intercepting proxy such as Burp/ZAP for live inspection. This is
        # NOT reachable by the model - external-tool proxy flags stay
        # refused in the arg guards.
        def _capture(resp):
            # httpx materialises response.next_request even when we do not
            # follow redirects - a 30x to javascript:/data:/malformed
            # Location crashes inside client.request() and the response is
            # lost. Response hooks run BEFORE that step, so the box carried
            # in request extensions still gets the verbatim 30x.
            box = resp.request.extensions.get("_argus_box")
            if box is not None:
                box["resp"] = resp

        self._client = httpx.Client(
            verify=tls_verify,
            follow_redirects=False,
            timeout=httpx.Timeout(15.0, connect=8.0),
            headers=default_headers or {},
            proxy=proxy or None,
            event_hooks={"response": [_capture]},
            # target traffic must come only from declared inputs:
            # trust_env would let HTTP_PROXY silently re-route scoped
            # requests and let ~/.netrc auto-attach Basic credentials to
            # a matching target host. --proxy covers corp egress.
            trust_env=False,
        )

    def _fetch_capped(self, method: str, url: str,
                      req_headers: dict, body, tkw: dict,
                      box: dict) -> tuple:
        """One request via client.stream(): the body is read bounded at
        BODY_CAP, so a hostile or misconfigured target cannot exhaust
        memory by streaming an unbounded response - the old path pulled
        resp.content (full buffering) before slicing.
        Returns (resp, raw_bytes, truncated): resp is closed, but status/
        headers/url/request stay readable; reading its body raises."""
        with self._client.stream(
                method, url, headers=req_headers, content=body,
                follow_redirects=False, extensions={"_argus_box": box},
                **tkw) as resp:
            # DNS-rebinding guard: the scope check resolved the host once,
            # but this connection resolved it again - a changed answer now
            # points at a private address while passing the earlier check.
            # The connected peer's real address is authoritative.
            if not self.scope.allow_private:
                ns = resp.extensions.get("network_stream")
                peer = None
                try:
                    addr = ns.get_extra_info("server_addr") if ns else None
                    if addr:
                        peer = _ipaddress.ip_address(addr[0])
                except (ValueError, TypeError, OSError, AttributeError):
                    peer = None
                if peer is not None and _ip_private(peer):
                    raise ScopeError(
                        f"connection to {resp.request.url.host} resolved to "
                        f"private address {peer} at connect time "
                        f"(DNS rebinding protection)")
            buf = bytearray()
            for chunk in resp.iter_bytes(65536):
                buf += chunk
                if len(buf) > BODY_CAP:
                    break
            truncated = len(buf) > BODY_CAP
            return resp, bytes(buf[:BODY_CAP]), truncated

    @staticmethod
    def _decode_body(raw: bytes, encoding: str | None) -> str:
        try:
            return raw.decode(encoding or "utf-8", errors="replace")
        except (LookupError, TypeError):
            return raw.decode("utf-8", errors="replace")

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
        if not isinstance(method, str) or not method.strip() or \
                any(ord(c) < 0x21 or ord(c) > 0x7E for c in method):
            # httpx does NOT reject control chars in the method - a CRLF
            # there is written verbatim into the request line, smuggling
            # a header past every framing check
            raise ValueError(
                f"invalid HTTP method {method!r}: printable token only")
        if body is not None and not isinstance(body, (str, bytes)):
            raise TypeError(
                f"body must be str or bytes, got {type(body).__name__}")
        if headers is not None and not isinstance(headers, dict):
            raise TypeError(
                f"headers must be a dict, got {type(headers).__name__}")
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
        box: dict = {}
        raw = b""
        truncated = False
        try:
            resp, raw, truncated = self._fetch_capped(
                method.upper(), url, req_headers, body, tkw, box)
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
                resp, raw, truncated = self._fetch_capped(
                    m2, nxt, req_headers, b2, tkw, box)
                hops += 1
            elapsed_ms = round((time.monotonic() - started) * 1000, 1)
            response_data = {
                "status": resp.status_code,
                "headers": _headers_dict(resp),
                "body": self._decode_body(raw, resp.encoding),
                "elapsed_ms": elapsed_ms,
                "final_url": str(resp.url),
                "truncated": truncated,
            }
            if chain:
                response_data["redirects"] = chain
        except httpx.InvalidURL as exc:
            # Not an HTTPError: httpx refuses to parse the redirect target
            # (javascript:/data:/malformed Location). The event hook held on
            # to the verbatim 30x, so evidence survives the exception.
            elapsed_ms = round((time.monotonic() - started) * 1000, 1)
            error = f"{type(exc).__name__}: {exc}"
            resp = resp or box.get("resp")
            # raw was already read bounded inside the stream context; the
            # closed Response's .text would raise ResponseNotRead here
            rbody = self._decode_body(
                raw, getattr(resp, "encoding", None)) if raw else ""
            response_data = {
                "status": resp.status_code if resp is not None else 0,
                "headers": _headers_dict(resp) if resp is not None else {},
                "body": rbody,
                "elapsed_ms": elapsed_ms,
                "error": error,
            }
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
                                 "headers": _redact_headers(
                                     dict(resp.request.headers),
                                     self._secret_values),
                                 "body": body[:BODY_CAP].decode(
                                     "utf-8", "replace")
                                 if isinstance(body, bytes) else
                                 body[:BODY_CAP]
                                 if isinstance(body, str) else body},
                        response={"status": resp.status_code,
                                  "headers": _redact_headers(
                                      _headers_dict(resp),
                                      self._secret_values),
                                  "body": self._decode_body(
                                      raw, resp.encoding),
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

        # persisted request bodies get the same cap as responses - a
        # model-written upload payload must not bloat the transcript
        req_body = body[:BODY_CAP] if isinstance(body, bytes) else \
            (body[:BODY_CAP] if isinstance(body, str) else body)
        rid = self.session.record_exchange(
            tool=tool,
            request={"method": method.upper(), "url": url,
                     "headers": _redact_headers(sent_headers,
                                                self._secret_values),
                     "body": req_body.decode("utf-8", "replace")
                     if isinstance(req_body, bytes) else req_body},
            response={**response_data,
                      "headers": _redact_headers(
                          response_data["headers"], self._secret_values)},
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

    _WS_GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    _WS_MAX_FRAME = 16384

    def send_ws(
        self,
        url: str,
        message: str,
        origin: str = "",
        tool: str = "probe_websocket",
        note: str = "",
    ) -> dict:
        """One WebSocket handshake and one framed message, on one socket.

        `send_raw` cannot do this: after a 101 the connection stops speaking
        HTTP, and `http.client.HTTPResponse` has no way to read a frame. So
        this is the third socket-owning path in the package, and it goes
        through the same guards as the other two - scope check with the
        rebinding re-check at connect time, the rate limiter, the request
        budget, and two recorded exchanges.

        Deliberately minimal: masked text frame out, one frame in, close.
        No fragmentation, no binary, no continuation, no second message. The
        proof this supports is "the channel accepted a cross-origin
        handshake and answered a message", and nothing here needs more than
        one frame to show that.
        """
        import base64
        import hashlib
        import http.client
        import os as _os
        import struct

        parsed = self.scope.check(url)
        path = parsed.path or "/"
        if parsed.query:
            path += "?" + parsed.query
        host_port = f"{parsed.hostname}:{parsed.port}" if parsed.port \
            else parsed.hostname
        port = parsed.port or (443 if parsed.scheme in ("https", "wss")
                               else 80)
        key = base64.b64encode(_os.urandom(16)).decode()
        want = base64.b64encode(hashlib.sha1(
            (key + self._WS_GUID).encode()).digest()).decode()

        if parsed.scheme in ("https", "wss"):
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
        out: dict = {"handshake_id": "", "message_id": "", "accept_ok": False,
                     "answered": False, "reply": "", "status": 0}
        try:
            conn.connect()
            if not self.scope.allow_private and conn.sock is not None:
                try:
                    peer_ip = _ipaddress.ip_address(
                        conn.sock.getpeername()[0])
                except (ValueError, TypeError, OSError):
                    peer_ip = None
                if peer_ip is not None and _ip_private(peer_ip):
                    conn.close()
                    raise ScopeError(
                        f"connection to {parsed.hostname} resolved to "
                        f"private address {peer_ip} at connect time "
                        f"(DNS rebinding protection)")
            lines = [f"GET {path} HTTP/1.1", f"Host: {host_port}",
                     "Upgrade: websocket", "Connection: Upgrade",
                     f"Sec-WebSocket-Key: {key}",
                     "Sec-WebSocket-Version: 13"]
            if origin:
                lines.append(f"Origin: {origin}")
            emitted = {"host", "connection", "upgrade", "origin",
                       "sec-websocket-key", "sec-websocket-version"}
            for k, v in self._default_headers.items():
                if k.lower() in emitted:
                    continue
                emitted.add(k.lower())
                lines.append(f"{k}: {v}")
            if "user-agent" not in emitted:
                lines.append("User-Agent: argus-ws/1.0")
            raw = ("\r\n".join(lines) + "\r\n\r\n").encode()

            self.rate.wait()
            with self._sent_lock:
                if self.sent >= self.max_requests:
                    raise RequestBudgetExhausted(
                        f"request budget exhausted ({self.max_requests}); "
                        "call finish")
                self.sent += 1
            started = time.monotonic()
            conn.sock.sendall(raw)
            resp = http.client.HTTPResponse(conn.sock, method="GET")
            resp.begin()
            headers = dict(resp.getheaders())
            out["status"] = resp.status
            lower = {k.lower(): v for k, v in headers.items()}
            accept = str(lower.get("sec-websocket-accept") or "")
            out["accept_ok"] = (resp.status == 101
                                and "websocket" in str(
                                    lower.get("upgrade") or "").lower()
                                and accept == want)
            out["handshake_id"] = self.session.record_exchange(
                tool=tool,
                request={"method": "GET", "url": url,
                         "headers": _redact_headers(
                             {l.split(": ", 1)[0]: l.split(": ", 1)[1]
                              for l in lines[1:]}, self._secret_values),
                         "request_text": "\r\n".join(lines)},
                response={"status": resp.status, "headers": headers,
                          "body": "",
                          "elapsed_ms": round(
                              (time.monotonic() - started) * 1000, 1)},
                note=note or "websocket upgrade handshake",
                agent=self.agent)
            if not out["accept_ok"]:
                return out

            # masked text frame, as RFC 6455 requires of a client
            payload = message.encode()[:self._WS_MAX_FRAME]
            mask = _os.urandom(4)
            frame = bytearray([0x81])
            if len(payload) < 126:
                frame.append(0x80 | len(payload))
            elif len(payload) < 1 << 16:
                frame.append(0x80 | 126)
                frame += struct.pack(">H", len(payload))
            else:
                frame.append(0x80 | 127)
                frame += struct.pack(">Q", len(payload))
            frame += mask
            frame += bytes(b ^ mask[i % 4] for i, b in enumerate(payload))

            self.rate.wait()
            with self._sent_lock:
                if self.sent >= self.max_requests:
                    raise RequestBudgetExhausted(
                        f"request budget exhausted ({self.max_requests}); "
                        "call finish")
                self.sent += 1
            started = time.monotonic()
            conn.sock.settimeout(5.0)
            conn.sock.sendall(bytes(frame))
            reply, error = self._ws_read_frame(conn.sock), None
        except (http.client.HTTPException, OSError, TimeoutError,
                struct.error) as exc:
            reply, error = "", f"{type(exc).__name__}: {exc}"
            if not out["handshake_id"]:
                out["error"] = error
                return out
        finally:
            try:
                conn.sock.sendall(b"\x88\x00")   # close frame, best effort
            except (OSError, AttributeError):
                pass
            conn.close()
        out["answered"] = bool(reply)
        out["reply"] = reply[:self._WS_MAX_FRAME]
        out["message_id"] = self.session.record_exchange(
            tool=tool,
            request={"method": "WSFRAME", "url": url,
                     "headers": {}, "body": message},
            response={"status": 101 if reply else 0, "headers": {},
                      "body": reply,
                      "elapsed_ms": round(
                          (time.monotonic() - started) * 1000, 1)},
            note=note or "websocket text frame",
            agent=self.agent)
        if error:
            out["error"] = error
        return out

    def _ws_read_frame(self, sock) -> str:
        """One server frame's text payload, bounded. Server frames are
        never masked, so a masked one is a protocol violation and is read
        as no answer rather than silently unmasked."""
        import struct

        def _exact(n: int) -> bytes:
            buf = b""
            while len(buf) < n:
                chunk = sock.recv(n - len(buf))
                if not chunk:
                    return buf
                buf += chunk
            return buf

        head = _exact(2)
        if len(head) < 2:
            return ""
        opcode = head[0] & 0x0F
        if head[1] & 0x80:
            return ""                      # masked server frame: invalid
        length = head[1] & 0x7F
        if length == 126:
            raw = _exact(2)
            if len(raw) < 2:
                return ""
            length = struct.unpack(">H", raw)[0]
        elif length == 127:
            raw = _exact(8)
            if len(raw) < 8:
                return ""
            length = struct.unpack(">Q", raw)[0]
        if opcode in (0x8, 0x9, 0xA) or length > self._WS_MAX_FRAME:
            return ""                      # close/ping/pong is not an answer
        return _exact(length).decode("utf-8", "replace")

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
        rbfile = None
        try:
            conn.connect()
            # same rebinding guard as _fetch_capped: the scope check's
            # resolution and this socket's are two separate answers
            if not self.scope.allow_private and conn.sock is not None:
                try:
                    peer_ip = _ipaddress.ip_address(
                        conn.sock.getpeername()[0])
                except (ValueError, TypeError, OSError):
                    peer_ip = None
                if peer_ip is not None and _ip_private(peer_ip):
                    conn.close()
                    raise ScopeError(
                        f"connection to {parsed.hostname} resolved to "
                        f"private address {peer_ip} at connect time "
                        f"(DNS rebinding protection)")
            # ONE buffered reader shared by every response on this
            # connection: each HTTPResponse would otherwise wrap the socket
            # in its own BufferedReader, and the first response's read-ahead
            # would swallow the NEXT response's bytes - seen downstream as
            # RemoteDisconnected or a mid-body BadStatusLine on extra reads.
            rbfile = conn.sock.makefile("rb")
            for spec in requests:
                method = (spec.get("method") or "GET").upper()
                lines = [f"{method} {path} HTTP/1.1",
                         f"Host: {host_port}",
                         "Connection: keep-alive"]
                # operator headers (--header auth cookies) ride every send,
                # raw included - on an authenticated target an unauthenticated
                # smuggle probe dies at the front-end before reaching the
                # framing boundary. Framing headers stay spec-controlled.
                emitted = {"host", "connection"}
                for k, v in self._default_headers.items():
                    kl = k.lower()
                    if kl in emitted or kl in ("content-length",
                                               "transfer-encoding"):
                        continue
                    emitted.add(kl)
                    lines.append(f"{k}: {v}")
                if "user-agent" not in emitted:
                    emitted.add("user-agent")
                    lines.append("User-Agent: argus-raw/1.0")
                spec_headers = spec.get("headers") or []
                if isinstance(spec_headers, dict):
                    # models naturally emit {"A":"b"}; iterating a dict
                    # would unpack 2-char KEYS into (k,v) and silently
                    # write a wrong header onto the wire
                    spec_headers = list(spec_headers.items())
                for k, v in spec_headers:
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
                try:
                    # sock-level send + HTTPResponse: the connection's own
                    # state machine only understands well-formed requests
                    conn.sock.sendall(raw_req)
                    send_error = None
                except (http.client.HTTPException, OSError) as exc:
                    send_error = f"{type(exc).__name__}: {exc}"
                # reads>1 collects pipelined/unsolicited responses: a
                # desynced back-end answers a poisoned queued request
                # without us sending anything more
                n_reads = max(1, int(spec.get("reads") or 1))
                for ri in range(n_reads):
                    status, rheaders, rbody, error = 0, {}, "", send_error
                    try:
                        if ri > 0:
                            conn.sock.settimeout(3.0)  # extra reads are opportunistic
                        resp = http.client.HTTPResponse(
                            conn.sock, method=method)
                        resp.fp.close()  # private reader never read - swap
                        resp.fp = _NoCloseFile(rbfile)  # share the real one
                        resp.begin()
                        # the full body MUST be drained or its bytes corrupt
                        # the next response's parse on this reused connection -
                        # but only the first BODY_CAP is kept: a hostile server
                        # cannot exhaust memory with an unbounded body
                        buf = bytearray()
                        while True:
                            chunk = resp.read(65536)
                            if not chunk:
                                break
                            if len(buf) <= BODY_CAP:
                                buf += chunk
                        rbody = bytes(buf[:BODY_CAP]).decode(
                            "utf-8", "replace")
                        status = resp.status
                        rheaders = dict(resp.getheaders())
                    except (http.client.HTTPException, OSError,
                            TimeoutError) as exc:
                        if error is None:
                            error = f"{type(exc).__name__}: {exc}"
                    finally:
                        conn.sock.settimeout(15.0)
                    elapsed = round((time.monotonic() - started) * 1000, 1)
                    rid = self.session.record_exchange(
                        tool=tool,
                        request={"method": method if ri == 0 else "-",
                                 "url": url,
                                 # a dict collapses duplicate headers - and
                                 # a duplicated/conflicting header pair IS
                                 # the evidence - so keep the wire text too
                                 "headers": _redact_headers(
                                     {l.split(": ", 1)[0]:
                                          l.split(": ", 1)[1]
                                      for l in lines[1:]},
                                     self._secret_values),
                                 "raw": True,
                                 "request_text": _redact_request_text(
                                     raw_req.decode("utf-8", "replace"),
                                     self._secret_values)[:4000],
                                 "body": body[:BODY_CAP].decode(
                                     "utf-8", "replace")},
                        response={"status": status,
                                  "headers": _redact_headers(
                                      rheaders, self._secret_values),
                                  "body": rbody, "elapsed_ms": elapsed},
                        note=(note or "raw send")
                             + ("" if ri == 0 else f" (unsolicited #{ri})"),
                        agent=self.agent)
                    entry = {"request_id": rid, "status": status,
                             "elapsed_ms": elapsed,
                             "solicited": ri == 0,
                             "body": rbody[:RETURN_CAP]}
                    if error:
                        entry["error"] = error
                    sends_out.append(entry)
                    if error:
                        break
                if send_error or (sends_out and sends_out[-1].get("error")
                                  and spec.get("stop_on_error", True)):
                    break
        finally:
            try:
                conn.close()
            except Exception:
                pass
            if rbfile is not None:
                try:
                    rbfile.close()
                except Exception:
                    pass
        return {"sends": sends_out,
                "note": "raw sends share one connection - order matters" if len(sends_out) > 1 else ""}

    def close(self) -> None:
        self._client.close()
