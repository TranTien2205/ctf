#!/usr/bin/env python3
"""vulnapp - a deliberately vulnerable lab target for Argus.

Stdlib-only (works anywhere Python runs, including Windows). Exposes one bug
per Argus probe family so the agent can be exercised end-to-end offline:

    GET  /                     index with links + a search form
    GET  /search?q=            reflected XSS (unescaped reflection)
    GET  /item?id=             SQLi (error-based + boolean-blind, sqlite)
    GET  /stock?sku=           SQLi detectable only via an OR true/false pair
                               (AND arms all return the empty page)
    POST /login                SQLi auth bypass (' OR '1'='1), user-enum errors
    POST /login2               user-enum via timing (uniform error text)
    POST /login3               rate-limited login: 429 after 5 fails/user
    GET  /ping?host=           command injection (sleep separators)
    GET  /hello?name=          SSTI ({{expr}} arithmetic evaluation)
    GET  /download?file=       path traversal / file read
    GET  /redirect?next=       open redirect + CRLF header injection
    GET  /safedirect?next=     filtered redirect (//host bypass)
    hdr  X-Original-URL: /admin  middleware ACL bypass
                               (Location value is not sanitized)
    GET  /api/user/<id>        IDOR (any id served)
    POST /api/register         mass-assignment: stores every sent field
    POST /api/order            IDOR in a JSON body ({"order": N} served)
    GET  /fetch?url=           SSRF (real server-side fetch, 3s timeout)
    POST /xml                  XXE (simulated external-entity resolution)
    POST /api/login            NoSQLi ($ne/$gt operator password bypass)
    POST /upload, GET /uploads file upload served back with active content-type
    GET  /redeem               race condition (unlocked check-then-act)
    GET  /import?data=         deserialization (magic bytes -> parser error)
    GET  /cached               cache poisoning (X-Forwarded-Host unkeyed)
    GET  /profile[/x.css]      cache deception (path confusion)
    GET+POST /api/config       prototype pollution (__proto__ merge)
    POST /api/config2          proto pollution via constructor.prototype
    GET  /api/data             CORS: reflects Origin + credentials
    GET  /api/me               JWT (HS256, weak secret 'secret123')
    GET  /token?user=          issues a JWT
    GET  /.git/HEAD, /.env, /debug  info disclosure
    POST /desync, /desync-cl, /desync-obf, /desync-none
                               request smuggling sims: CL.TE, TE.CL,
                               obfuscated-TE differential, agreed framing
    GET  /ws                   websocket handshake (101)

Run:  python lab/vulnapp.py [port]
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import re
import shlex
import shutil
import sqlite3
import struct
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# The lab tree is seeded fresh per server under a runtime workdir - it
# must NOT live beside this module: installed into site-packages the
# package dir may be read-only, and a shared on-disk tree bleeds state
# (uploads, registered users) between runs. make_server() points these
# at a fresh tempdir unless the caller supplies one.
WWW = ""
FAKEFS = ""
JWT_SECRET = "secret123"

# ---------------------------------------------------------------- setup

def _init_db() -> sqlite3.Connection:
    db = sqlite3.connect(":memory:", check_same_thread=False)
    db.execute("CREATE TABLE items (id INTEGER, name TEXT, price REAL)")
    db.execute("CREATE TABLE users (id INTEGER, username TEXT, password TEXT, role TEXT)")
    db.execute("CREATE TABLE secrets (flag TEXT)")
    db.execute("CREATE TABLE stock (sku TEXT, name TEXT, visible INTEGER)")
    db.executemany("INSERT INTO items VALUES (?,?,?)",
                   [(1, "widget", 9.99), (2, "gadget", 19.99), (3, "sprocket", 4.50)])
    db.executemany("INSERT INTO stock VALUES (?,?,?)",
                   [("A-2", "widget xl", 1), ("A-3", "gadget pro", 1)])
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


_EXEC_NOARGS = {"id", "whoami", "uname", "hostname", "pwd"}
_EXEC_WITHARGS = {"echo", "cat"}
_EXEC_ALLOW = _EXEC_NOARGS | _EXEC_WITHARGS
# One GET must not become thousands of fork/execs: a 64 KB value of `;id`
# produced ~21,500 of them on one thread.
_EXEC_MAX_SEGMENTS = 8

def _injected_commands(value: str) -> list[str]:
    """The command segments an injected parameter carries, loosely as a shell
    would split them. Segment 0 is the host argument itself, not a command.

    Bounded at _EXEC_MAX_SEGMENTS: a real shell would run them all, and this
    is a lab that must not be a way to pin the operator's own machine.
    """
    text = str(value or "")[:8192].replace("%0a", "\n")
    segments = [a or b for a, b in
                re.findall(r"\$\(([^)]*)\)|`([^`]*)`", text)]
    outside = re.sub(r"\$\([^)]*\)|`[^`]*`", "", text)
    segments += re.split(r"[;&|\n]+", outside)[1:]
    out = []
    for segment in segments:
        segment = segment.strip().strip('"').strip("'").split("#")[0].strip()
        # a NUL anywhere raises ValueError out of shlex/subprocess, and the
        # request died with no response at all
        segment = segment.replace("\x00", "")
        if segment:
            out.append(segment)
        if len(out) >= _EXEC_MAX_SEGMENTS:
            break
    return out

def _lab_exec(command: str) -> str:
    try:
        parts = shlex.split(command)
    except ValueError:
        return f"sh: {command}: syntax error"
    if not parts:
        return ""
    name = os.path.basename(parts[0])
    if name not in _EXEC_ALLOW:
        return f"sh: {parts[0]}: command not found"
    # basename("/bin/rm") is "rm" and refused, but basename("./id") is "id" and
    # shutil.which would resolve it against PATH, not against the path given -
    # so a leading path component is simply rejected.
    if parts[0] != name:
        return f"sh: {parts[0]}: command not found"
    if name in _EXEC_NOARGS and len(parts) > 1:
        return f"{name}: extra operand '{parts[1]}'"
    if name == "echo":
        return " ".join(parts[1:])
    if name == "cat":
        if len(parts) < 2:
            return ""
        target = os.path.normpath(parts[1].replace("\x00", "")).lstrip("/\\")
        path = os.path.join(FAKEFS, target)
        # realpath, and compare against the directory WITH its separator: a
        # prefix test lets /x/fake-other through when the root is /x/fake, and
        # a symlink inside the tree pointed anywhere at all.
        # normcase, because on NT the comparison is case-insensitive and a
        # plain startswith refuses `FAKE\x` inside root `fake` - failing closed,
        # but refusing a legitimate read the rce/lfi demo depends on. Verified
        # against ntpath semantics rather than assumed.
        root = os.path.normcase(os.path.realpath(FAKEFS))
        real = os.path.normcase(os.path.realpath(path))
        if real != root and not real.startswith(root + os.sep):
            return f"cat: {parts[1]}: Permission denied"
        try:
            with open(path, encoding="utf-8", errors="replace") as fh:
                return fh.read(4096)
        except OSError:
            return f"cat: {parts[1]}: No such file or directory"
    exe = shutil.which(name)
    if not exe:
        return f"sh: {name}: command not found"
    try:
        done = subprocess.run([exe, *parts[1:]], capture_output=True,
                              text=True, timeout=3)
    except (OSError, subprocess.SubprocessError):
        return f"sh: {name}: cannot execute"
    return (done.stdout or done.stderr or "")[:4096]

_FAKE_METADATA = (
    b'{"ami-id":"ami-0lab00000000","instance-id":"i-0labfixture0000",'
    b'"local-ipv4":"10.0.0.17","local-hostname":"ip-10-0-0-17.lab.internal",'
    b'"iam":{"info":{"InstanceProfileArn":'
    b'"arn:aws:iam::000000000000:instance-profile/lab-role"}}}')


class Handler(BaseHTTPRequestHandler):
    db = None
    server_version = "LabVuln/1.0"
    protocol_version = "HTTP/1.1"  # keep-alive: needed for desync exercise

    def finish(self):
        # A socket closed with unread inbound data makes Windows send RST
        # instead of FIN, which can race away a just-written reply - the
        # desync lab's poisoned-response signal is exactly that case.
        # Drain the kernel buffer first so teardown is a clean FIN.
        try:
            self.connection.setblocking(0)
            while self.connection.recv(65536):
                pass
        except (BlockingIOError, OSError):
            pass
        finally:
            super().finish()

    # -- helpers ---------------------------------------------------------
    _WS_MAX_FRAME = 4096

    def _ws_echo_once(self) -> None:
        """Read one masked client frame and echo its payload back.

        Enough to make the channel provable and no more: one frame, bounded,
        then a close. A lab that only completes the handshake cannot show
        that the channel answers, which is the half of the finding that
        matters - an endpoint that 101s and then says nothing is not a
        hijackable channel.
        """
        import struct
        sock = self.connection
        deadline = time.monotonic() + 5.0   # the WHOLE frame, not one recv:
        # settimeout bounds a single read, so a client feeding one byte at a
        # time held a handler thread indefinitely. Test-only code, but it
        # runs in the selftest's own process.

        def _expired() -> bool:
            return time.monotonic() > deadline

        try:
            sock.settimeout(3.0)
            head = sock.recv(2)
            if len(head) < 2:
                return
            opcode = head[0] & 0x0F
            masked = bool(head[1] & 0x80)
            length = head[1] & 0x7F
            if length == 126:
                length = struct.unpack(">H", sock.recv(2))[0]
            elif length == 127:
                length = struct.unpack(">Q", sock.recv(8))[0]
            if length > self._WS_MAX_FRAME:
                return
            mask = sock.recv(4) if masked else b""
            payload = b""
            while len(payload) < length:
                if _expired():
                    return
                chunk = sock.recv(length - len(payload))
                if not chunk:
                    break
                payload += chunk
            if masked and mask:
                payload = bytes(b ^ mask[i % 4]
                                for i, b in enumerate(payload))
            if opcode == 0x8:                      # client said close
                sock.sendall(b"\x88\x00")
                return
            body = b"echo: " + payload[:self._WS_MAX_FRAME]
            frame = bytearray([0x81])              # FIN + text, unmasked
            if len(body) < 126:
                frame.append(len(body))
            else:
                frame.append(126)
                frame += struct.pack(">H", len(body))
            frame += body
            sock.sendall(bytes(frame))
            sock.sendall(b"\x88\x00")             # and close politely
        except (OSError, struct.error, IndexError):
            return
        finally:
            try:
                sock.settimeout(None)
            except OSError:
                pass

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

    def _drain_leftover(self):
        """Consume any bytes the other framing left in the stream, so the
        next request line starts clean. read1() serves buffered bytes
        without a raw read; on a non-blocking socket an empty read raises
        instead of hanging - deterministic on every platform."""
        self.connection.setblocking(0)
        try:
            while self.rfile.read1(65536):
                pass
        except (BlockingIOError, OSError):
            pass
        finally:
            self.connection.setblocking(1)

    def _body(self):
        try:
            n = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            n = 0
        # a huge declared length just waits for bytes that never come -
        # cap so a hostile client cannot pin the handler thread forever
        n = min(n, 1_000_000)
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

        # middleware honours X-Original-URL/X-Rewrite-URL while the edge
        # 403s /admin directly - the classic header-based ACL bypass
        xou = (self.headers.get("X-Original-URL")
               or self.headers.get("X-Rewrite-URL"))
        if xou == "/admin":
            self._send(body="<html><body>admin panel: users=3 "
                            "cfg=release-1</body></html>")
            return

        if path == "/":
            self._send(body="""<html><head><title>LabShop</title></head><body>
