"""recon — deterministic surface mapping. No model in the find step.

Breadth is cheap and should never cost tokens: ports, service and framework
fingerprints, paths, parameters, and the endpoints and keys shipped inside
JavaScript are all found by plain code. What a model is for is deciding which of
those inputs is worth a hypothesis, and that decision is better when the map was
produced the same way every time.

Everything here is class `recon` in the ledger, which gives it its own budget: a
surface that has been mapped should be classified, not mapped again.
"""
from __future__ import annotations

import os
import re
import urllib.parse
import xml.etree.ElementTree as ET

from ... import config
from ...ledger.state import RECON
from .. import exec as ex
from .. import httpkit
from ..mcp import Server, ToolContext, ToolError

SERVER = Server("recon", "ports, fingerprints, paths, parameters and javascript mining")

_URL = {"target": {"type": "string", "description": "URL or host; must be in scope"}}


def _host_of(target: str) -> str:
    if "://" in target:
        return urllib.parse.urlsplit(target).hostname or target
    return target.split("/")[0].split(":")[0]


def _base_of(target: str) -> str:
    if "://" not in target:
        return "http://" + target.rstrip("/")
    split = urllib.parse.urlsplit(target)
    return f"{split.scheme}://{split.netloc}"


# --- ports -------------------------------------------------------------------

@SERVER.tool(
    "recon.ports",
    "Map which TCP ports answer on one host and what service each one claims, with nmap. "
    "Returns one line per open port and records each as surface. Unprivileged by default "
    "(connect scan), so no root is needed.",
    {"properties": {**_URL,
                    "ports": {"type": "string",
                              "description": "nmap port spec, or 'top-100' / 'top-1000' (default)"},
                    "service_detection": {"type": "boolean", "description": "run -sV (default true)"},
                    "timeout": {"type": "integer", "description": "seconds, default 300"}},
     "required": ["target"]},
    tier=config.TIER_ACTIVE, vuln_class=RECON, step="host-liveness", requires=("nmap",),
)
def ports(context: ToolContext, target: str, ports: str = "top-1000",
          service_detection: bool = True, timeout: int = 300) -> dict:
    host = _host_of(target)
    argv = ["nmap", "-Pn", "-n", "-T4", "-oX", "-"]
    argv.append("-sS" if os.geteuid() == 0 else "-sT")
    if service_detection:
        argv += ["-sV", "--version-light"]
    if ports.startswith("top-"):
        argv += ["--top-ports", ports.split("-", 1)[1]]
    else:
        argv += ["-p", ports]
    argv.append(host)
    result = ex.run(argv, timeout=timeout, log_path=context.command_log)
    found = _parse_nmap(result.stdout)
    for entry in found:
        context.emit_surface(target, "port", f"{entry['port']}/{entry['protocol']}",
                             detail={k: v for k, v in entry.items() if k != "port"})
    lines = [f"{e['port']}/{e['protocol']} {e['state']} {e['service']} {e['product']} {e['version']}".strip()
             for e in found]
    return {
        "summary": f"{len(found)} open port(s) on {host}" + (": " + ", ".join(
            str(e["port"]) for e in found) if found else ""),
        "result": "signal" if found else "no-signal",
        "argv": argv, "exit_code": result.exit_code, "duration_ms": result.duration_ms,
        "data": {"host": host, "open_ports": found},
        "output": "\n".join(lines) or result.text(4000),
        "evidence": {"kind": "probe", "target": target, "tool": "nmap",
                     "command": argv, "stdout_span": result.stdout,
                     "extracted": {"open_ports": found}},
        "next": "fingerprint each HTTP service before fuzzing anything",
    }


def _parse_nmap(xml_text: str) -> list[dict]:
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []
    out = []
    for port in root.iterfind(".//port"):
        state = port.find("state")
        if state is None or state.get("state") != "open":
            continue
        service = port.find("service")
        out.append({
            "port": int(port.get("portid", 0)),
            "protocol": port.get("protocol", "tcp"),
            "state": "open",
            "service": (service.get("name") if service is not None else "") or "",
            "product": (service.get("product") if service is not None else "") or "",
            "version": (service.get("version") if service is not None else "") or "",
            "tunnel": (service.get("tunnel") if service is not None else "") or "",
        })
    return sorted(out, key=lambda e: e["port"])


