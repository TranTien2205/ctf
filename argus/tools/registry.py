"""Tool registry: JSON schemas for Claude's tool_use and the dispatcher."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ..config import Config
from ..httpclient import GuardedClient
from ..scope import ScopeGuard
from ..session import Session


@dataclass
class Context:
    cfg: Config
    scope: ScopeGuard
    session: Session
    client: GuardedClient
    skills_dir: object  # Path
    finished: bool = False
    finish_summary: str = ""


# Tool functions are imported lazily inside _impl() to keep module import cheap.
def _impl(name: str) -> Callable:
    from . import analysis, probes, web  # noqa: F401
    table = {
        "http_request": web.http_request,
        "crawl": web.crawl,
        "js_recon": web.js_recon,
        "fingerprint": web.fingerprint,
        "probe_reflection": probes.probe_reflection,
        "probe_sqli": probes.probe_sqli,
        "probe_time": probes.probe_time,
        "probe_ssti": probes.probe_ssti,
        "probe_lfi": probes.probe_lfi,
        "probe_redirect": probes.probe_redirect,
        "probe_cors": probes.probe_cors,
        "probe_method": probes.probe_method,
        "jwt_decode": analysis.jwt_decode,
        "load_skill": analysis.load_skill,
        "note": analysis.note,
        "read_notes": analysis.read_notes,
        "record_finding": analysis.record_finding,
        "run_external": analysis.run_external,
        "finish": analysis.finish,
    }
    return table[name]


_STR = {"type": "string"}
_INT = {"type": "integer"}
_BOOL = {"type": "boolean"}
_STRARR = {"type": "array", "items": {"type": "string"}}
_HEADERS = {"type": "object", "additionalProperties": {"type": "string"}}

URL_DESC = "Absolute URL. Must be inside the declared scope."


def _schema(name: str, description: str, properties: dict, required: list[str]) -> dict:
    return {
        "name": name,
        "description": description,
        "input_schema": {"type": "object", "properties": properties,
                         "required": required},
    }


TOOL_SCHEMAS: list[dict] = [
    _schema(
        "http_request",
        "Send one HTTP request inside scope. The full request and response are "
        "recorded in the transcript; cite the returned request_id as evidence. "
        "Redirects are NOT followed unless follow_redirects is true - a 3xx "
        "Location is itself evidence. Session cookies are kept by the client.",
        {
            "method": {**_STR, "description": "HTTP method, e.g. GET, POST, PUT, DELETE, OPTIONS"},
            "url": {**_STR, "description": URL_DESC},
            "headers": {**_HEADERS, "description": "Extra headers for this request only"},
            "body": {**_STR, "description": "Raw request body (for POST/PUT/PATCH)"},
            "follow_redirects": {**_BOOL, "description": "Follow 3xx chains (default false)"},
            "note": {**_STR, "description": "One-line note stored with the transcript entry"},
        },
        ["method", "url"],
    ),
    _schema(
        "crawl",
        "Breadth-first crawl from a URL, same-origin only. Returns pages, links, "
        "query parameters, and HTML forms (action, method, input names). Use "
        "early to map the attack surface.",
        {
            "url": {**_STR, "description": URL_DESC},
            "depth": {**_INT, "description": "Max link depth (default 2)"},
            "max_pages": {**_INT, "description": "Page cap (default 40)"},
        },
        ["url"],
    ),
    _schema(
        "js_recon",
        "Fetch a page, collect its JavaScript files, and extract API endpoints, "
        "fetch/axios calls, and secret-looking strings with file+line. Better "
        "than directory brute force for modern apps.",
        {"url": {**_STR, "description": URL_DESC}},
        ["url"],
    ),
    _schema(
        "fingerprint",
        "Passive recon on a URL: server/framework headers, cookie flags, "
        "security-header audit, robots.txt and sitemap.xml. Sends at most 3 "
        "requests.",
        {"url": {**_STR, "description": URL_DESC}},
        ["url"],
    ),
    _schema(
        "probe_reflection",
        "Reflected-XSS check: injects a unique canary into a parameter and "
        "reports whether it is reflected, in which context (html/attribute/"
        "script/url), and whether dangerous characters survive unescaped.",
        {
            "url": {**_STR, "description": URL_DESC + " Include the query string."},
            "param": {**_STR, "description": "Query parameter name to inject into"},
            "method": {**_STR, "description": "GET or POST (default GET)"},
            "data": {**_STR, "description": "POST body template; the value of param is replaced by the canary"},
        },
        ["url", "param"],
    ),
    _schema(
        "probe_sqli",
        "SQL-injection differential check on one parameter: baseline, a syntax "
        "probe (quote), and a matched true/false pair. Reports whether an SQL "
        "error appears or the true/false responses meaningfully differ.",
        {
            "url": {**_STR, "description": URL_DESC + " Include the query string."},
            "param": {**_STR, "description": "Parameter to test"},
            "method": {**_STR, "description": "GET or POST (default GET)"},
            "data": {**_STR, "description": "POST body template; param value is replaced"},
            "json_body": {**_BOOL, "description": "Send data as JSON object instead of form"},
        },
        ["url", "param"],
    ),
    _schema(
        "probe_time",
        "Time-based blind check: measures baseline latency, then sends "
        "DBMS-specific and shell sleep payloads (SLEEP, pg_sleep, WAITFOR, "
        "sleep/timeout command separators). Confirms only when injected latency "
        "clearly exceeds baseline + margin.",
        {
            "url": {**_STR, "description": URL_DESC + " Include the query string."},
            "param": {**_STR, "description": "Parameter to test"},
            "method": {**_STR, "description": "GET or POST (default GET)"},
            "data": {**_STR, "description": "POST body template; param value is replaced"},
            "delay_s": {**_INT, "description": "Requested sleep seconds (default 4)"},
        },
        ["url", "param"],
    ),
    _schema(
        "probe_ssti",
        "Server-side template injection check: sends arithmetic markers in "
        "Jinja2/Twig/ERB/Freemarker syntax ({{7*7}}, ${7*7}, <%= 7*7 %>) and "
        "reports which evaluated to 49.",
        {
            "url": {**_STR, "description": URL_DESC + " Include the query string."},
            "param": {**_STR, "description": "Parameter to test"},
            "method": {**_STR, "description": "GET or POST (default GET)"},
            "data": {**_STR, "description": "POST body template; param value is replaced"},
        },
        ["url", "param"],
    ),
    _schema(
        "probe_lfi",
        "Local file inclusion / path traversal check: sends traversal and "
        "absolute-path payloads, then looks for file-content markers "
        "(root:x: / [fonts] / etc) in the response.",
        {
            "url": {**_STR, "description": URL_DESC + " Include the query string."},
            "param": {**_STR, "description": "Parameter to test"},
        },
        ["url", "param"],
    ),
    _schema(
        "probe_redirect",
        "Open redirect check: sets the parameter to an external URL and reads "
        "the Location header of the response.",
        {
            "url": {**_STR, "description": URL_DESC + " Include the query string."},
            "param": {**_STR, "description": "Parameter that names the destination"},
        },
        ["url", "param"],
    ),
    _schema(
        "probe_cors",
        "CORS misconfiguration check: sends a foreign Origin and reports "
        "whether it is reflected in Access-Control-Allow-Origin, and whether "
        "credentials are allowed.",
        {"url": {**_STR, "description": URL_DESC}},
        ["url"],
    ),
    _schema(
        "probe_method",
        "OPTIONS check: reports Allow/Access-Control-Allow-Methods and tries "
        "PUT of a harmless canary file to detect writable methods.",
        {"url": {**_STR, "description": URL_DESC}},
        ["url"],
    ),
    _schema(
        "jwt_decode",
        "Decode a JWT/JWS without verifying: header, payload, algorithm, and "
        "weakness assessment (alg=none acceptance hints, HMAC weak-secret "
        "offline crack against a builtin wordlist). Analysis only - never forges.",
        {"token": {**_STR, "description": "The JWT string"}},
        ["token"],
    ),
    _schema(
        "load_skill",
        "Load a knowledge module (methodology for one bug class: detection, "
        "first probes, confirmation criteria, bypasses). Call 'index' for the "
        "list of available skills.",
        {"name": {**_STR, "description": "Skill name, e.g. sqli, xss, ssrf, idor, auth-session"}},
        ["name"],
    ),
    _schema(
        "note",
        "Append a working note to notes.md - hypotheses, dead ends, partial "
        "results. Use it so a later turn or a human reviewer can follow the "
        "reasoning.",
        {"text": {**_STR, "description": "Markdown text to append"}},
        ["text"],
    ),
    _schema(
        "read_notes",
        "Read back everything written to notes.md this session.",
        {},
        [],
    ),
    _schema(
        "record_finding",
        "Record a verified vulnerability. REQUIRES evidence: at least one "
        "request_id whose recorded response literally contains "
        "evidence_excerpt. A finding without verbatim response evidence is "
        "rejected. Record only confirmed issues - 'looks suspicious' is a note, "
        "not a finding.",
        {
            "title": {**_STR, "description": "Short title, e.g. 'Reflected XSS in /search q parameter'"},
            "severity": {**_STR, "description": "critical | high | medium | low | info"},
            "category": {**_STR, "description": "Bug class, e.g. xss, sqli, ssrf, idor, cors"},
            "url": {**_STR, "description": "Affected endpoint"},
            "evidence_ids": {**_STRARR, "description": "request_ids from tool results that prove it"},
            "evidence_excerpt": {**_STR, "description": "Verbatim quote from a cited response that proves the bug"},
            "description": {**_STR, "description": "What it is, how to reproduce, impact"},
            "remediation": {**_STR, "description": "How to fix it"},
        },
        ["title", "severity", "category", "url", "evidence_ids",
         "evidence_excerpt", "description", "remediation"],
    ),
    _schema(
        "run_external",
        "Run an installed external tool (sqlmap, nuclei, nmap, ffuf, curl) "
        "against an in-scope URL. Timeout-bounded, output truncated. The "
        "command and output are recorded; a scanner's claim is not evidence - "
        "verify with http_request before record_finding.",
        {
            "tool": {**_STR, "description": "sqlmap | nuclei | nmap | ffuf | curl"},
            "args": {**_STR, "description": "Argument string; URLs must stay in scope"},
            "timeout_s": {**_INT, "description": "Max run seconds (default 120, cap 600)"},
        },
        ["tool", "args"],
    ),
    _schema(
        "finish",
        "End the assessment. Call when testing is complete or budget is spent. "
        "Provide an honest summary: what was tested, what was found, what "
        "remains uncertain.",
        {"summary": {**_STR, "description": "Final assessment summary"}},
        ["summary"],
    ),
]


def dispatch(ctx: Context, name: str, arguments: dict) -> dict:
    """Run one tool call; never raises - errors come back as dicts."""
    try:
        fn = _impl(name)
    except KeyError:
        return {"error": f"unknown tool: {name}"}
    try:
        return {"result": fn(ctx, **(arguments or {}))}
    except TypeError as exc:
        return {"error": f"bad arguments for {name}: {exc}"}
    except Exception as exc:  # tool failures are data for the model
        return {"error": f"{type(exc).__name__}: {exc}"}
