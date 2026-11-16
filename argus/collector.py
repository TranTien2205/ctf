"""An out-of-band collector: the channel a payload calls back on.

Two proof classes were capped at `candidate` for the want of this one
component, and both for the same reason. `xss` could see a payload reflected
but not that a browser ran it; `ssrf` could see a response change but not
that the target had reached anything. In both, the missing half is the same
shape: the payload, when it actually executes, causes a REQUEST, and that
request has to arrive somewhere this package records.

Why the callback and not the browser's own answer
-------------------------------------------------
A browser can be asked `window.__nonce` and will answer truthfully. But the
answer reaches the gate through the probe, and the gate's whole position is
that a probe's report of its own success is not evidence - that is what
`record_finding` refuses for every other class. A callback is different in
kind: the bytes arrive on a socket this module owns, and the probe never
writes them. It is the same arrangement as `id; echo <nonce>`, where the
probe sends and `GuardedClient` records.

What this does NOT prove
------------------------
A hit from loopback cannot be told apart from this process calling itself.
Against the threat this package actually defends against - a MODEL claiming
something that did not happen - that is sound, because the model does not
get to write here; only this module does. It is not sound against argus's
own probes lying, and nothing in this package is. `witness_is_remote` below
exists so the one case where the distinction IS checkable - a remote target
reaching us - can be required rather than assumed.
"""

from __future__ import annotations

import http.server
import json
import secrets
import socket
import threading
import time
from typing import Any, Callable

__all__ = ["Collector", "new_nonce", "NONCE_RE"]

import re

# A nonce has to survive an HTML attribute, a URL path and a shell word
# without quoting, so it is letters and digits only. 16 hex characters is
# 64 bits: the gate asks whether THIS probe's nonce came back, and a
# collision would have to be produced by the target, not stumbled into.
NONCE_RE = re.compile(r"\bargus([0-9a-f]{16})\b")


def new_nonce() -> str:
    """A fresh callback nonce. `argus` prefix so a hit is readable on sight."""
    return "argus" + secrets.token_hex(8)


class _Handler(http.server.BaseHTTPRequestHandler):
    """Answers nothing and serves nothing. It exists to be reached."""

    # BaseHTTPRequestHandler logs to stderr by default, which would put
    # target-controlled bytes into the operator's terminal unfiltered.
    def log_message(self, fmt: str, *args: Any) -> None:  # noqa: A002
        return

    def _note(self, method: str) -> None:
        length = 0
        try:
            length = int(self.headers.get("content-length") or 0)
        except (TypeError, ValueError):
            length = 0
        # A callback is a signal, not a payload. Read a bounded prefix so a
        # target that answers with a gigabyte cannot spend this process's
        # memory, and say so rather than silently truncating to nothing.
        body = b""
        if 0 < length <= self.server.max_body:  # type: ignore[attr-defined]
            try:
                body = self.rfile.read(length)
            except OSError:
                body = b""
        elif length > self.server.max_body:  # type: ignore[attr-defined]
            try:
                body = self.rfile.read(self.server.max_body)  # type: ignore[attr-defined]
            except OSError:
                body = b""
        self.server.note_hit(  # type: ignore[attr-defined]
            method=method,
            path=self.path,
            headers={k.lower(): v for k, v in self.headers.items()},
            peer=self.client_address[0] if self.client_address else "",
            body=body.decode("utf-8", "replace"),
        )
        self.send_response(204)
        self.send_header("content-length", "0")
        self.end_headers()

    def do_GET(self) -> None:
        self._note("GET")

    def do_POST(self) -> None:
        self._note("POST")

    def do_PUT(self) -> None:
        self._note("PUT")

    def do_HEAD(self) -> None:
        self._note("HEAD")

    def do_OPTIONS(self) -> None:
        self._note("OPTIONS")