<h1>LabShop</h1>
<form action="/search" method="GET"><input name="q"><button>search</button></form>
<form action="/settings/update-email" method="GET"><input name="email"><button>save</button></form>
<ul><li><a href="/item?id=1">item 1</a></li>
<li><a href="/redirect?next=/">go</a></li>
<li><a href="/download?file=welcome.txt">readme</a></li>
<li><a href="/hello?name=guest">hello</a></li>
<li><a href="/ping?host=127.0.0.1">ping diag</a></li></ul>
<script src="/static/app.js"></script>
<!-- TODO: remove /debug before production -->
</body></html>""")

        elif path == "/weird-links":
            # hostile target-controlled URLs: crawl/js_recon must skip
            # rather than die on hrefs urljoin itself rejects
            self._send(body="""<html><body>
<a href="http://[bad">bad ipv6</a>
<a href="/item?id=2">item 2</a>
<form action="http://[bad"><input name="x"></form>
<script src="//[bad/x.js"></script>
<script src="/static/app.js"></script>
</body></html>""")

        elif path == "/bad-headers":
            # planted hygiene case: headers PRESENT but values invalid /
            # self-disabling - checkbox audits that only test presence
            # miss every one of these
            self._send(body="<html><body>ok</body></html>", headers={
                "X-Frame-Options": "ALLOWALL",
                "X-Content-Type-Options": "false",
                "Strict-Transport-Security": "max-age=0",
                "Referrer-Policy": "unsafe-url",
                "Content-Security-Policy": "default-src *",
            })

        elif path == "/graphql":
            # accepts GET ?query= too - many real graphql servers do
            q = p.get("query", "")
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

        elif path == "/product":
            # numeric-context sqli: id is NOT quoted, errors are swallowed,
            # so only an unquoted boolean pair differentiates
            i = p.get("id", "1")
            try:
                rows = self.db.execute(
                    f"SELECT name, price FROM items WHERE id = {i}").fetchall()
            except sqlite3.Error:
                rows = []
            if rows:
                out = "".join(f"<li>{n} - ${pr}</li>" for n, pr in rows)
                self._send(body=f"<html><body><ul>{out}</ul></body></html>")
            else:
                self._send(body="<html><body>No product.</body></html>")

        elif path == "/stock":
            # OR-pair sqli: an AND-tail filter means baseline AND true/false
            # all return empty; only the OR '1'='1 arm returns rows.
            # Errors are swallowed so the error channel stays dark.
            i = p.get("sku", "1")
            try:
                rows = self.db.execute(
                    f"SELECT name FROM stock WHERE sku = '{i}' "
                    "AND visible = 1").fetchall()
            except sqlite3.Error:
                rows = []
            if rows:
                out = "".join(f"<li>{n}</li>" for n, in rows)
                self._send(body=f"<html><body><ul>{out}</ul></body></html>")
            else:
                self._send(body="<html><body>No stock.</body></html>")

        elif path == "/ping":
            host = p.get("host", "")
            m = re.search(r"sleep\s+(\d+)", host)
            sql = (re.search(r"SLEEP\((\d+)\)", host) or
                   re.search(r"pg_sleep\((\d+)\)", host) or
                   re.search(r"WAITFOR DELAY '0:0:(\d+)'", host))
            bench = re.search(r"BENCHMARK\((\d+)", host)
            if re.search(r"[;&|`$(]", host) and m:
                time.sleep(min(int(m.group(1)), 8))
                self._send(body="<html><body>PING ok</body></html>")
            elif sql:
                time.sleep(min(int(sql.group(1)), 8))
                self._send(body="<html><body>PING ok</body></html>")
            elif bench:
                # heavy query: iterations, not seconds - ~1s per million
                time.sleep(min(int(bench.group(1)) // 1_000_000, 8))
                self._send(body="<html><body>PING ok</body></html>")
            elif re.search(r"[;&|`$(]", host) or "%0a" in host:
                # real execution, allowlisted and shell-free (see _lab_exec)
                outputs = [_lab_exec(c) for c in _injected_commands(host)]
                outputs = [o for o in outputs if o]
                if outputs:
                    body = "\n".join(outputs)
                    self._send(body="<html><body><pre>PING 127.0.0.1: 4 "
                                    f"packets, 0% loss\n{body}</pre></body></html>")
                else:
                    self._send(500, "<html><body>sh: syntax error</body></html>")
            else:
                self._send(body=f"<html><body>PING {host}: 4 packets, 0% loss"
                                f"</body></html>")

        elif path == "/profile" or path.startswith("/profile/"):
            # path confusion: the same private page resolves under any
            # suffix - a static-extension URL is cacheable by a CDN
            body = ("<html><body>Profile: bob &lt;bob@lab.local&gt; "
                    "ssn=123-45-6789</body></html>")
            self._send(body=body)

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

        elif path == "/hello2":
            # planted both-present SSTI: the page renders {{expr}} AND
            # echoes the raw input (error-page style) - a detector that
            # only counts evals when the payload is absent misses this
            name = p.get("name", "guest")
            def render2(m):
                expr = m.group(1)
                if re.fullmatch(r"[\d\s+\-*/().]+", expr):
                    try:
                        return str(eval(expr, {"__builtins__": {}}, {}))
                    except Exception:
                        return m.group(0)
                return m.group(0)
            rendered = re.sub(r"\{\{(.*?)\}\}", render2, name)
            self._send(body=f"<html><body>Hello, {rendered}!"
                            f" <i>you typed: {name}</i></body></html>")

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

        elif path == "/safedirect":
            # naive filter: only "local" paths allowed - but //host is a
            # protocol-relative EXTERNAL url that still starts with /
            nxt = p.get("next", "/")
            if nxt.startswith("/"):
                self._send(302, "<html><body>redirecting</body></html>",
                           headers={"Location": nxt})
            else:
                self._send(400, "<html><body>external urls not allowed"
                                "</body></html>")

        elif path == "/jsredirect":
            # client-side open redirect: no Location header at all
            nxt = p.get("next", "/")
            self._send(body=f"<html><head><meta http-equiv='refresh' "
                       f"content='0;url={nxt}'></head><body>go</body></html>")

        elif path == "/fetch":
            # A real server-side fetch, bounded the same way /ping is. It used
            # to pass the parameter straight to urlopen, so
            # `?url=file:///etc/passwd` returned the OPERATOR'S real
            # /etc/passwd - the same line the `cat` allowlist exists to
            # prevent, through a different door. http(s) to loopback only;
            # the cloud-metadata address answers from a fixture so the SSRF
            # demonstration still works without touching a real network.
            u = p.get("url", "")
            parsed = urllib.parse.urlparse(u)
            host = (parsed.hostname or "").lower()
            if host in ("169.254.169.254", "metadata.google.internal"):
                self._send(body=b"FETCHED:\n" + _FAKE_METADATA)
            elif parsed.scheme not in ("http", "https"):
                self._send(502, f"fetch error for {u}: unsupported scheme "
                                f"{parsed.scheme!r}", ctype="text/plain")
            elif host not in ("127.0.0.1", "localhost", "::1", "0.0.0.0",
                              "[::1]"):
                self._send(502, f"fetch error for {u}: only loopback is "
                                "reachable from this lab", ctype="text/plain")
            else:
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

        elif path == "/.env":
            self._send(body="DB_HOST=db.internal\nDB_PASSWORD=hunter2\n"
                            "SECRET_KEY=lab-secret-0123\n", ctype="text/plain")

        elif path == "/ws-strict":
            # the same endpoint with the check in place: a foreign Origin is
            # refused before the upgrade. Present so the probe and the gate
            # can both be shown refusing a channel that is not hijackable.
            origin = self.headers.get("Origin", "")
            host = self.headers.get("Host", "")
            o_host = origin.split("//", 1)[-1].split("/", 1)[0] if origin \
                else ""
            if origin and o_host != host:
                self._send(403, body="origin not allowed")
                return
            key = self.headers.get("Sec-WebSocket-Key", "")
            accept = base64.b64encode(hashlib.sha1(
                (key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()
            ).digest()).decode()
            self.send_response(101, "Switching Protocols")
            self.send_header("Upgrade", "websocket")
            self.send_header("Connection", "Upgrade")
            self.send_header("Sec-WebSocket-Accept", accept)
            self.end_headers()
            self._ws_echo_once()


        elif path == "/ws":
            # RFC 6455 handshake: a live ws endpoint answers 101 + Accept
            key = self.headers.get("Sec-WebSocket-Key", "")
            accept = base64.b64encode(hashlib.sha1(
                (key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()
            ).digest()).decode()
            # Deliberately broken: no Origin check at all. That is the bug -
            # any page on the internet can open this channel in the victim's
            # browser, with the victim's cookies, and read the answers.
            self.send_response(101, "Switching Protocols")
            self.send_header("Upgrade", "websocket")
            self.send_header("Connection", "Upgrade")
            self.send_header("Sec-WebSocket-Accept", accept)
            self.end_headers()
            self._ws_echo_once()

        elif path == "/static/app.js":
            self._send(body="""fetch('/api/user/1').then(r=>r.json());
