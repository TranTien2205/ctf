"""The dashboard's HTTP front end: `http.server`, standard library only.

This is a console on a pentester's machine. It starts scans, it reads
session artifacts, and it renders bytes a target chose, so it is written as
if whoever reaches the port is hostile:

* loopback by default, and a non-loopback bind needs an opt-in that the
  bind address itself cannot grant (see `serve`);
* a run id from the URL is validated and then resolved under the session
  root, so a path cannot leave it;
* request bodies are capped and read only after the length is checked;
* `report.html` embeds target-influenced bytes and is served with a
  `Content-Security-Policy: sandbox`, so it cannot run script in the
  dashboard's origin even when framed by it;
* errors are JSON. The stdlib's own `send_error` writes an HTML page with
  the request path interpolated into it, which is a reflected-XSS surface in
  the dashboard's origin, so it is replaced.
"""
from __future__ import annotations

import io
import ipaddress
import json
import os
import sys
import urllib.parse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable

from ..scope import ScopeError
from . import api
from .api import MAX_BODY, RunRegistry, TooManyRuns

#: The dashboard page another module writes; read per request so an edit
#: shows up without restarting the server. Capped: the server should refuse
#: a pathological file rather than read it into memory.
DASHBOARD_FILE = "dashboard.html"
MAX_DASHBOARD_BYTES = 4 << 20

#: How much of an over-sized body is read and discarded so the client can
#: finish writing and read the 413. Nothing is kept, so this costs one
#: 64 KiB buffer; beyond it the connection closes mid-write, which is the
#: right answer for a caller sending tens of megabytes.
DRAIN_LIMIT = 4 * MAX_BODY

#: The only media types a POST body may carry. A cross-site HTML form can
#: send `text/plain`, `application/x-www-form-urlencoded` or
#: `multipart/form-data` with no preflight, and `enctype="text/plain"`
#: serialises `<input name='{"mode":"lab","target":"http://x/","extra":"'
#: value='"}'>` to bytes that parse as JSON - measured, a POST /api/runs
#: with `Content-Type: text/plain` started a run, so JSON-only PARSING was
#: never the layer that stopped form CSRF. An absent Content-Type is
#: refused too: a cross-site `fetch` with a typeless Blob body sends none
#: and needs no preflight either.
_JSON_MEDIA_TYPES = ("application/json",)

#: Opt-in that a non-loopback bind needs on top of the bind address itself.
#: `serve()` used to derive `allow_remote` from the host it was asked to
#: bind, which auto-granted the override exactly when the gate would have
#: fired; the CLI has no flag for it, so this is the second channel.
ALLOW_REMOTE_ENV = "ARGUS_WEB_ALLOW_REMOTE"
_TRUTHY = ("1", "true", "yes", "on")

#: 421 Misdirected Request, as an int rather than `HTTPStatus`: this package
#: claims Python 3.10 and up, and the enum member is not in every version of
#: that range. `send_response` takes the int either way.
MISDIRECTED_REQUEST = 421

_BASE_HEADERS = (
    # a JSON body must never be sniffed into HTML by a browser
    ("X-Content-Type-Options", "nosniff"),
    ("Referrer-Policy", "no-referrer"),
    ("Cache-Control", "no-store"),
)

#: The dashboard ships as one in-tree file, so inline script and style are
#: first-party. Everything external is denied: a target-influenced string
#: that escapes the UI's escaping still cannot call home, and `connect-src
#: 'self'` keeps the page's fetches on this server.
_DASHBOARD_CSP = (
    "default-src 'none'; connect-src 'self'; img-src 'self' data:; "
    "font-src data:; style-src 'self' 'unsafe-inline'; "
    "script-src 'self' 'unsafe-inline'; frame-src 'self'; "
    "base-uri 'none'; form-action 'none'")

