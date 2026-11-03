#!/usr/bin/env python3
"""A deliberately vulnerable target, for testing this toolkit offline.

It exists so the proof matrix, the ledger gate and the harness can be exercised
end to end with no network, no lab VM and no real target. Every weakness here is
planted, each one maps to exactly one class in `argus/ledger/proof.py`, and the
flag for each is a string only a working exploit can read.

    /                       index, links and a form
    /search?q=              reflected into HTML and into a script string  -> xss
    /item?id=               string-concatenated SQL over sqlite           -> sqli
    /ping?host=             passed to a shell                             -> rce
    /view?file=             path joined without normalisation             -> lfi
    /calc?expr=             evaluated as a python expression              -> ssti
    /api/note?id=&user=     reads any note, trusts the user parameter     -> idor
    /fetch?url=             fetches any URL server-side                   -> ssrf
    /static/app.js          ships an endpoint list and a key shape        -> secret-exposure

It binds 127.0.0.1 only and refuses any other bind address. Do not deploy it.
"""
from __future__ import annotations

import html
import json
import os
import socketserver
import sqlite3
import subprocess
import sys
import threading
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler

BANNER = "vulnapp: intentionally vulnerable test fixture, loopback only"
ROOT = os.path.dirname(os.path.abspath(__file__))
SANDBOX = os.path.join(ROOT, "vulnapp-files")

FLAGS = {
    "sqli": "FLAG{sqli-dumped-the-users-table}",
    "rce": "FLAG{rce-ran-a-command}",
    "lfi": "FLAG{lfi-read-a-local-file}",
    "ssti": "FLAG{ssti-evaluated-an-expression}",
    "idor": "FLAG{idor-read-another-users-note}",
}

_DB = threading.local()


def db() -> sqlite3.Connection:
    if getattr(_DB, "connection", None) is None:
        connection = sqlite3.connect(":memory:")
        connection.executescript(
            """
            CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT);
            INSERT INTO users VALUES (1,'admin','s3cr3t-admin','admin'),
                                     (2,'alice','alice-pw','user'),
                                     (3,'bob','bob-pw','user');
            CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT, owner INTEGER);
            INSERT INTO items VALUES (1,'laptop',2),(2,'phone',3),(3,'router',1);
            CREATE TABLE notes (id INTEGER PRIMARY KEY, owner TEXT, body TEXT);
            """
        )
        connection.execute("INSERT INTO notes VALUES (1,'alice','shopping list')")
        connection.execute("INSERT INTO notes VALUES (2,'admin',?)", (FLAGS["idor"],))
        connection.commit()
        _DB.connection = connection
    return _DB.connection


INDEX = """<!doctype html><html><head><title>Vulnerable Widgets Inc</title>
<script src="/static/app.js"></script></head><body>
<h1>Widgets</h1>
<form action="/search" method="get"><input name="q" placeholder="search"><input type="submit"></form>
<ul>
<li><a href="/item?id=1">laptop</a></li>
<li><a href="/item?id=2">phone</a></li>
<li><a href="/view?file=readme.txt">readme</a></li>
<li><a href="/ping?host=127.0.0.1">ping</a></li>
<li><a href="/calc?expr=1%2B1">calc</a></li>
<li><a href="/api/note?id=1&user=alice">my note</a></li>
<li><a href="/fetch?url=http://127.0.0.1/robots.txt">fetch</a></li>
<li><a href="/redirect?to=/robots.txt">go</a></li>
</ul></body></html>"""

APP_JS = """// build 2026.11.1
const API = {
  notes: "/api/note",
  items: "/item",
  admin: "/admin/export",
  upload: "/api/upload"
};
const ANALYTICS_KEY = "AKIAIOSFODNN7EXAMPLE";
function load(id){ return fetch("/api/note?id=" + id + "&user=" + window.USER); }
"""


