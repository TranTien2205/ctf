"""Web surface tools: raw request, crawl, JS recon, passive fingerprint."""
from __future__ import annotations

import json as _json
import re
import urllib.parse
from html.parser import HTMLParser

from ..scope import ScopeError
from .registry import Context


def http_request(ctx: Context, method: str, url: str,
                 headers: dict | None = None, body: str | None = None,
                 follow_redirects: bool = False, note: str = "") -> dict:
    return ctx.client.send(method, url, headers=headers, body=body,
                           follow_redirects=follow_redirects, tool="http_request",
                           note=note)


class _SurfaceParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []
        self.forms: list[dict] = []
        self.scripts: list[str] = []
        self.inline_js: list[str] = []
        self.title = ""
        self._in_script = False
        self._script_buf: list[str] = []
        self._in_title = False
        self._cur_form: dict | None = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        elif tag == "script":
            if a.get("src"):
                self.scripts.append(a["src"])
            else:
                self._in_script = True
                self._script_buf = []
        elif tag == "form":
            self._cur_form = {"action": a.get("action", ""), "method": (a.get("method") or "GET").upper(), "inputs": []}
            self.forms.append(self._cur_form)
        elif tag in ("input", "textarea", "select") and self._cur_form is not None:
            self._cur_form["inputs"].append(
                {"name": a.get("name", ""), "type": a.get("type", "text")})
        elif tag == "link" and a.get("href"):
            self.links.append(a["href"])
        elif tag == "title":
            self._in_title = True

    def handle_endtag(self, tag):
        if tag == "script" and self._in_script:
            self._in_script = False
            self.inline_js.append("".join(self._script_buf))
        elif tag == "form":
            self._cur_form = None
        elif tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_script:
            self._script_buf.append(data)
        elif self._in_title:
            self.title += data.strip()


def _parse_surface(html: str) -> _SurfaceParser:
    parser = _SurfaceParser()
    try:
        parser.feed(html)
    except Exception:
        pass
    return parser


def crawl(ctx: Context, url: str, depth: int = 2, max_pages: int = 40) -> dict:
    depth = max(0, min(int(depth or 2), 4))
    max_pages = max(1, min(int(max_pages or 40), 200))
    seen: set[str] = set()
    queue: list[tuple[str, int]] = [(url, 0)]
    pages: list[dict] = []
    forms: list[dict] = []
    endpoints: set[str] = set()
    errors: list[str] = []

    def canon(u: str) -> str:
        p = urllib.parse.urlparse(u)
        clean_q = urllib.parse.urlencode(
            sorted(urllib.parse.parse_qsl(p.query)))
        return urllib.parse.urlunparse((p.scheme, p.netloc, p.path or "/",
                                        "", clean_q, ""))

    while queue and len(pages) < max_pages:
        cur, d = queue.pop(0)
        key = canon(cur)
        if key in seen:
            continue
        seen.add(key)
        try:
            res = ctx.client.send("GET", cur, tool="crawl", note=f"crawl depth {d}")
        except ScopeError as exc:
            errors.append(str(exc))
            continue
        status = res["status"]
        body = res.get("body", "")
        ctype = (res.get("headers") or {}).get("content-type", "")
        parsed = urllib.parse.urlparse(cur)
        params = sorted({n for n, _ in urllib.parse.parse_qsl(parsed.query)})
        page = {"url": cur, "status": status, "depth": d,
                "request_id": res["request_id"], "params": params}
        endpoints.add(parsed.path or "/")
        if "html" not in ctype and not body.lstrip().startswith("<"):
            pages.append(page)
            continue
        surf = _parse_surface(body)
        page["title"] = surf.title[:120]
        pages.append(page)
        for form in surf.forms:
            action = urllib.parse.urljoin(cur, form["action"] or cur)
            forms.append({"page": cur, "action": action,
                          "method": form["method"], "inputs": form["inputs"]})
            endpoints.add(urllib.parse.urlparse(action).path or "/")
        if d < depth:
            for link in surf.links + surf.scripts:
                if link.startswith(("javascript:", "mailto:", "tel:", "#")):
                    continue
                absu = urllib.parse.urljoin(cur, link)
                pu = urllib.parse.urlparse(absu)
                # follow in-scope hosts (incl. declared subdomains), not just
                # the start origin - scope.check still vets scheme/private
                if not ctx.scope.host_allowed(pu.hostname or ""):
                    continue
                if pu.path not in endpoints:
                    endpoints.add(pu.path or "/")
                ckey = canon(absu)
                if ckey not in seen:
                    queue.append((absu, d + 1))
    return {
        "pages_crawled": len(pages),
        "pages": pages[:60],
        "forms": forms[:40],
        "endpoints": sorted(endpoints)[:120],
        "skipped_errors": errors[:10],
        "note": "param names and forms are the attack surface; feed promising ones to probe_* tools",
    }