# --- fingerprint -------------------------------------------------------------

_TECH_MARKERS = [
    (re.compile(r"(?i)x-powered-by:\s*(php|express|asp\.net|next\.js)"), "header"),
    (re.compile(r"(?i)<meta[^>]+generator[^>]+content=\"([^\"]+)"), "generator"),
    (re.compile(r"(?i)(wp-content|wp-includes)/"), "wordpress"),
    (re.compile(r"(?i)/_next/static/"), "nextjs"),
    (re.compile(r"(?i)csrfmiddlewaretoken"), "django"),
    (re.compile(r"(?i)laravel_session"), "laravel"),
    (re.compile(r"(?i)JSESSIONID"), "java-servlet"),
    (re.compile(r"(?i)Apache Tomcat/?([\d.]+)?"), "tomcat"),
    (re.compile(r"(?i)__VIEWSTATE"), "asp.net-webforms"),
    (re.compile(r"(?i)/static/js/main\.[0-9a-f]{8}\.js"), "create-react-app"),
]


@SERVER.tool(
    "recon.fingerprint",
    "Identify what one HTTP service is running: server, framework, declared versions, security "
    "headers, cookie flags and the title. Uses httpx-toolkit when installed and falls back to a "
    "direct request, so it works with no extra tooling.",
    {"properties": {**_URL, "timeout": {"type": "integer"}}, "required": ["target"]},
    tier=config.TIER_ACTIVE, vuln_class=RECON, step="service-fingerprint",
)
def fingerprint(context: ToolContext, target: str, timeout: int = 30) -> dict:
    base = _base_of(target)
    # Redirects are followed here because a front page that redirects to /login
    # is the common case — but every hop is re-checked against the engagement
    # scope, so an in-scope host cannot redirect us somewhere we were never
    # authorised to reach.
    scope = context.state.scope
    response = httpkit.request("GET", base + "/", timeout=timeout, follow=True,
                               allow=lambda candidate: bool(scope.check(candidate)))
    if response.status is None:
        raise ToolError(f"{base} did not answer: {response.error}")
    body = response.body
    technologies = []
    for pattern, label in _TECH_MARKERS:
        match = pattern.search(body) or pattern.search(str(response.headers))
        if match:
            detail = match.group(1) if match.groups() else ""
            technologies.append(f"{label}:{detail}" if detail else label)
    title = (re.search(r"(?is)<title[^>]*>(.*?)</title>", body) or [None, ""])[1].strip()[:120] \
        if "<title" in body.lower() else ""
    missing_headers = [h for h in ("content-security-policy", "x-frame-options",
                                   "strict-transport-security", "x-content-type-options")
                       if not response.header(h)]
    cookies = response.headers.get("set-cookie", "")
    stack = {
        "server": response.header("server"), "powered_by": response.header("x-powered-by"),
        "technologies": technologies, "title": title, "status": response.status,
        "content_type": response.header("content-type"),
        "missing_security_headers": missing_headers,
        "cookie_flags": {"httponly": "httponly" in cookies.lower(),
                         "secure": "secure" in cookies.lower(),
                         "samesite": "samesite" in cookies.lower()} if cookies else {},
    }
    extra = {}
    if ex.which("httpx-toolkit") or ex.which("httpx"):
        binary = ex.which("httpx-toolkit") or ex.which("httpx")
        result = ex.run([binary, "-u", base, "-silent", "-json", "-tech-detect", "-status-code",
                         "-title", "-no-color"], timeout=min(timeout, 60),
                        log_path=context.command_log)
        extra["httpx"] = result.stdout.strip()[:2000]
    context.note_stack(target, stack)
    return {
        "summary": f"{base} -> {response.status} {stack['server'] or 'no server header'} "
                   f"{'/'.join(technologies) or 'no framework marker'}"
                   + (f" | title: {title}" if title else ""),
        "result": "signal",
        "data": stack | extra,
        "output": "\n".join(f"{k}: {v}" for k, v in response.headers.items())[:3000],
        "evidence": {"kind": "probe", "target": target, "tool": "recon.fingerprint",
                     **response.to_evidence(), "extracted": stack},
        "next": "a version here is a candidate, never a finding: check the CVE's preconditions first",
    }