const internal = '/internal/status';  // hidden route
const API_KEY = 'lab_key_0123456789abcdef';
const ws = new WebSocket('ws://127.0.0.1:9999/feed');
//# sourceMappingURL=app.js.map
""", ctype="application/javascript")

        elif path == "/static/app.js.map":
            # deployed sourcemap: original sources leak - a real-world find
            self._send(body=json.dumps({
                "version": 3,
                "sources": ["webpack://app/src/api.js",
                            "webpack://app/src/config.js"],
                "sourcesContent": [
                    "fetch('/api/admin/export').then(r => r.json());\n",
                    "export const client_secret = 'sm_secret_abcdef123456';\n",
                ],
            }), ctype="application/json")

        elif path in ("/desync", "/desync-cl", "/desync-none",
                      "/desync-obf"):
            self._send(200, "clean follow-up", ctype="text/plain")

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

        elif path == "/redeem/reset":
            # Test support, not part of the vulnerable surface. `/redeem` is
            # a one-time coupon held in a CLASS variable, so one test draining
            # it leaves every later test on the same server looking at an
            # endpoint with nothing to race for - which read as a verifier
            # regression until the counter was printed. Resetting is explicit
            # so the dependency is visible in the test that needs it.
            type(self)._coupons = 1
            self._send(body=json.dumps({"coupons": type(self)._coupons}),
                       ctype="application/json")


        elif path == "/redeem":
            # TOCTOU: check-then-act with no lock - concurrent requests all
            # pass the guard before the first commits the decrement
            if self._coupons > 0:
                time.sleep(0.15)      # race window: wide enough that an
                # 8-request burst overlaps even under test-suite load
                type(self)._coupons -= 1
                self._send(body=json.dumps(
                    {"ok": True, "left": type(self)._coupons}))
            else:
                self._send(409, json.dumps({"ok": False}),
                           ctype="application/json")

        elif path == "/import":
            # simulated vulnerable deserializer: magic-bytes payloads reach
            # the parser and produce framework error strings
            v = p.get("data", "")
            if v.startswith(("rO0AB", "O:", "a:", "c__builtin__",
                            "{", "!!", "\xac")):
                self._send(500, "java.io.InvalidClassException: filter "
                                "status - REJECTED", ctype="text/plain")
            else:
                self._send(body="imported: " + v[:80])

        elif path == "/api/config":
            cfg = dict(self._usercfg)
            cfg.update(type(self)._pp)    # polluted keys leak into every object
            self._send(body=json.dumps(cfg), ctype="application/json")

        elif path == "/cached":
            # cache keyed on path only: X-Forwarded-Host is unkeyed input
            if path not in self._cache:
                host = (self.headers.get("X-Forwarded-Host")
                        or self.headers.get("Host") or "lab")
                self._cache[path] = (f"<html><body>profile: "
                                     f"http://{host}/me</body></html>")
            self._send(body=self._cache[path])

        elif path == "/admin":
            self._send(403, "<html><body>Forbidden</body></html>")

        elif path == "/login":
            # session cookie without SameSite/HttpOnly - weak-cookie CSRF
            # surface plus a passive PHP framework hint for fingerprint()
            self._send(headers={"Set-Cookie": "PHPSESSID=lab5ess10n; Path=/"},
                       body="""<html><body><form method="POST" action="/login">
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
        if path in ("/desync", "/desync-cl", "/desync-none", "/desync-obf"):
            # Simulate a desync back-end:
            #   /desync      - TE-honoring behind a CL-honoring front (CL.TE)
            #   /desync-cl   - CL-honoring behind a TE-honoring front (TE.CL)
            #   /desync-none - agreed framing: reads its body fully, then
            #                  drains leftovers - a clean control endpoint
            #   /desync-obf  - front-end normalizes CANONICAL TE away (reads
            #                  CL + drains), but an OBFUSCATED TE slips
            #                  through to a chunked parser - the real-world
            #                  obfuscation differential
            # Whatever framing is NOT consumed stays in the stream and
            # poisons the next request line on this connection.
            te = "chunked" in (self.headers.get("Transfer-Encoding") or "")
            if path == "/desync-obf":
                te_raw = (self.headers.get("Transfer-Encoding") or "").strip()
                canonical = te_raw.lower() == "chunked"
                n = int(self.headers.get("Content-Length") or 0)
                if canonical or not te:
                    if n:
                        self.rfile.read(n)   # front normalized to CL
                    self._drain_leftover()
                    self._send(200, "clean", ctype="text/plain")
                    return
                # obfuscated TE (xchunked, 'chunked ', ...) reaches a lenient
                # chunked parser -> falls through to the chunked reader
            if te and path == "/desync-cl":
                n = int(self.headers.get("Content-Length") or 0)
                self.rfile.read(n)  # CL honored, TE ignored -> leftover stays
                self._send(200, "cl ok", ctype="text/plain")
                return
            if te and path == "/desync-none":
                n = int(self.headers.get("Content-Length") or 0)
                if n:
                    self.rfile.read(n)          # honor CL
                else:
                    while True:                  # or honor chunked
                        line = self.rfile.readline()
                        try:
                            size = int(line.strip() or b"0", 16)
                        except ValueError:
                            size = 0
                        if size == 0:
                            while self.rfile.readline() not in \
                                    (b"\r\n", b"\n", b""):
                                pass
                            break
                        self.rfile.read(size)
                        self.rfile.readline()
                # then drain whatever the OTHER framing left behind, so the
                # next request line starts clean - front and back agree here
                self._drain_leftover()
                self._send(200, "clean", ctype="text/plain")
                return
            if te:
                while True:
                    line = self.rfile.readline()
                    try:
                        size = int(line.strip() or b"0", 16)
                    except ValueError:
                        size = 0
                    if size == 0:
                        while self.rfile.readline() not in (b"\r\n", b"\n", b""):
                            pass  # consume trailer until the blank line
                        break
                    self.rfile.read(size)
                    self.rfile.readline()  # CRLF after chunk data
                self._send(200, "chunked ok", ctype="text/plain")
            else:
                self._body()  # CL path consumes the whole body
                self._send(200, "cl ok", ctype="text/plain")
            return
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
                # user-enumeration vuln: the error reveals whether the
                # username exists before the password is even checked
                exists = self.db.execute(
                    "SELECT 1 FROM users WHERE username = ?",
                    (u,)).fetchone()
                if exists:
                    self._send(body="<html><body>Wrong password for "
                                    f"{u}.</body></html>")
                else:
                    self._send(body="<html><body>Unknown user."
                                    "</body></html>")
            return
        if path == "/login2":
            # uniform error text but a real account runs the (expensive)
            # password verify - timing-only enumeration channel
            b = self._body()
            u, pw = b.get("username", ""), b.get("password", "")
            exists = self.db.execute(
                "SELECT 1 FROM users WHERE username = ?",
                (u,)).fetchone()
            if exists:
                time.sleep(0.4)   # simulated bcrypt verify
                if pw == "hunter2":
                    self._send(body="<html><body>Welcome!</body></html>")
                    return
            self._send(body="<html><body>Invalid credentials.</body></html>")
            return
        if path == "/login3":
            # rate-limited login: after 5 failed attempts on one username
            # the account is locked - exercises probe_lockout's positive
            # path (login2 is uniform-error, login is unthrottled)
            b = self._body()
            u = b.get("username", "")
            attempts = type(self)._lockout.get(u, 0)
            if attempts >= 5:
                self._send(429, "<html><body>Account locked - too many "
                                "attempts, try again later.</body></html>")
                return
            type(self)._lockout[u] = attempts + 1
            self._send(body="<html><body>Invalid credentials.</body></html>")
            return
        if path == "/xml":
            # simulated XXE-prone parser: external entities get "resolved"
            # against the fake filesystem / a canned metadata service
            n = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(n).decode("utf-8", "replace") if n else ""
            m = re.search(r'<!ENTITY\s+(\w+)\s+SYSTEM\s+["\']([^"\']+)["\']',
                          raw)
            xi = re.search(
                r'<xi:include[^>]*href=["\']([^"\']+)["\'][^>]*>', raw)
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
            elif xi:
                # XInclude: the classic DOCTYPE-filter bypass - include
                # elements resolve without any entity declaration
                uri = xi.group(1)
                if uri.startswith("file://"):
                    target = os.path.normpath(
                        os.path.join(FAKEFS, uri[7:].lstrip("/")))
                    try:
                        with open(target, encoding="utf-8",
                                  errors="replace") as fh:
                            content = fh.read(4096)
                    except OSError:
                        content = "[include read failed]"
                else:
                    content = ""
                out = raw.replace(xi.group(0), content)
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
        if path == "/api/config":
            # vulnerable merge: __proto__ keys land on the shared prototype
            b = self._body()
            if isinstance(b, dict):
                for k, v in b.items():
                    if k == "__proto__" and isinstance(v, dict):
                        type(self)._pp.update(v)
                    elif (k == "constructor" and isinstance(v, dict)
                          and isinstance(v.get("prototype"), dict)):
                        type(self)._pp.update(v["prototype"])
                    else:
                        self._usercfg[k] = v
            self._send(body=json.dumps({"merged": True}),
                       ctype="application/json")
            return
        if path == "/api/config2":
            # __proto__ is "filtered" but constructor.prototype still
            # reaches the same shared prototype - the classic bypass
            b = self._body()
            if isinstance(b, dict):
                for k, v in b.items():
                    if (k == "constructor" and isinstance(v, dict)
                            and isinstance(v.get("prototype"), dict)):
                        type(self)._pp.update(v["prototype"])
                    elif k != "__proto__":
                        self._usercfg[k] = v
            self._send(body=json.dumps({"merged": True}),
                       ctype="application/json")
            return
        if path == "/api/login":
            # simulated NoSQL query: a dict password is treated as a query
            # operator document (mongo-style $ne/$gt/$regex -> always true)
            b = self._body()
            u = b.get("username", "") if isinstance(b, dict) else ""
            pw = b.get("password", "") if isinstance(b, dict) else ""
            # urlencoded PHP-array syntax: password[$ne]=x parses to the
            # same operator document on a lenient backend
            form_ops = [k for k in b
                        if re.match(r"^\w+\[\$\w+\]$", str(k))]
            if form_ops and not isinstance(pw, dict):
                pw = {re.sub(r"^\w+\[|\]$", "", form_ops[0]): b[form_ops[0]]}
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
        if path == "/api/register":
            # mass-assignment vuln: the endpoint stores EVERY field the
            # caller sends - including role/admin - and echoes the record.
            # A whitelist implementation would drop unknown keys.
            b = self._body()
            if not isinstance(b, dict) or not b.get("username"):
                self._send(400, json.dumps({"error": "username required"}),
                           ctype="application/json")
                return
            rec = dict(b)
            rec["id"] = len(type(self)._registered) + 10
            type(self)._registered.append(rec)
            self._send(201, json.dumps({"created": rec}),
                       ctype="application/json")
            return
        if path == "/api/order":
            # POST-body IDOR: any order id is served regardless of caller
            b = self._body()
            oid = b.get("order", 0) if isinstance(b, dict) else 0
            try:
                oid = int(oid)
            except (TypeError, ValueError):
                oid = 0
            self._send(body=json.dumps(
                {"order": oid, "owner": f"user-{oid}",
                 "total": 10 + oid}), ctype="application/json")
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
        if path == "/graphql-strict":
            # introspection disabled BUT "did you mean" still leaks schema
            # names - the blind-enumeration surface graphql_introspect's
            # suggestion probe exists to flag
            b = self._body()
            q = b.get("query", "") if isinstance(b, dict) else ""
            if "__schema" in q:
                self._send(body=json.dumps({"errors": [{"message":
                    "introspection is disabled"}]}),
                    ctype="application/json")
            elif "namee" in q:
                self._send(body=json.dumps({"errors": [{"message":
                    'Cannot query field "namee" on type "User". '
                    'Did you mean "name"?'}]}), ctype="application/json")
            else:
                self._send(body=json.dumps({"data": {}}),
                           ctype="application/json")
            return
        self._send(404, "<html><body>not found</body></html>")

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Allow", "GET, POST, OPTIONS, TRACE")
        origin = self.headers.get("Origin")
        if origin:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Access-Control-Allow-Methods",
                             "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Credentials", "true")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def do_TRACE(self):
        # planted cross-site tracing vuln: TRACE echoes request headers
        # back - leaks HttpOnly cookies/auth headers to a reading XSS
        body = "".join(f"{k}: {v}\n" for k, v in self.headers.items())
        self.send_response(200)
        self.send_header("Content-Type", "message/http")
        self.send_header("Content-Length", str(len(body.encode())))
        self.end_headers()
        self.wfile.write(body.encode())