#: report.html is rendered from evidence, which means it contains bytes the
#: target chose. `sandbox` with no tokens is the strongest form of the
#: directive: scripts disabled, unique opaque origin, no form submission, so
#: the file cannot read or act in the dashboard's origin even inside an
#: iframe on the dashboard. `default-src 'none'` stops it fetching anything,
#: and `style-src 'unsafe-inline'` keeps the report's own inline stylesheet
#: working (CSS is what makes it readable, and sandbox already removes the
#: scripting that would make inline dangerous).
_REPORT_CSP = ("sandbox; default-src 'none'; style-src 'unsafe-inline'; "
               "img-src data:; frame-ancestors 'self'")


_LOOPBACK_NAMES = {"localhost", "localhost.localdomain", "127.0.0.1", "::1"}


def _is_loopback(host: str) -> bool:
    h = str(host or "").strip().strip("[]").lower()
    if h in ("localhost", "localhost.localdomain", ""):
        return True
    try:
        return ipaddress.ip_address(h).is_loopback
    except ValueError:
        return False


def _allow_remote_from_env() -> bool:
    """Whether the environment grants the non-loopback bind."""
    return (os.environ.get(ALLOW_REMOTE_ENV) or "").strip().lower() in _TRUTHY


def _check_bind_host(host: str, allow_remote: bool) -> None:
    """Refuse a non-loopback bind unless it was asked for explicitly.

    The default has to be loopback and the override has to be a separate
    argument, because this console starts scans and renders a target's bytes:
    binding it to an interface hands both to whoever reaches the port, and
    on an engagement that port is often on the same network as the target.
    """
    if not _is_loopback(host) and not allow_remote:
        raise ValueError(
            f"refusing to bind {host!r}: this console starts scans and has no "
            "authentication. Pass allow_remote=True (or set "
            f"{ALLOW_REMOTE_ENV}=1) to override, and do not do that on a "
            "network you share with the target")


class _WebServer(ThreadingHTTPServer):
    daemon_threads = True      # a stuck handler must not block shutdown
    allow_reuse_address = True
    registry: RunRegistry
    root: Path


