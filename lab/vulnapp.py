#!/usr/bin/env python3
"""vulnapp - a deliberately vulnerable lab target for Argus.

Stdlib-only (works anywhere Python runs, including Windows). Exposes one bug
per Argus probe family so the agent can be exercised end-to-end offline:

    GET  /                     index with links + a search form
    GET  /search?q=            reflected XSS (unescaped reflection)
    GET  /item?id=             SQLi (error-based + boolean-blind, sqlite)
    POST /login                SQLi auth bypass (' OR '1'='1)
    GET  /ping?host=           command injection (sleep separators)
    GET  /hello?name=          SSTI ({{expr}} arithmetic evaluation)
    GET  /download?file=       path traversal / file read
    GET  /redirect?next=       open redirect
    GET  /api/user/<id>        IDOR (any id served)
    GET  /fetch?url=           SSRF (real server-side fetch, 3s timeout)
    POST /xml                  XXE (simulated external-entity resolution)
    POST /api/login            NoSQLi ($ne/$gt operator password bypass)
    POST /upload, GET /uploads file upload served back with active content-type
    GET  /api/data             CORS: reflects Origin + credentials
    GET  /api/me               JWT (HS256, weak secret 'secret123')
    GET  /token?user=          issues a JWT
    GET  /.git/HEAD, /debug    info disclosure

Run:  python lab/vulnapp.py [port]
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import re
import sqlite3
import sys
import threading
import time
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

LABDIR = os.path.dirname(os.path.abspath(__file__))
WWW = os.path.join(LABDIR, "www")
FAKEFS = os.path.join(LABDIR, "fakefs")
JWT_SECRET = "secret123"

# ---------------------------------------------------------------- setup

def _init_db() -> sqlite3.Connection:
    db = sqlite3.connect(":memory:", check_same_thread=False)
    db.execute("CREATE TABLE items (id INTEGER, name TEXT, price REAL)")
    db.execute("CREATE TABLE users (id INTEGER, username TEXT, password TEXT, role TEXT)")
    db.execute("CREATE TABLE secrets (flag TEXT)")
    db.executemany("INSERT INTO items VALUES (?,?,?)",
                   [(1, "widget", 9.99), (2, "gadget", 19.99), (3, "sprocket", 4.50)])
    db.executemany("INSERT INTO users VALUES (?,?,?,?)",
                   [(1, "admin", "s3cr3t-admin-pw", "admin"),
                    (2, "alice", "alice-pw", "user"),
                    (3, "bob", "bob-pw", "user")])
    db.execute("INSERT INTO secrets VALUES ('LAB{sql1_fl4g_h3r3}')")
    return db


def _jwt(user: str) -> str:
    def b64(o): return base64.urlsafe_b64encode(
        json.dumps(o).encode()).decode().rstrip("=")
    head, pay = b64({"alg": "HS256", "typ": "JWT"}), \
        b64({"sub": user, "role": "user", "iat": int(time.time())})
    sig = base64.urlsafe_b64encode(
        hmac.new(JWT_SECRET.encode(), f"{head}.{pay}".encode(),
                 hashlib.sha256).digest()).decode().rstrip("=")
    return f"{head}.{pay}.{sig}"


def _jwt_verify(token: str):
    try:
        head, pay, sig = token.split(".")
        expect = base64.urlsafe_b64encode(
            hmac.new(JWT_SECRET.encode(), f"{head}.{pay}".encode(),
                     hashlib.sha256).digest()).decode().rstrip("=")
        if hmac.compare_digest(sig, expect):
            pad = "=" * (-len(pay) % 4)
            return json.loads(base64.urlsafe_b64decode(pay + pad))
    except Exception:
        return None
    return None


class Handler(BaseHTTPRequestHandler):
    db = None
    server_version = "LabVuln/1.0"

    # -- helpers ---------------------------------------------------------
    def _send(self, status=200, body="", ctype="text/html; charset=utf-8",
              headers=None):
        data = body.encode() if isinstance(body, str) else body
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("X-Powered-By", "LabVuln/1.0")
        origin = self.headers.get("Origin")
        if origin:
            # deliberately broken CORS: reflect any origin, allow credentials
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Credentials", "true")
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _params(self):
        q = urllib.parse.urlparse(self.path).query
        return dict(urllib.parse.parse_qsl(q))

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n).decode("utf-8", "replace") if n else ""
        if (self.headers.get("Content-Type") or "").startswith("application/json"):
            try:
                return json.loads(raw)
            except ValueError:
                return {}
        return dict(urllib.parse.parse_qsl(raw))

    def log_message(self, fmt, *args):
        pass  # quiet lab

    # -- routes ----------------------------------------------------------
    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        p = self._params()

        if path == "/":
            self._send(body="""<html><head><title>LabShop</title></head><body>