class Handler(BaseHTTPRequestHandler):
    server_version = "VulnWidgets/1.4"
    sys_version = ""

    def _send(self, body: str | bytes, code: int = 200, content_type: str = "text/html") -> None:
        payload = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("X-Powered-By", "VulnWidgets")
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self) -> None:                                            # noqa: N802
        split = urllib.parse.urlsplit(self.path)
        query = urllib.parse.parse_qs(split.query, keep_blank_values=True)
        route = split.path
        one = lambda name, default="": (query.get(name) or [default])[0]  # noqa: E731
        try:
            if route == "/":
                return self._send(INDEX)
            if route == "/static/app.js":
                return self._send(APP_JS, content_type="application/javascript")
            if route == "/robots.txt":
                return self._send("User-agent: *\nDisallow: /admin/\n", content_type="text/plain")
            if route == "/search":                                       # xss
                value = one("q")
                return self._send(f"<html><body><p>No results for {value}</p>"
                                  f"<script>var term='{value}';</script></body></html>")
            if route == "/item":                                         # sqli
                identifier = one("id", "1")
                cursor = db().execute(f"SELECT id,name FROM items WHERE id = {identifier}")  # noqa: S608
                rows = cursor.fetchall()
                return self._send("<html><body><table>" + "".join(
                    f"<tr><td>{r[0]}</td><td>{html.escape(str(r[1]))}</td></tr>" for r in rows)
                    + "</table></body></html>")
            if route == "/ping":                                         # rce
                host = one("host", "127.0.0.1")
                completed = subprocess.run(f"echo pinging {host}", shell=True,  # noqa: S602
                                           capture_output=True, text=True, timeout=10)
                return self._send(f"<pre>{completed.stdout}{completed.stderr}</pre>")
            if route == "/view":                                         # lfi
                name = one("file", "readme.txt")
                path = os.path.join(SANDBOX, name)
                with open(path, "rb") as handle:
                    return self._send(handle.read(), content_type="text/plain")
            if route == "/calc":                                         # ssti-shaped
                expression = one("expr", "1+1")
                value = eval(expression, {"__builtins__": {}}, {})       # noqa: S307
                return self._send(f"<html><body>result: {value}</body></html>")
            if route == "/api/note":                                     # idor
                identifier, user = one("id", "1"), one("user", "alice")
                row = db().execute("SELECT id,owner,body FROM notes WHERE id=?",
                                   (identifier,)).fetchone()
                if row is None:
                    return self._send(json.dumps({"error": "not found"}), 404, "application/json")
                return self._send(json.dumps({"id": row[0], "owner": row[1], "body": row[2],
                                              "requested_by": user}), 200, "application/json")
            if route == "/fetch":                                        # ssrf
                url = one("url")
                with urllib.request.urlopen(url, timeout=5) as response:  # noqa: S310
                    return self._send(response.read()[:4000], content_type="text/plain")
            if route == "/redirect":                                     # open-redirect
                destination = one("to", "/")
                self.send_response(302)
                self.send_header("Location", destination)
                self.send_header("Content-Length", "0")
                self.end_headers()
                return
            if route == "/admin/export":
                return self._send(json.dumps({"error": "forbidden"}), 403, "application/json")
            return self._send("<html><body>not found</body></html>", 404)
        except Exception as error:                                       # noqa: BLE001
            return self._send(f"<html><body>error: {html.escape(str(error))}</body></html>", 500)

    def do_POST(self) -> None:                                           # noqa: N802
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length).decode("utf-8", "replace")
        self.path = self.path + ("&" if "?" in self.path else "?") + body
        return self.do_GET()

    def log_message(self, *args) -> None:                                # keep the test output clean
        pass


class Server(socketserver.ThreadingTCPServer):
    allow_reuse_address = True
    daemon_threads = True

    def handle_error(self, request, client_address) -> None:
        """A scanner closes connections mid-response constantly; a broken pipe is
        normal traffic here, not an error worth a stack trace."""
        return


def seed_files() -> None:
    os.makedirs(SANDBOX, exist_ok=True)
    with open(os.path.join(SANDBOX, "readme.txt"), "w") as handle:
        handle.write("Widgets Inc internal readme\n")
    with open(os.path.join(SANDBOX, "flag.txt"), "w") as handle:
        handle.write(FLAGS["lfi"] + "\n")
    # A file whose shape the LFI proof checks for, inside the fixture only.
    with open(os.path.join(SANDBOX, "passwd"), "w") as handle:
        handle.write("root:x:0:0:root:/root:/bin/sh\nwww-data:x:33:33:www-data:/var/www:/usr/sbin/nologin\n")


def serve(port: int = 0) -> tuple[Server, int]:
    seed_files()
    server = Server(("127.0.0.1", port), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, server.server_address[1]


def main() -> int:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8099
    print(BANNER, file=sys.stderr)
    server, bound = serve(port)
    print(f"http://127.0.0.1:{bound}/", flush=True)
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        server.shutdown()
    return 0


if __name__ == "__main__":
    sys.exit(main())
