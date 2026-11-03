"""An out-of-band collector, for the classes whose proof is a callback.

Blind SSRF, blind XXE, JNDI lookups and blind injection all share one shape:
nothing comes back in the response, and the only honest evidence is that the
target reached a host we control carrying a token only we could have minted.

This is a small HTTP listener that writes one JSONL line per request into the
engagement directory. It is not a public interactsh: it binds an interface on
this machine, which is the right answer for a lab or an internal engagement and
useless for a target with no route back. That limit is stated rather than hidden
— `proof.oob_check` says so when nothing arrives.
"""
from __future__ import annotations

import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from ..util import append_jsonl, now_iso

_SERVERS: dict[int, "Collector"] = {}


class _Handler(BaseHTTPRequestHandler):
    server_version = "argus-collector/0.1"
    hits_path: Path

    def _record(self, method: str) -> None:
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length).decode("utf-8", "replace") if length else ""
        append_jsonl(self.hits_path, {
            "ts": now_iso(), "method": method, "path": self.path,
            "source_ip": self.client_address[0],
            "headers": {k.lower(): v for k, v in self.headers.items()},
            "body": body[:4000],
        })
        payload = b"ok\n"
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):                     # noqa: N802
        self._record("GET")

    def do_POST(self):                    # noqa: N802
        self._record("POST")

    def do_PUT(self):                     # noqa: N802
        self._record("PUT")

    def log_message(self, *args):         # stdout belongs to the MCP transport
        pass


class Collector:
    def __init__(self, server: ThreadingHTTPServer, hits_path: Path, bind: str, port: int):
        self.server = server
        self.hits_path = hits_path
        self.bind = bind
        self.port = port
        self.started = now_iso()

    def stop(self) -> None:
        self.server.shutdown()
        self.server.server_close()
        _SERVERS.pop(self.port, None)


def start(hits_path: Path, bind: str = "0.0.0.0", port: int = 0) -> Collector:
    handler = type("_BoundHandler", (_Handler,), {"hits_path": hits_path})
    server = ThreadingHTTPServer((bind, port), handler)
    bound_port = server.server_address[1]
    threading.Thread(target=server.serve_forever, daemon=True).start()
    collector = Collector(server, hits_path, bind, bound_port)
    _SERVERS[bound_port] = collector
    return collector


def running() -> dict[int, Collector]:
    return dict(_SERVERS)


def local_addresses() -> list[str]:
    """Addresses a target might be able to reach us on, best effort."""
    addresses = {"127.0.0.1"}
    try:
        for info in socket.getaddrinfo(socket.gethostname(), None):
            addresses.add(info[4][0])
    except OSError:
        pass
    try:
        probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        probe.connect(("8.8.8.8", 80))
        addresses.add(probe.getsockname()[0])
        probe.close()
    except OSError:
        pass
    return sorted(addresses)