<h1>LabShop</h1>
<form action="/search" method="GET"><input name="q"><button>search</button></form>
<ul><li><a href="/item?id=1">item 1</a></li>
<li><a href="/redirect?next=/">go</a></li>
<li><a href="/download?file=welcome.txt">readme</a></li>
<li><a href="/hello?name=guest">hello</a></li>
<li><a href="/ping?host=127.0.0.1">ping diag</a></li></ul>
<script src="/static/app.js"></script>
<!-- TODO: remove /debug before production -->
</body></html>""")

        elif path == "/search":
            q = p.get("q", "")
            self._send(body=f"<html><body>Results for: {q}</body></html>")

        elif path == "/item":
            i = p.get("id", "1")
            try:
                rows = self.db.execute(
                    f"SELECT name, price FROM items WHERE id = '{i}'").fetchall()
            except sqlite3.Error as exc:
                self._send(500, f"<html><body>sqlite3.OperationalError: {exc}"
                                f" near \"{i}\": syntax error</body></html>")
                return
            if rows:
                out = "".join(f"<li>{n} - ${pr}</li>" for n, pr in rows)
                self._send(body=f"<html><body><ul>{out}</ul></body></html>")
            else:
                self._send(body="<html><body>No item found.</body></html>")

        elif path == "/ping":
            host = p.get("host", "")
            m = re.search(r"sleep\s+(\d+)", host)
            if re.search(r"[;&|`$(]", host) and m:
                time.sleep(min(int(m.group(1)), 8))
                self._send(body="<html><body>PING ok</body></html>")
            elif re.search(r"[;&|`$(]", host):
                self._send(500, "<html><body>sh: syntax error</body></html>")
            else:
                self._send(body=f"<html><body>PING {host}: 4 packets, 0% loss"
                                f"</body></html>")

        elif path == "/hello":
            name = p.get("name", "guest")
            def render(m):
                expr = m.group(1)
                if re.fullmatch(r"[\d\s+\-*/().]+", expr):
                    try:
                        return str(eval(expr, {"__builtins__": {}}, {}))
                    except Exception:
                        return m.group(0)
                return m.group(0)
            rendered = re.sub(r"\{\{(.*?)\}\}", render, name)
            self._send(body=f"<html><body>Hello, {rendered}!</body></html>")

        elif path == "/download":
            fname = p.get("file", "welcome.txt")
            if fname.startswith("/"):
                target = os.path.join(FAKEFS, fname.lstrip("/"))
            else:
                target = os.path.normpath(os.path.join(WWW, fname))
            try:
                with open(target, "rb") as fh:
                    data = fh.read()
                self._send(body=data, ctype="application/octet-stream")
            except OSError:
                self._send(404, "<html><body>file not found</body></html>")

        elif path == "/redirect":
            nxt = p.get("next", "/")
            self._send(302, "<html><body>redirecting</body></html>",
                       headers={"Location": nxt})

        elif path == "/fetch":
            u = p.get("url", "")
            try:
                with urllib.request.urlopen(u, timeout=3) as resp:
                    data = resp.read(4096)
                self._send(body=b"FETCHED:\n" + data)
            except Exception as exc:
                self._send(502, f"fetch error for {u}: {exc}",
                           ctype="text/plain")

        elif path.startswith("/api/user/"):
            uid = path.rsplit("/", 1)[-1]
            row = self.db.execute(
                "SELECT id, username, role FROM users WHERE id = ?",
                (uid,)).fetchone()
            if row:
                self._send(body=json.dumps(
                    {"id": row[0], "username": row[1], "role": row[2],
                     "email": f"{row[1]}@lab.local"}),
                    ctype="application/json")
            else:
                self._send(404, json.dumps({"error": "no such user"}),
                           ctype="application/json")

        elif path == "/api/data":
            self._send(body=json.dumps({"balance": 9000, "tier": "gold"}),
                       ctype="application/json")

        elif path == "/token":
            self._send(body=json.dumps({"token": _jwt(p.get("user", "guest"))}),
                       ctype="application/json")

        elif path == "/api/me":
            auth = self.headers.get("Authorization", "")
            tok = auth.removeprefix("Bearer ").strip()
            claims = _jwt_verify(tok) if tok else None
            if claims:
                self._send(body=json.dumps({"ok": True, "claims": claims}),
                           ctype="application/json")
            else:
                self._send(401, json.dumps({"error": "bad token"}),
                           ctype="application/json")

        elif path == "/debug":
            self._send(body="<html><body>DEBUG ON<br>Traceback (most recent "
                            "call last): File \"/srv/app/main.py\", line 42<br>"
                            "sqlite3.Connection @ 0xdeadbeef</body></html>")

        elif path == "/.git/HEAD":
            self._send(body="ref: refs/heads/main", ctype="text/plain")

        elif path == "/static/app.js":
            self._send(body="""fetch('/api/user/1').then(r=>r.json());