class _Server(http.server.ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True
    max_body = 4096

    def note_hit(self, **hit: Any) -> None:
        raise NotImplementedError


class Collector:
    """A listener that records what reaches it.

    `host` defaults to loopback. A target on another machine cannot reach
    loopback, so SSRF needs a routable bind - and that opens a port to the
    LAN, which is a decision an operator makes rather than a default this
    takes. `routable_host()` finds the address to pass, and nothing calls it
    for you.
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 0) -> None:
        self.hits: list[dict] = []
        self._lock = threading.Lock()
        self._sink: Callable[[dict], None] | None = None
        self._srv = _Server((host, port), _Handler)
        self._srv.note_hit = self._note  # type: ignore[method-assign]
        self.host, self.port = self._srv.server_address[0], self._srv.server_address[1]
        self._thread = threading.Thread(target=self._srv.serve_forever,
                                        kwargs={"poll_interval": 0.1},
                                        daemon=True)

    # -- lifecycle ------------------------------------------------------
    def __enter__(self) -> "Collector":
        self.start()
        return self

    def __exit__(self, *exc: Any) -> None:
        self.stop()

    def start(self) -> "Collector":
        self._thread.start()
        return self

    def stop(self) -> None:
        self._srv.shutdown()
        self._srv.server_close()

    # -- recording ------------------------------------------------------
    def _note(self, **hit: Any) -> None:
        # `ts` is this module's clock, not anything the caller sends: the
        # gate asks whether the callback came AFTER the request that caused
        # it, and a timestamp the target could set would answer a different
        # question than the one being asked.
        entry = dict(hit, ts=round(time.time(), 3))
        entry["nonces"] = sorted({m.group(0) for m in
                                  NONCE_RE.finditer(hit.get("path", "")
                                                    + " " + hit.get("body", ""))})
        with self._lock:
            self.hits.append(entry)
            sink = self._sink
        if sink is not None:
            sink(entry)

    def on_hit(self, sink: Callable[[dict], None]) -> None:
        """Call `sink` for each hit, e.g. to write it to the transcript."""
        with self._lock:
            self._sink = sink

    def url(self, nonce: str) -> str:
        """The URL a payload should reach for `nonce` to be recorded."""
        return f"http://{self.host}:{self.port}/{nonce}"

    def hits_for(self, nonce: str, after: float = 0.0) -> list[dict]:
        """Hits carrying `nonce`, optionally only those recorded after a time.

        `after` is compared with `>`, not `>=`: a hit stamped in the same
        millisecond as the request that supposedly caused it has not been
        shown to follow it, and the question here is which came first.
        """
        with self._lock:
            return [h for h in self.hits
                    if nonce in h.get("nonces", []) and h["ts"] > after]

    def as_exchange(self, hit: dict) -> tuple[dict, dict]:
        """A hit, in the request/response shape the transcript records.

        `direction` is the field that matters: without it a hit this
        process received and a request this process sent read identically
        once they are both entries with a `request` key, and a probe
        calling its own collector would look exactly like a target calling
        it. The gate requires `inbound`.
        """
        request = {
            "direction": "inbound",
            "method": hit.get("method", ""),
            "url": f"http://{self.host}:{self.port}{hit.get('path', '')}",
            "headers": hit.get("headers", {}),
            "body": hit.get("body", ""),
            "peer": hit.get("peer", ""),
        }
        response = {"status": 204, "headers": {"content-length": "0"}, "body": ""}
        return request, response


def routable_host(toward: str) -> str:
    """The local address a host at `toward` would see us on.

    No packet is sent - connecting a UDP socket only picks the route - but
    it answers the question `127.0.0.1` cannot: which of this machine's
    addresses is the one a target on another machine can reach.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect((toward, 9))
        return str(sock.getsockname()[0])
    except OSError:
        return "127.0.0.1"
    finally:
        sock.close()


def witness_is_remote(hit: dict, loopback_ok: bool = False) -> bool:
    """Whether this hit came from somewhere other than this machine.

    For `ssrf` the target is on another host, so a loopback hit proves
    nothing and this must be true. For `xss` the browser runs here, so it
    cannot be - which is why that class gets the weaker claim, stated in
    its own words rather than borrowed from this one.
    """
    peer = (hit.get("peer") or "").strip()
    if not peer:
        return False
    if peer.startswith("127.") or peer in ("::1", "localhost"):
        return bool(loopback_ok)
    return True