class _Handler(BaseHTTPRequestHandler):
    server_version = "argus-web"
    sys_version = ""            # do not advertise the Python version
    protocol_version = "HTTP/1.1"
    #: a client that opens a socket and says nothing holds a thread until
    #: this fires
    timeout = 30

    # bound per server by make_server
    registry: RunRegistry
    root: Path
    quiet: bool = False
    loopback_bind: bool = True
    bound_host: str = "127.0.0.1"

    # -- who is allowed to talk to us -------------------------------------

    def _origin_ok(self) -> bool:
        """Refuse a request whose Host or Origin says it is not our page.

        Two attacks on a console that listens on loopback with no
        authentication:

        * DNS rebinding. A page on evil.example resolves that name to
          127.0.0.1 and becomes same-origin with this server, after which it
          can read findings and reports and start runs. The browser sends
          `Host: evil.example`, which is the only part of the request that
          carries the rebinding, so the Host header is checked against the
          address we actually bound.
        * A cross-site fetch. Those carry an `Origin` that is not ours. An
          absent Origin is allowed, because curl and urllib send none and
          the browser - the only client that can be made to attack us -
          always sends one on a cross-origin request.

        The HOST check, and only that one, is skipped for an explicit
        non-loopback bind: the operator named an interface and this module
        does not know which names are meant to reach it. Note what that
        leaves: `expected` below is built from the caller's own Host header,
        so with the Host check gone an attacker who sets both headers
        matches. That is why the remote bind now needs its own opt-in (see
        `serve`), and why the warning printed there names this check as one
        of the things it switches off.
        """
        raw_host = self.headers.get("Host") or ""
        if self.loopback_bind:
            if not raw_host:
                # HTTP/1.1 requires a Host, and on a loopback bind the Host
                # check IS the anti-rebinding check - skipping it for a
                # request that simply omits the header hands over the
                # bypass. Measured: `GET /api/health` with no Host -> 200.
                return False
            try:
                name = urllib.parse.urlsplit("//" + raw_host).hostname or ""
            except ValueError:
                return False
            if name.lower() not in _LOOPBACK_NAMES | {self.bound_host.lower()}:
                return False
        origin = self.headers.get("Origin")
        if origin:
            expected = {f"http://{raw_host}", f"https://{raw_host}"}
            if origin not in expected:
                return False
        return True

    def _reject_foreign(self) -> bool:
        if self._origin_ok():
            return False
        # 421: this request was sent to a server that is not the one the
        # client thinks it is talking to.
        self._json(MISDIRECTED_REQUEST,
                   {"error": "unexpected Host or Origin for this console"},
                   close=True)
        return True

    # -- plumbing ---------------------------------------------------------

    def log_message(self, fmt, *args):  # noqa: D102 - stdlib hook
        """One sanitized line. The stdlib version writes the raw request
        line to stderr, which lets a caller inject control characters into
        the operator's terminal."""
        if self.quiet:
            return
        try:
            text = fmt % args
        except Exception:
            text = str(fmt)
        clean = "".join(ch if 0x20 <= ord(ch) < 0x7f else "." for ch in text)
        sys.stderr.write(f"[argus-web] {clean[:200]}\n")

    def send_error(self, code, message=None, explain=None):  # noqa: D102
        """JSON errors, and never the caller's own bytes back.

        The stdlib builds an HTML page containing `self.path` and the parsed
        request line. Served from the dashboard's origin that is a reflected
        injection surface, and it is reached for malformed requests before
        any route of ours runs. The standard reason phrase is used rather
        than `message`, so nothing a caller sent is echoed at all.
        """
        try:
            phrase = self.responses.get(code, ("error",))[0]
        except Exception:
            phrase = "error"
        try:
            self._send(code, json.dumps({"error": str(phrase).lower()})
                       .encode(), "application/json; charset=utf-8",
                       close=True)
        except Exception:
            pass
        self.close_connection = True

    def _send(self, code: int, body: bytes, ctype: str,
              extra: tuple[tuple[str, str], ...] = (),
              close: bool = False) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        for key, value in _BASE_HEADERS:
            self.send_header(key, value)
        for key, value in extra:
            self.send_header(key, value)
        if close:
            self.close_connection = True
            self.send_header("Connection", "close")
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, code: int, payload: dict, close: bool = False) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self._send(code, body, "application/json; charset=utf-8", close=close)

    def _not_found(self) -> None:
        self._json(HTTPStatus.NOT_FOUND, {"error": "not found"})

    def _send_file(self, path: Path, ctype: str,
                   extra: tuple[tuple[str, str], ...] = ()) -> None:
        """Stream an artifact without reading it into memory.

        Content-Length comes from the open handle, not from a separate stat
        of the name, so the length and the bytes describe the same file even
        if a re-render replaces it mid-request.
        """
        try:
            fh = path.open("rb")
        except OSError:
            self._not_found()
            return
        with fh:
            try:
                size = fh.seek(0, io.SEEK_END)
                fh.seek(0)
            except OSError:
                self._not_found()
                return
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(size))
            for key, value in _BASE_HEADERS:
                self.send_header(key, value)
            for key, value in extra:
                self.send_header(key, value)
            self.end_headers()
            if self.command == "HEAD":
                return
            left = size
            while left > 0:
                chunk = fh.read(min(65536, left))
                if not chunk:
                    # the file shrank under us: the client sees a short read
                    # rather than a hung connection
                    self.close_connection = True
                    return
                self.wfile.write(chunk)
                left -= len(chunk)

    def _segments(self) -> tuple[list[str], dict[str, list[str]]]:
        """Path segments and query, each segment unquoted exactly once.

        Unquoting the whole path before splitting would turn `%2f` back into
        a separator and hand a traversal straight to the router, so the split
        happens on the raw path and each piece is decoded after.
        """
        split = urllib.parse.urlsplit(self.path)
        segs = [urllib.parse.unquote(s) for s in split.path.split("/") if s]
        return segs, urllib.parse.parse_qs(split.query, keep_blank_values=True)

    def _body(self) -> dict | None:
        """The POST body as a JSON object, or None after sending the error.

        Two gates run before a single byte is read: the media type, which
        is what refuses a cross-site form POST, and then the declared
        length - the point of a cap that reads first is nothing.
        """
        media = (self.headers.get("Content-Type") or "").split(";")[0]
        media = media.strip().lower()
        if media not in _JSON_MEDIA_TYPES and not media.endswith("+json"):
            # Checked before a byte is read, and before the length: this
            # is the layer that refuses a cross-site form POST (see
            # `_JSON_MEDIA_TYPES`). The Origin header cannot carry that
            # alone, because `_origin_ok` allows an absent Origin.
            self._json(HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
                       {"error": "body must be application/json; this "
                                 "console accepts no form content types"},
                       close=True)
            return None
        if "chunked" in (self.headers.get("Transfer-Encoding") or "").lower():
            # A chunked body has no declared length, so it cannot be capped
            # before it is read. This console has no need for one.
            self._json(HTTPStatus.LENGTH_REQUIRED,
                       {"error": "chunked bodies are not accepted; send "
                                 "Content-Length"}, close=True)
            return None
        raw_len = self.headers.get("Content-Length")
        if raw_len is None:
            self._json(HTTPStatus.LENGTH_REQUIRED,
                       {"error": "Content-Length required"}, close=True)
            return None
        try:
            length = int(raw_len)
        except (TypeError, ValueError):
            self._json(HTTPStatus.BAD_REQUEST,
                       {"error": "bad Content-Length"}, close=True)
            return None
        if length < 0:
            self._json(HTTPStatus.BAD_REQUEST,
                       {"error": "bad Content-Length"}, close=True)
            return None
        if length > MAX_BODY:
            # Drained in fixed-size chunks and discarded, up to a bound.
            # Replying without reading anything at all was the first version
            # and a test caught it: the client is still writing when the
            # socket closes, so it sees a broken pipe and never reads the
            # 413. Discarding in 64 KiB pieces keeps memory constant (the
            # point of the cap), the bound keeps the time finite, and the
            # socket timeout bounds a slow writer.
            left = min(length, DRAIN_LIMIT)
            try:
                while left > 0:
                    chunk = self.rfile.read(min(65536, left))
                    if not chunk:
                        break
                    left -= len(chunk)
            except OSError:
                pass
            self._json(HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                       {"error": f"body larger than {MAX_BODY} bytes"},
                       close=True)
            return None
        raw = self.rfile.read(length) if length else b""
        if len(raw) != length:
            self._json(HTTPStatus.BAD_REQUEST,
                       {"error": "truncated body"}, close=True)
            return None
        # JSON only, and no urlencoded form parsing anywhere. The layer
        # that stops a cross-site form POST is the Content-Type allowlist
        # above, NOT this parser: an `enctype="text/plain"` form can produce
        # a body that parses here, which was measured against this server
        # before the allowlist existed. A cross-origin JSON fetch is
        # preflighted, and this server answers with no CORS headers at all.
        try:
            data = json.loads(raw.decode("utf-8")) if raw else {}
        except (UnicodeDecodeError, ValueError):
            self._json(HTTPStatus.BAD_REQUEST,
                       {"error": "body must be UTF-8 JSON"})
            return None
        if not isinstance(data, dict):
            self._json(HTTPStatus.BAD_REQUEST,
                       {"error": "body must be a JSON object"})
            return None
        return data

    @staticmethod
    def _request_fields(data: dict) -> tuple[str, str, dict | None, str, list[str]]:
        """(mode, target, auth, extra, type_errors) from a request body.

        Type problems become validation errors rather than a 500: the shape
        arrives over HTTP from whatever reached the port.
        """
        errors: list[str] = []
        mode = data.get("mode")
        target = data.get("target")
        auth = data.get("auth")
        extra = data.get("extra", "")
        if not isinstance(mode, str):
            errors.append("mode must be a string")
            mode = ""
        if not isinstance(target, str):
            errors.append("target must be a string")
            target = ""
        if auth is not None and not isinstance(auth, dict):
            errors.append("auth must be an object or null")
            auth = None
        if auth is not None:
            auth = {k: v for k, v in auth.items() if isinstance(v, str)}
        if not isinstance(extra, str):
            errors.append("extra must be a string")
            extra = ""
        return mode, target, auth, extra, errors

    # -- routes -----------------------------------------------------------

    def do_GET(self) -> None:  # noqa: N802 - stdlib hook
        if self._reject_foreign():
            return
        segs, query = self._segments()
        if not segs:
            self._dashboard()
            return
        if segs[0] != "api":
            self._not_found()
            return
        rest = segs[1:]
        if rest == ["health"]:
            self._json(HTTPStatus.OK,
                       api.health(self.registry.model_configured))
            return
        if rest == ["runs"]:
            self._json(HTTPStatus.OK, {"runs": self.registry.runs()})
            return
        if len(rest) == 2 and rest[0] == "runs":
            self._one_run(rest[1])
            return
        if rest == ["findings"]:
            self._json(HTTPStatus.OK,
                       {"findings": api.findings_rows(self.root)})
            return
        if rest == ["reports"]:
            self._json(HTTPStatus.OK,
                       {"reports": api.reports_rows(self.root)})
            return
        if len(rest) == 2 and rest[0] == "reports":
            self._report(rest[1], (query.get("fmt") or ["md"])[0])
            return
        if rest == ["prompt"]:  # POST-only route
            self._json(HTTPStatus.METHOD_NOT_ALLOWED,
                       {"error": "method not allowed"})
            return
        self._not_found()

    def do_HEAD(self) -> None:  # noqa: N802 - stdlib hook
        """Routed through do_GET, which is what makes the HEAD branches in
        `_send` and `_send_file` reachable: without this hook the stdlib
        answered 501 for every HEAD (measured on /api/health) while those
        two branches read as support for it."""
        self.do_GET()

    @staticmethod
    def _get_only(segs: list[str]) -> bool:
        """Known paths this server serves for GET only.

        So a POST to one is the 405 the contract claims rather than a 404
        reserved for a path that does not exist. Measured before this:
        `POST /` and `POST /api/runs/<id>` both answered 404.
        """
        if not segs:
            return True                      # "/" is the dashboard page
        if segs[:1] != ["api"]:
            return False
        rest = segs[1:]
        if rest in (["health"], ["findings"], ["reports"]):
            return True
        return len(rest) == 2 and rest[0] in ("runs", "reports")

    def do_POST(self) -> None:  # noqa: N802 - stdlib hook
        if self._reject_foreign():
            return
        segs, _ = self._segments()
        if segs == ["api", "prompt"]:
            self._prompt()
            return
        if segs == ["api", "runs"]:
            self._start_run()
            return
        if self._get_only(segs):
            self._json(HTTPStatus.METHOD_NOT_ALLOWED,
                       {"error": "method not allowed"})
            return
        self._not_found()

    # -- route bodies -----------------------------------------------------

    def _dashboard(self) -> None:
        page = Path(__file__).resolve().parent / DASHBOARD_FILE
        extra = (("Content-Security-Policy", _DASHBOARD_CSP),
                 ("X-Frame-Options", "DENY"))
        try:
            size = page.stat().st_size
        except OSError:
            size = -1
        if size < 0:
            # The page is written separately from this module. Say so rather
            # than crash, and name the API so the console is still usable.
            self._send(HTTPStatus.OK, _MISSING_PAGE.encode("utf-8"),
                       "text/html; charset=utf-8", extra)
            return
        if size > MAX_DASHBOARD_BYTES:
            self._json(HTTPStatus.INTERNAL_SERVER_ERROR,
                       {"error": f"{DASHBOARD_FILE} is larger than "
                                 f"{MAX_DASHBOARD_BYTES} bytes"})
            return
        self._send_file(page, "text/html; charset=utf-8", extra)

    def _one_run(self, run_id: str) -> None:
        if not api.valid_run_id(run_id):
            self._json(HTTPStatus.BAD_REQUEST, {"error": "invalid run id"})
            return
        run = self.registry.run(run_id)
        if run is None:
            self._not_found()
            return
        self._json(HTTPStatus.OK,
                   {"run": run, "events": self.registry.events(run_id)})

    def _report(self, run_id: str, fmt: str) -> None:
        if not api.valid_run_id(run_id):
            # Reached by `/api/reports/..%2f..%2fetc%2fpasswd`: the segment
            # decodes to a path and is refused on syntax, before anything
            # touches the filesystem.
            self._json(HTTPStatus.BAD_REQUEST, {"error": "invalid run id"})
            return
        if fmt not in api.REPORT_FORMATS:
            self._json(HTTPStatus.BAD_REQUEST,
                       {"error": "fmt must be one of "
                                 + ", ".join(api.REPORT_FORMATS)})
            return
        path = api.report_path(self.root, run_id, fmt)
        if path is None:
            self._not_found()
            return
        ctype = api.REPORT_FORMATS[fmt][1]
        extra: tuple[tuple[str, str], ...] = ()
        if fmt == "html":
            extra = (("Content-Security-Policy", _REPORT_CSP),)
        self._send_file(path, ctype, extra)

    def _prompt(self) -> None:
        data = self._body()
        if data is None:
            return
        mode, target, auth, extra, type_errors = self._request_fields(data)
        result = api.preview_prompt(mode, target, auth, extra)
        if type_errors:
            result = {"ok": False, "prompt": "",
                      "errors": type_errors + list(result["errors"])}
        self._json(HTTPStatus.OK, result)

    def _start_run(self) -> None:
        data = self._body()
        if data is None:
            return
        mode, target, auth, extra, type_errors = self._request_fields(data)
        result = api.preview_prompt(mode, target, auth, extra)
        errors = type_errors + list(result["errors"])
        if errors or not result["ok"]:
            # Nothing is created on this path. The session directory, the
            # prompt file and the thread all come after the gate, so a
            # refused request leaves no artifact that looks like a run.
            self._json(HTTPStatus.BAD_REQUEST,
                       {"ok": False, "run_id": "",
                        "errors": errors or ["prompt preview refused the "
                                             "request"]})
            return
        try:
            run = self.registry.create(mode=mode, target=target, auth=auth,
                                       extra=extra, prompt=result["prompt"])
        except TooManyRuns as exc:
            self._json(HTTPStatus.TOO_MANY_REQUESTS,
                       {"ok": False, "run_id": "", "errors": [str(exc)]})
            return
        except ScopeError as exc:
            # The scope guard is the one check nothing may bypass, so its
            # refusal is reported as a refusal and not as a server error.
            self._json(HTTPStatus.BAD_REQUEST,
                       {"ok": False, "run_id": "",
                        "errors": [f"out of scope: {exc}"]})
            return
        except (OSError, ValueError) as exc:
            self._json(HTTPStatus.INTERNAL_SERVER_ERROR,
                       {"ok": False, "run_id": "",
                        "errors": [f"{type(exc).__name__}: "
                                   f"{api._redact(str(exc))[:200]}"]})
            return
        self._json(HTTPStatus.OK,
                   {"ok": True, "run_id": run["id"], "errors": []})