const internal = '/internal/status';  // hidden route
const API_KEY = 'lab_key_0123456789abcdef';
""", ctype="application/javascript")

        elif path == "/internal/status":
            self._send(body=json.dumps({"status": "internal-ok"}),
                       ctype="application/json")

        elif path == "/robots.txt":
            self._send(body="User-agent: *\nDisallow: /debug\nDisallow: /admin",
                       ctype="text/plain")

        elif path.startswith("/uploads/"):
            target = os.path.normpath(os.path.join(WWW, path.lstrip("/")))
            try:
                with open(target, "rb") as fh:
                    data = fh.read()
            except OSError:
                self._send(404, "<html><body>no such upload</body></html>")
                return
            ctype = ("image/svg+xml" if target.endswith(".svg")
                     else "text/html" if target.endswith((".html", ".htm"))
                     else "application/octet-stream")
            self._send(body=data, ctype=ctype)

        elif path == "/admin":
            self._send(403, "<html><body>Forbidden</body></html>")

        elif path == "/login":
            self._send(body="""<html><body><form method="POST" action="/login">
<input name="username"><input name="password" type="password">
<button>login</button></form></body></html>""")

        elif path == "/reset":
            # password-reset form that builds its action URL from Host /
            # X-Forwarded-Host - the classic host-header poisoning shape
            host = self.headers.get("X-Forwarded-Host") or \
                self.headers.get("Host") or "lab"
            self._send(body=f"""<html><body><h1>Reset password</h1>
