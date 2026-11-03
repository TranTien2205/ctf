"""scan — template and signature scanners.

Both tools here produce *candidates*. A nuclei match and a nikto signature name
a class worth a hypothesis; neither is a finding, and the ledger will not accept
one as proof. The `next` field on every result says so, because the single most
common way an automated tester produces a false report is pasting a scanner's
label into a findings table.
"""
from __future__ import annotations

import json

from ... import config
from ...ledger.state import RECON
from .. import exec as ex
from ..mcp import Server, ToolContext

SERVER = Server("scan", "template and signature scanners; candidates only")


@SERVER.tool(
    "scan.nuclei",
    "Run nuclei's templates against one target and return each match with its template id, "
    "severity and matched part. Every match is a CANDIDATE: it names a class to open a hypothesis "
    "on, and the class's own proof requirement still has to be met before anything is recorded.",
    {"properties": {
        "target": {"type": "string"},
        "severity": {"type": "string", "description": "comma separated: info,low,medium,high,critical"},
        "tags": {"type": "string", "description": "comma separated template tags, e.g. cve,sqli,exposure"},
        "templates": {"type": "string", "description": "path to a template or directory"},
        "rate_limit": {"type": "integer", "description": "requests per second, default 50"},
        "max_seconds": {"type": "integer", "description": "default 300"},
        "headers": {"type": "object"},
    }, "required": ["target"]},
    tier=config.TIER_ACTIVE, vuln_class=RECON, step="template-scan", requires=("nuclei",),
)
def nuclei(context: ToolContext, target: str, severity: str = "low,medium,high,critical",
           tags: str = "", templates: str = "", rate_limit: int = 50, max_seconds: int = 300,
           headers: dict | None = None) -> dict:
    argv = ["nuclei", "-u", target, "-jsonl", "-silent", "-no-color", "-disable-update-check",
            "-severity", severity, "-rate-limit", str(max(1, min(int(rate_limit), 300))),
            "-timeout", "10", "-retries", "1"]
    if tags:
        argv += ["-tags", tags]
    if templates:
        argv += ["-t", templates]
    for name, value in (headers or {}).items():
        argv += ["-H", f"{name}: {value}"]
    result = ex.run(argv, timeout=max_seconds, log_path=context.command_log)
    matches = []
    for line in result.stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        info = record.get("info") or {}
        matches.append({"template": record.get("template-id"), "name": info.get("name"),
                        "severity": info.get("severity"), "matched": record.get("matched-at"),
                        "type": record.get("type"),
                        "tags": info.get("tags"), "cve": (info.get("classification") or {}).get("cve-id"),
                        "extracted": record.get("extracted-results")})
    by_severity: dict[str, int] = {}
    for match in matches:
        key = match.get("severity") or "unknown"
        by_severity[key] = by_severity.get(key, 0) + 1
    for match in matches:
        context.emit_surface(target, "candidate", match.get("template") or "unknown",
                             detail={k: v for k, v in match.items() if v})
    return {
        "summary": f"{len(matches)} nuclei match(es) on {target}: {by_severity or 'none'}",
        "result": "signal" if matches else "no-signal",
        "argv": argv, "exit_code": result.exit_code, "duration_ms": result.duration_ms,
        "data": {"matches": matches[:120], "by_severity": by_severity},
        "output": "\n".join(f"[{m['severity']}] {m['template']} -> {m['matched']}"
                            for m in matches[:120]) or result.text(2000),
        "evidence": {"kind": "probe", "target": target, "tool": "nuclei", "command": argv,
                     "extracted": {"candidate_count": len(matches),
                                   "templates": [m["template"] for m in matches[:60]]}},
        "next": ("open a hypothesis per credible match and meet that class's proof requirement; "
                 "a template id is not evidence"),
    }


@SERVER.tool(
    "scan.nikto",
    "Run nikto's signature checks against one HTTP service. Noisy by design and it will flag "
    "configuration observations as well as issues; treat every line as a candidate to confirm.",
    {"properties": {"target": {"type": "string"},
                    "max_seconds": {"type": "integer", "description": "default 420"},
                    "tuning": {"type": "string", "description": "nikto -Tuning value, e.g. 1234567"}},
     "required": ["target"]},
    tier=config.TIER_ACTIVE, vuln_class=RECON, step="signature-scan", requires=("nikto",),
)
def nikto(context: ToolContext, target: str, max_seconds: int = 420, tuning: str = "") -> dict:
    argv = ["nikto", "-h", target, "-Format", "json", "-output", "-", "-nointeractive",
            "-maxtime", str(max(30, min(int(max_seconds), 900)))]
    if tuning:
        argv += ["-Tuning", tuning]
    result = ex.run(argv, timeout=max_seconds + 60, log_path=context.command_log)
    findings = []
    text = result.stdout.strip()
    try:
        parsed = json.loads(text[text.index("{"):text.rindex("}") + 1]) if "{" in text else {}
        for item in (parsed.get("vulnerabilities") or []):
            findings.append({"id": item.get("id"), "method": item.get("method"),
                             "url": item.get("url"), "message": item.get("msg")})
    except (ValueError, json.JSONDecodeError):
        findings = [{"message": line.strip()} for line in result.stdout.splitlines()
                    if line.strip().startswith("+")]
    return {
        "summary": f"{len(findings)} nikto observation(s) on {target}",
        "result": "signal" if findings else "no-signal",
        "argv": argv, "exit_code": result.exit_code, "duration_ms": result.duration_ms,
        "data": {"observations": findings[:120]},
        "output": "\n".join(str(f.get("message")) for f in findings[:120]) or result.text(3000),
        "evidence": {"kind": "probe", "target": target, "tool": "nikto", "command": argv,
                     "extracted": {"observation_count": len(findings)}},
        "next": "pick the observations that imply a class and prove those; ignore the rest",
    }