_JS_ENDPOINT = re.compile(
    r"""(?:fetch|axios(?:\.\w+)?|\.open|\$\.ajax|\$\.get|\$\.post)\s*\(\s*['"`]([^'"`]{1,200})['"`]"""
    r"""|['"](/(?:api|rest|v\d+|graphql|auth|user|admin|internal)[^'"`\s]{0,150})['"`]"""
    r"""|url\s*[:=]\s*['"`]([^'"`]{1,200})['"`]""",
    re.I,
)
_JS_SECRET = re.compile(
    r"""(?i)(api[_-]?key|api[_-]?secret|access[_-]?token|auth[_-]?token|secret|password|passwd|private[_-]?key|aws[_-]?secret|client[_-]?secret)"""
    r"""\s*[:=]\s*['"`]([^'"`\s]{8,120})['"`]"""
)
_SRCMAP = re.compile(r"sourceMappingURL=([^\s]+)")
_JS_WS = re.compile(r"""['"`](wss?://[^'"`\s]{4,200})['"`]""", re.I)


def js_recon(ctx: Context, url: str) -> dict:
    res = ctx.client.send("GET", url, tool="js_recon", note="page for JS inventory")
    body = res.get("body", "")
    surf = _parse_surface(body)
    scripts = [urllib.parse.urljoin(url, s) for s in surf.scripts]
    inline = [s for s in surf.inline_js if s.strip()]

    ws_endpoints: list[dict] = []

    def scan(text: str, src: str) -> tuple[list[dict], list[dict]]:
        eps, secrets = [], []
        for m in _JS_ENDPOINT.finditer(text):
            val = next(g for g in m.groups() if g)
            line = text.count("\n", 0, m.start()) + 1
            eps.append({"endpoint": val, "source": src, "line": line})
        for m in _JS_SECRET.finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            secrets.append({"kind": m.group(1), "value": m.group(2),
                            "source": src, "line": line})
        for m in _JS_WS.finditer(text):
            line = text.count("\n", 0, m.start()) + 1
            ws_endpoints.append({"endpoint": m.group(1), "source": src,
                                 "line": line})
        return eps, secrets

    endpoints: list[dict] = []
    secrets: list[dict] = []
    for i, chunk in enumerate(inline):
        e, s = scan(chunk, f"{url}#inline-{i}")
        endpoints.extend(e)
        secrets.extend(s)
    fetched = 0
    maps_found = 0
    for src in scripts[:15]:
        try:
            r = ctx.client.send("GET", src, tool="js_recon", note="js bundle")
        except ScopeError:
            continue
        fetched += 1
        bundle = r.get("body", "")
        e, s = scan(bundle, src)
        endpoints.extend(e)
        secrets.extend(s)

        # Sourcemap recovery: a deployed .map exposes the original sources -
        # comments, env refs, file paths - far richer than the minified bundle
        m = _SRCMAP.search(bundle[-2000:])
        map_url = urllib.parse.urljoin(src, m.group(1)) if m else src + ".map"
        try:
            mr = ctx.client.send("GET", map_url, tool="js_recon",
                                 note="sourcemap probe")
        except ScopeError:
            mr = None
        if mr is None or not (200 <= mr["status"] < 300):
            continue
        try:
            smap = _json.loads(mr.get("body", ""))
        except (ValueError, _json.JSONDecodeError):
            continue
        contents = smap.get("sourcesContent")
        if not isinstance(contents, list):
            continue
        maps_found += 1
        names = smap.get("sources") or []
        for i, cont in enumerate(contents[:20]):
            if not isinstance(cont, str):
                continue
            label = names[i] if i < len(names) else f"source-{i}"
            e, s = scan(cont, f"{map_url}#{label}")
            endpoints.extend(e)
            secrets.extend(s)

    uniq_eps, seen = [], set()
    for ep in endpoints:
        if ep["endpoint"] not in seen:
            seen.add(ep["endpoint"])
            uniq_eps.append(ep)
    return {
        "page_request_id": res["request_id"],
        "scripts_found": len(scripts),
        "scripts_fetched": fetched,
        "sourcemaps_found": maps_found,
        "endpoints": uniq_eps[:80],
        "websocket_endpoints": ws_endpoints[:20],
        "secret_candidates": secrets[:30],
        "note": "secret_candidates are leads, not findings - verify usage before recording",
    }