def make_server(port: int = 0, workdir: str = ""):
    global WWW, FAKEFS
    root = workdir or tempfile.mkdtemp(prefix="argus-lab-")
    WWW = os.path.join(root, "www")
    FAKEFS = os.path.join(root, "fakefs")
    Handler.db = _init_db()
    Handler._coupons = 1
    Handler._cache = {}
    Handler._lockout = {}
    Handler._registered = []
    Handler._pp = {}
    Handler._usercfg = {"theme": "dark", "lang": "en"}
    os.makedirs(WWW, exist_ok=True)
    os.makedirs(os.path.join(FAKEFS, "etc"), exist_ok=True)
    os.makedirs(os.path.join(FAKEFS, "windows"), exist_ok=True)
    with open(os.path.join(FAKEFS, "windows", "win.ini"), "w") as fh:
        fh.write("; for 16-bit app support\n[fonts]\n[extensions]\n")
    with open(os.path.join(WWW, "welcome.txt"), "w") as fh:
        fh.write("welcome to labshop\n")
    with open(os.path.join(WWW, "app.py.bak"), "w") as fh:
        fh.write("# backup of app.py - DB_PASSWORD=labdbpass123\n")
    with open(os.path.join(FAKEFS, "etc", "passwd"), "w") as fh:
        fh.write("root:x:0:0:root:/root:/bin/bash\n"
                 "daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\n")
    srv = _LabServer(("127.0.0.1", port), Handler)
    return srv


class _LabServer(ThreadingHTTPServer):
    daemon_threads = True

    def handle_error(self, request, client_address):
        # probes legitimately drop keep-alive sockets mid-read (redirect
        # scheme recovery, smuggle raw sends); that reset is test signal,
        # not a server bug - keep stderr for real handler crashes only
        if isinstance(sys.exc_info()[1], (ConnectionError, TimeoutError)):
            return
        super().handle_error(request, client_address)


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8777
    srv = make_server(port)
    print(f"lab vulnerable app on http://127.0.0.1:{srv.server_address[1]}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.shutdown()