# --- parameters and endpoints ------------------------------------------------

_FORM_RE = re.compile(r"(?is)<form[^>]*>(.*?)</form>")
_FORM_ATTR_RE = re.compile(r"(?is)<form([^>]*)>")
_INPUT_RE = re.compile(r"(?is)<(?:input|textarea|select)([^>]*)>")
_ATTR_RE = re.compile(r"""(?i)(\w[\w-]*)\s*=\s*["']?([^"'\s>]*)""")
_HREF_RE = re.compile(r"""(?i)(?:href|src|action)\s*=\s*["']([^"'#>]+)""")
_JS_URL_RE = re.compile(r"""(?:fetch|axios(?:\.\w+)?|open|url\s*[:=]|ajax)\s*\(?\s*["'`]([^"'`\s]+)""")
_JS_PATH_RE = re.compile(r"""["'`](/[A-Za-z0-9._~/\-]{2,80})["'`]""")
_QUERY_PARAM_RE = re.compile(r"[?&]([A-Za-z_][\w\-\[\]]{0,40})=")
_SECRET_RE = [
    ("aws-access-key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("google-api-key", re.compile(r"AIza[0-9A-Za-z_\-]{35}")),
    ("slack-token", re.compile(r"xox[baprs]-[0-9A-Za-z\-]{10,}")),
    ("stripe-key", re.compile(r"(?:sk|rk)_live_[0-9A-Za-z]{20,}")),
    ("github-pat", re.compile(r"gh[pousr]_[A-Za-z0-9]{30,}")),
    ("private-key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("jwt", re.compile(r"eyJ[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}\.[A-Za-z0-9_\-]{8,}")),
    ("basic-auth-url", re.compile(r"https?://[^/\s:@]+:[^/\s:@]+@")),
]
_NOISE_PARAMS = {"utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content", "fbclid",
                 "gclid", "_ga", "ref", "v", "ver", "cache", "t", "_"}


@SERVER.tool(
    "recon.params",
    "Crawl one origin shallowly and list every input it exposes: form fields with their method and "
    "action, query parameters seen in links, and endpoints referenced from JavaScript. Records each "
    "as surface. Inputs are where every class lives, so this is the map a hypothesis is drawn on.",
    {"properties": {**_URL,
                    "depth": {"type": "integer", "description": "same-origin link depth, 0-2 (default 1)"},
                    "max_pages": {"type": "integer", "description": "default 12"},
                    "timeout": {"type": "integer"}},
     "required": ["target"]},
    tier=config.TIER_ACTIVE, vuln_class=RECON, step="parameter-discovery",
)
def params(context: ToolContext, target: str, depth: int = 1, max_pages: int = 12,
           timeout: int = 15) -> dict:
    base = _base_of(target)
    origin = urllib.parse.urlsplit(base).netloc
    depth = max(0, min(int(depth), 2))
    max_pages = max(1, min(int(max_pages), 40))
    start = target if "://" in target else base + "/"
    seen: set[str] = set()
    queue = [(start, 0)]
    forms, parameters, endpoints, scripts = [], {}, set(), set()

    while queue and len(seen) < max_pages:
        url, level = queue.pop(0)
        if url in seen:
            continue
        seen.add(url)
        response = httpkit.request("GET", url, timeout=timeout)
        if response.status is None:
            continue
        body = response.body
        for match in _FORM_ATTR_RE.finditer(body):
            attributes = dict(_ATTR_RE.findall(match.group(1)))
            block = body[match.end(): match.end() + 4000]
            fields = []
            for field_match in _INPUT_RE.finditer(block):
                field_attributes = dict(_ATTR_RE.findall(field_match.group(1)))
                name = field_attributes.get("name") or field_attributes.get("id")
                if name:
                    fields.append({"name": name, "type": field_attributes.get("type", "text")})
            action = urllib.parse.urljoin(url, attributes.get("action", ""))
            forms.append({"page": url, "action": action,
                          "method": (attributes.get("method") or "get").upper(), "fields": fields})
            for field in fields:
                parameters.setdefault(field["name"], {"name": field["name"], "locations": set(),
                                                      "seen_at": set()})
                parameters[field["name"]]["locations"].add(
                    "body" if (attributes.get("method") or "get").lower() == "post" else "query")
                parameters[field["name"]]["seen_at"].add(action)
        for match in _HREF_RE.finditer(body):
            link = urllib.parse.urljoin(url, match.group(1))
            split = urllib.parse.urlsplit(link)
            if split.netloc != origin or split.scheme not in ("http", "https"):
                continue
            if split.path.endswith(".js"):
                scripts.add(link)
            endpoints.add(split.path or "/")
            for name in _QUERY_PARAM_RE.findall("?" + split.query):
                if name in _NOISE_PARAMS:
                    continue
                parameters.setdefault(name, {"name": name, "locations": set(), "seen_at": set()})
                parameters[name]["locations"].add("query")
                parameters[name]["seen_at"].add(split.path)
            if level < depth:
                queue.append((urllib.parse.urlunsplit(split._replace(fragment="")), level + 1))

    for name, entry in parameters.items():
        context.emit_surface(target, "param", name,
                             detail={"locations": sorted(entry["locations"]),
                                     "seen_at": sorted(entry["seen_at"])[:6]})
    for form in forms:
        context.emit_surface(target, "form", f"{form['method']} {form['action']}",
                             detail={"fields": [f["name"] for f in form["fields"]]})
    for path in sorted(endpoints)[:200]:
        context.emit_surface(target, "endpoint", path)

    listing = [f"{entry['name']:24} {'/'.join(sorted(entry['locations'])):10} "
               f"{', '.join(sorted(entry['seen_at'])[:3])}" for entry in parameters.values()]
    return {
        "summary": f"{len(parameters)} parameter(s), {len(forms)} form(s), {len(endpoints)} path(s), "
                   f"{len(scripts)} script(s) across {len(seen)} page(s) of {origin}",
        "result": "signal" if parameters or forms else "no-signal",
        "data": {"parameters": [{"name": e["name"], "locations": sorted(e["locations"]),
                                 "seen_at": sorted(e["seen_at"])[:6]} for e in parameters.values()],
                 "forms": forms, "paths": sorted(endpoints)[:120], "scripts": sorted(scripts)[:40],
                 "pages_crawled": sorted(seen)},
        "output": "\n".join(listing)[:6000],
        "evidence": {"kind": "probe", "target": target, "tool": "recon.params",
                     "extracted": {"parameter_count": len(parameters), "form_count": len(forms),
                                   "paths": sorted(endpoints)[:60],
                                   "parameters": sorted(parameters)[:80]}},
        "next": "name a class and a falsifier for the inputs worth probing; park the rest explicitly",
    }


@SERVER.tool(
    "recon.js_mine",
    "Fetch the JavaScript one page loads and mine it for endpoints, parameter names and credential "
    "shapes. Secrets are reported by kind and position with the value redacted — the ledger never "
    "stores a live key.",
    {"properties": {**_URL, "max_scripts": {"type": "integer", "description": "default 12"},
                    "timeout": {"type": "integer"}},
     "required": ["target"]},
    tier=config.TIER_ACTIVE, vuln_class=RECON, step="javascript-mining",
)
def js_mine(context: ToolContext, target: str, max_scripts: int = 12, timeout: int = 20) -> dict:
    base = _base_of(target)
    page = httpkit.request("GET", target if "://" in target else base + "/", timeout=timeout)
    if page.status is None:
        raise ToolError(f"{base} did not answer: {page.error}")
    origin = urllib.parse.urlsplit(base).netloc
    scripts = []
    for match in _HREF_RE.finditer(page.body):
        link = urllib.parse.urljoin(base, match.group(1))
        if link.endswith(".js") and urllib.parse.urlsplit(link).netloc == origin:
            scripts.append(link)
    scripts = sorted(set(scripts))[: max(1, min(int(max_scripts), 30))]
    endpoints, secrets, parameters = set(), [], set()
    for script_url in scripts:
        response = httpkit.request("GET", script_url, timeout=timeout)
        if response.status is None:
            continue
        text = response.body
        for match in _JS_URL_RE.finditer(text):
            endpoints.add(match.group(1)[:200])
        for match in _JS_PATH_RE.finditer(text):
            endpoints.add(match.group(1))
        for name in _QUERY_PARAM_RE.findall(text):
            if name not in _NOISE_PARAMS:
                parameters.add(name)
        for kind, pattern in _SECRET_RE:
            for match in pattern.finditer(text):
                value = match.group(0)
                secrets.append({"kind": kind, "script": script_url,
                                "offset": match.start(),
                                "preview": value[:6] + "…REDACTED"})
    for endpoint in sorted(endpoints)[:200]:
        if endpoint.startswith("/"):
            context.emit_surface(target, "endpoint", endpoint, detail={"source": "javascript"})
    for name in sorted(parameters)[:120]:
        context.emit_surface(target, "param", name, detail={"source": "javascript"})
    return {
        "summary": f"{len(scripts)} script(s): {len(endpoints)} endpoint(s), {len(parameters)} "
                   f"parameter name(s), {len(secrets)} credential shape(s)",
        "result": "signal" if (endpoints or secrets) else "no-signal",
        "data": {"scripts": scripts, "endpoints": sorted(endpoints)[:150],
                 "parameters": sorted(parameters)[:120], "secrets": secrets},
        "output": "\n".join(sorted(endpoints))[:5000],
        "evidence": {"kind": "probe", "target": target, "tool": "recon.js_mine",
                     "extracted": {"endpoint_count": len(endpoints), "secret_kinds":
                                   sorted({s["kind"] for s in secrets}),
                                   "endpoints": sorted(endpoints)[:80]}},
        "next": ("a credential shape in a bundle is not a finding until it is shown live against "
                 "its own issuer" if secrets else "probe the endpoints the HTML never linked"),
    }


@SERVER.tool(
    "recon.subdomains",
    "Passive subdomain enumeration for one apex domain with subfinder. Queries third-party data "
    "sources only; it never touches the target. Results still have to pass the engagement scope "
    "before anything is probed.",
    {"properties": {"domain": {"type": "string", "description": "apex domain, e.g. example.com"},
                    "timeout": {"type": "integer"}},
     "required": ["domain"]},
    tier=config.TIER_PASSIVE, vuln_class=RECON, step="subdomain-enumeration", requires=("subfinder",),
    touches_target=False,
)
def subdomains(context: ToolContext, domain: str, timeout: int = 180) -> dict:
    argv = ["subfinder", "-d", domain, "-silent", "-all"]
    result = ex.run(argv, timeout=timeout, log_path=context.command_log)
    hosts = sorted({line.strip() for line in result.stdout.splitlines() if line.strip()})
    in_scope, out_of_scope = [], []
    if context.engagement:
        scope = context.state.scope
        for host in hosts:
            (in_scope if scope.check(host) else out_of_scope).append(host)
    return {
        "summary": f"{len(hosts)} host(s) for {domain}; {len(in_scope)} in scope, "
                   f"{len(out_of_scope)} outside it",
        "result": "signal" if hosts else "no-signal",
        "argv": argv, "exit_code": result.exit_code, "duration_ms": result.duration_ms,
        "data": {"in_scope": in_scope, "out_of_scope": out_of_scope[:50]},
        "output": "\n".join(hosts)[:5000],
        "next": "only the in_scope list may be probed; the rest is context, not surface",
    }