<form method="POST" action="http://{host}/reset">
<input name="email"><button>send reset link</button>
</form></body></html>""")

        else:
            self._send(404, "<html><body>not found</body></html>")

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/login":
            b = self._body()
            u, pw = b.get("username", ""), b.get("password", "")
            try:
                row = self.db.execute(
                    f"SELECT id, role FROM users WHERE username = '{u}' "
                    f"AND password = '{pw}'").fetchone()
            except sqlite3.Error as exc:
                self._send(500, f"sqlite3.OperationalError: {exc}",
                           ctype="text/plain")
                return
            if row:
                self._send(body=f"<html><body>Welcome {u}! role={row[1]}"
                                f"</body></html>")
            else:
                self._send(body="<html><body>Login failed.</body></html>")
            return
        if path == "/xml":
            # simulated XXE-prone parser: external entities get "resolved"
            # against the fake filesystem / a canned metadata service
            n = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(n).decode("utf-8", "replace") if n else ""
            m = re.search(r'<!ENTITY\s+(\w+)\s+SYSTEM\s+["\']([^"\']+)["\']',
                          raw)
            out = raw
            if m:
                name, uri = m.group(1), m.group(2)
                if uri.startswith("file://"):
                    target = os.path.normpath(
                        os.path.join(FAKEFS, uri[7:].lstrip("/")))
                    try:
                        with open(target, encoding="utf-8",
                                  errors="replace") as fh:
                            content = fh.read(4096)
                    except OSError:
                        content = "[entity read failed]"
                elif uri.startswith("http"):
                    content = "ami-id\ninstance-id\nlocal-hostname\n"
                else:
                    content = ""
                out = raw.replace(f"&{name};", content)
            self._send(body=f"<response><echo>{out}</echo></response>",
                       ctype="application/xml")
            return
        if path == "/upload":
            # unsafe upload: stores attacker bytes under /uploads/ and
            # serves them back with a content type derived from extension
            n = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(n) if n else b""
            hdr_end = raw.find(b"\r\n\r\n")
            fname_m = re.search(rb'filename="([^"]+)"',
                                raw[:hdr_end if hdr_end >= 0 else 400])
            if hdr_end < 0 or not fname_m:
                self._send(400, "no file", ctype="text/plain")
                return
            fname = os.path.basename(
                fname_m.group(1).decode("utf-8", "replace"))
            content = raw[hdr_end + 4:]
            end = content.rfind(b"\r\n--")
            if end >= 0:
                content = content[:end]
            os.makedirs(os.path.join(WWW, "uploads"), exist_ok=True)
            with open(os.path.join(WWW, "uploads", fname), "wb") as fh:
                fh.write(content)
            self._send(body=json.dumps({"url": f"/uploads/{fname}"}),
                       ctype="application/json")
            return
        if path == "/api/login":
            # simulated NoSQL query: a dict password is treated as a query
            # operator document (mongo-style $ne/$gt/$regex -> always true)
            b = self._body()
            u = b.get("username", "") if isinstance(b, dict) else ""
            pw = b.get("password", "") if isinstance(b, dict) else ""
            if isinstance(pw, dict) and any(str(k).startswith("$")
                                            for k in pw):
                row = self.db.execute(
                    "SELECT role FROM users WHERE username = ?",
                    (u,)).fetchone()
                self._send(body=json.dumps(
                    {"ok": True, "role": row[0] if row else "user"}),
                    ctype="application/json")
                return
            row = self.db.execute(
                "SELECT role FROM users WHERE username = ? AND password = ?",
                (u, str(pw))).fetchone()
            if row:
                self._send(body=json.dumps({"ok": True, "role": row[0]}),
                           ctype="application/json")
            else:
                self._send(401, json.dumps({"ok": False}),
                           ctype="application/json")
            return
        if path == "/graphql":
            b = self._body()
            q = b.get("query", "") if isinstance(b, dict) else ""
            if "__schema" in q:
                self._send(body=json.dumps({"data": {"__schema": {
                    "queryType": {"name": "Query"},
                    "mutationType": None,
                    "types": [{"name": "User", "fields": [
                        {"name": "id"}, {"name": "username"},
                        {"name": "password"}]}]}}}), ctype="application/json")
            else:
                self._send(body=json.dumps({"data": {}}),
                           ctype="application/json")
            return
        self._send(404, "<html><body>not found</body></html>")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Allow", "GET, POST, OPTIONS")
        origin = self.headers.get("Origin")
        if origin:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Methods",
                             "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Content-Length", "0")
        self.end_headers()


def make_server(port: int = 0):
    Handler.db = _init_db()
    os.makedirs(WWW, exist_ok=True)
    os.makedirs(os.path.join(FAKEFS, "etc"), exist_ok=True)
    with open(os.path.join(WWW, "welcome.txt"), "w") as fh:
        fh.write("welcome to labshop\n")
    with open(os.path.join(WWW, "app.py.bak"), "w") as fh:
        fh.write("# backup of app.py - DB_PASSWORD=labdbpass123\n")
    with open(os.path.join(FAKEFS, "etc", "passwd"), "w") as fh:
        fh.write("root:x:0:0:root:/root:/bin/bash\n"
                 "daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\n")
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    return srv


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8777
    srv = make_server(port)
    print(f"lab vulnerable app on http://127.0.0.1:{srv.server_address[1]}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.shutdown()