_SEC_HEADERS = [
    "content-security-policy", "strict-transport-security",
    "x-content-type-options", "x-frame-options", "referrer-policy",
    "permissions-policy",
]


def fingerprint(ctx: Context, url: str) -> dict:
    res = ctx.client.send("GET", url, tool="fingerprint", note="baseline GET")
    headers = {k.lower(): v for k, v in (res.get("headers") or {}).items()}
    cookies = []
    raw_cookies = res.get("headers", {}).get("set-cookie", "")
    for part in ([raw_cookies] if isinstance(raw_cookies, str) else raw_cookies):
        if not part:
            continue
        first = part.split(";", 1)[0]
        flags = {
            "httponly": "httponly" in part.lower(),
            "secure": "secure" in part.lower(),
            "samesite": (re.search(r"samesite=(\w+)", part, re.I) or [None, None])[1],
        }
        cookies.append({"name": first.split("=", 1)[0].strip(), **flags})

    missing = [h for h in _SEC_HEADERS if h not in headers]
    robots = sitemap = None
    p = urllib.parse.urlparse(url)
    root = f"{p.scheme}://{p.netloc}"
    try:
        r = ctx.client.send("GET", root + "/robots.txt", tool="fingerprint")
        if r["status"] == 200:
            disallow = re.findall(r"(?im)^disallow:\s*(\S+)", r.get("body", ""))
            robots = {"status": 200, "disallow": disallow[:30],
                      "request_id": r["request_id"]}
        else:
            robots = {"status": r["status"]}
    except ScopeError:
        pass
    try:
        r = ctx.client.send("GET", root + "/sitemap.xml", tool="fingerprint")
        sitemap = {"status": r["status"], "request_id": r["request_id"]}
    except ScopeError:
        pass

    stack_hints = []
    for h in ("server", "x-powered-by", "x-aspnet-version", "x-generator"):
        if h in headers:
            stack_hints.append(f"{h}: {headers[h]}")
    if "x-nextjs-cache" in headers or "_next/" in res.get("body", ""):
        stack_hints.append("framework: next.js (hint)")
    return {
        "request_id": res["request_id"],
        "status": res["status"],
        "headers": headers,
        "stack_hints": stack_hints,
        "cookies": cookies,
        "missing_security_headers": missing,
        "robots": robots,
        "sitemap": sitemap,
    }


_INTROSPECTION = (
    "{__schema{queryType{name} mutationType{name} subscriptionType{name}"
    " types{name kind fields{name type{name kind ofType{name kind}}}}}}")


def graphql_introspect(ctx: Context, url: str) -> dict:
    """POST a standard introspection query and summarize the schema -
    types, fields, mutation/subscription roots. A disabled endpoint or an
    error body is reported as negative evidence."""
    body = '{"query": ' + _json.dumps(_INTROSPECTION) + "}"
    r = ctx.client.send("POST", url,
                        headers={"Content-Type": "application/json"},
                        body=body, tool="graphql_introspect",
                        note="introspection query")
    raw = r.get("body") or ""
    try:
        doc = _json.loads(raw)
    except ValueError:
        return {"verdict": "no schema (non-JSON response)",
                    "request_id": r["request_id"], "status": r["status"]}
    schema = ((doc.get("data") or {}).get("__schema"))
    if not schema:
        errs = [e.get("message", "?") for e in doc.get("errors") or []][:5]
        return {"verdict": "introspection refused or empty",
                "request_id": r["request_id"], "errors": errs}
    types = [t for t in (schema.get("types") or [])
             if t.get("name") and not t["name"].startswith("__")]
    out_types = [{"name": t["name"], "kind": t.get("kind"),
                  "fields": [f["name"] for f in (t.get("fields") or [])
                             if f.get("name")][:40]}
                 for t in types][:40]
    return {"verdict": "schema introspected",
            "request_id": r["request_id"],
            "query_root": (schema.get("queryType") or {}).get("name"),
            "mutation_root": (schema.get("mutationType") or {}).get("name"),
            "subscription_root":
                (schema.get("subscriptionType") or {}).get("name"),
            "types": out_types}