_MISSING_PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>argus console</title></head><body>
<h1>argus console</h1>
<p>The dashboard page (<code>argus/web/dashboard.html</code>) is not present
in this installation, so there is nothing to render. The JSON API is
serving:</p>
<ul>
<li><code>GET /api/health</code></li>
<li><code>POST /api/prompt</code></li>
<li><code>GET /api/runs</code>, <code>POST /api/runs</code>,
    <code>GET /api/runs/&lt;id&gt;</code></li>
<li><code>GET /api/findings</code></li>
<li><code>GET /api/reports</code>,
    <code>GET /api/reports/&lt;id&gt;?fmt=md|html|sarif</code></li>
</ul>
</body></html>
"""


def make_server(host: str = "127.0.0.1", port: int = 8787, *,
                root: Path | str,
                model_configured: bool = False,
                runner: Callable[[dict, Callable[[str], None]], None] | None = None,
                allow_remote: bool = False,
                registry: RunRegistry | None = None,
                quiet: bool = False,
                secrets: list[str] | None = None) -> _WebServer:
    """A ThreadingHTTPServer serving the console and the JSON API.

    `port=0` binds an ephemeral port, which is how the tests drive it.
    `runner` is what actually performs a run: the web layer owns run
    bookkeeping and refuses to pretend an agent ran, so the orchestration is
    injected rather than imported.
    """
    _check_bind_host(host, allow_remote)
    rootp = Path(root).expanduser()
    reg = registry or RunRegistry(rootp, model_configured=model_configured,
                                  runner=runner, secrets=secrets)
    # A handler subclass per server rather than module-level state: two
    # servers in one process (a test suite is one) must not share a root.
    handler = type("_BoundHandler", (_Handler,),
                   {"registry": reg, "root": rootp, "quiet": bool(quiet),
                    "loopback_bind": _is_loopback(host),
                    "bound_host": str(host or "127.0.0.1")})
    srv = _WebServer((host, port), handler)
    srv.registry = reg
    srv.root = rootp
    return srv


def serve(host: str = "127.0.0.1", port: int = 8787,
          root: Path | str = Path("sessions"),
          runner: Callable[[dict, Callable[[str], None]], None] | None = None,
          *, allow_remote: bool | None = None,
          secrets: list[str] | None = None) -> int:
    """Blocking entry point: print the URL and serve until interrupted.

    `runner` performs a run; with none, a started run reaches `blocked` and
    says why, and nothing claims an agent ran. It is a keyword argument with
    a default so the CLI's three-positional call keeps working and the
    integration still has one place to pass a runner in.

    `allow_remote` is the override `_check_bind_host` asks for, and it is
    NOT derived from `host`. This function used to compute
    `remote = not _is_loopback(host)` and pass that as `allow_remote`, which
    granted the override exactly when the gate would have fired: measured,
    `serve("0.0.0.0", 0, root)` returned having bound ('0.0.0.0', 35413)
    with the Host anti-rebinding check off, so `argus web --bind 0.0.0.0`
    handed every evidence excerpt in /api/findings and POST /api/runs to
    anyone who reached the port, on one argument and a stderr warning. Left
    as None it is read from the environment, because the CLI has no flag to
    pass it with - so a non-loopback bind now takes two deliberate acts.
    """
    rootp = Path(root).expanduser()
    # Presence of a credential SOURCE, not validity - see
    # `api.credential_source_present`. Whether a credential actually works
    # is the runner's answer, at run start, where a failure can be reported
    # against a run instead of printed next to a URL.
    model = api.credential_source_present()
    if allow_remote is None:
        allow_remote = _allow_remote_from_env()
    if secrets is None:
        # The same declared-secret rule as `config`: semicolon-separated,
        # >=4 chars (the floor is `Session`'s). Without this the shipped
        # path - `argus web`, which passes no secrets - would have no
        # declared values to scrub out of the event log.
        declared = (os.environ.get("ARGUS_SECRETS") or "").split(";")
        secrets = [s for s in declared if len(s) >= 4]
    remote = not _is_loopback(host)
    try:
        srv = make_server(host, port, root=rootp, model_configured=model,
                          allow_remote=bool(allow_remote), runner=runner,
                          secrets=secrets)
    except ValueError as exc:
        # The bind gate. Reported, not raised: this is the CLI's return
        # value, and a traceback would read as a crash rather than as the
        # refusal it is.
        print(f"argus web: {exc}", file=sys.stderr)
        return 2
    shown = host if not remote else "127.0.0.1"
    bound = srv.server_address[1]
    print(f"argus console: http://{shown}:{bound}/")
    print(f"  session directory: {rootp}")
    tools = api._health_tools()
    print("  tools on PATH: "
          + (", ".join(n for n, ok in tools.items() if ok) or "none"))
    print("  model credential: "
          + ("a source is present" if model else
             "none found - the agent half will not run"))
    if remote:
        print(f"  WARNING: bound to {host}, not loopback. This console has "
              "no authentication and starts scans, and the Host "
              "anti-rebinding check is off for a non-loopback bind.",
              file=sys.stderr)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print()
    finally:
        # server_close only: shutdown() from this thread would wait on the
        # loop that has already left, and serve_forever's own finally has
        # released it.
        srv.server_close()
    return 0
