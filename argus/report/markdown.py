"""Render findings + transcript into an audit-ready markdown report."""
from __future__ import annotations

import json
import re
import time
import urllib.parse
from pathlib import Path

from ..config import Config
from ..session import (SEVERITIES, Session, _cwe_of, _owasp_of,
                        sanitized_findings)
from ..httpclient import _redact_headers

_SEV_ORDER = {s: i for i, s in enumerate(SEVERITIES)}
_SEV_LABEL = {
    "critical": "Critical", "high": "High", "medium": "Medium",
    "low": "Low", "info": "Info",
}


def _excerpt(text: str, needle: str, span: int = 300) -> str:
    idx = text.find(needle)
    if idx < 0:
        return text[:span]
    start = max(0, idx - span // 3)
    return text[start: idx + len(needle) + span]


def _fence(text: str) -> str:
    """A ```-run inside untrusted bytes breaks a fixed-length fence and can
    inject fake report sections. Always fence one longer than the longest
    backtick run in the content."""
    longest = max((len(m.group()) for m in re.finditer(r"`+", text)),
                  default=0)
    return "`" * max(3, longest + 1)


def _code(text: str) -> str:
    """Inline-code for untrusted strings (URLs, ids) - a backtick inside the
    value would break the span, so fence wider when needed."""
    return f"`{text}`" if "`" not in str(text) else f"`` {text} ``"


def _join_list(v, empty: str) -> str:
    """', '.join over operator-editable meta.json values - a non-list
    must not crash or spew per-character output."""
    if not isinstance(v, list):
        return str(v) if v else empty
    return ", ".join(str(x) for x in v if x) or empty


def _tool_surface(meta: dict) -> str:
    """`--tools` restricted runs have different coverage - the report must
    say so. meta carries "all" or the sorted allowlist."""
    t = meta.get("tools")
    if isinstance(t, list):
        return (f"restricted to {len(t)} tools "
                f"({', '.join(str(x) for x in t[:8])}"
                f"{', …' if len(t) > 8 else ''})")
    return "all"


def _coverage(session: Session) -> dict:
    """What the run actually exercised - endpoints touched (method + path +
    param names, values stripped), probe families run, requests per tool."""
    tools: dict[str, int] = {}
    endpoints: set[str] = set()
    probes: set[str] = set()
    with session._lock:  # straggler workers may still append mid-render
        entries = list(session._transcript.values())
    for e in entries:
        if not isinstance(e, dict) or e.get("kind") == "artifacts_digest":
            continue  # the seal is bookkeeping, not exercised surface
        tool = str(e.get("tool") or e.get("kind") or "?")
        tools[tool] = tools.get(tool, 0) + 1
        if tool.startswith("probe_"):
            probes.add(tool)
        req = e.get("request")
        if not isinstance(req, dict) or not req.get("url"):
            continue
        try:
            p = urllib.parse.urlparse(str(req["url"]))
        except ValueError:
            continue  # tampered transcript line with an unparseable url
        names = sorted(k for k, _ in urllib.parse.parse_qsl(p.query))
        endpoints.add(f"{req.get('method', 'GET')} {p.path or '/'}"
                      + ("?" + "&".join(names) if names else ""))
    return {"requests_by_tool": dict(sorted(tools.items())),
            "endpoints": sorted(endpoints),
            "probes": sorted(probes)}


def _duration(session: Session) -> float:
    """Run duration: reuse the value stored in summary.json on first render
    so a re-rendered report shows the run's real length, not time-since."""
    try:
        prev = json.loads((session.dir / "summary.json").read_text(
            encoding="utf-8"))
        if prev.get("duration_s") is not None:
            return float(prev["duration_s"])
    except Exception:
        pass
    return round(time.time() - session.started, 1)


def render_report(session: Session, cfg: Config, summary: str = "",
                  extra: dict | None = None) -> Path:
    extra = dict(extra or {})
    # a re-render (`argus report`) must not drop run metrics the original
    # render recorded (mode, llm_calls, llm_tokens, agents) - they land as
    # top-level summary keys, so carry forward every key the canonical
    # schema does not own, under any freshly supplied ones
    _BASE = {"session", "findings", "counts", "requests", "duration_s",
             "time_to_first_finding_s", "coverage", "transcript_chain_head"}
    _prev = session.dir / "summary.json"
    if _prev.exists():
        try:
            _old = json.loads(_prev.read_text(encoding="utf-8"))
            extra = {**{k: v for k, v in _old.items() if k not in _BASE},
                     **extra}
        except (ValueError, OSError):
            pass
    coverage = _coverage(session)
    findings = sorted(sanitized_findings(session.findings),
                      key=lambda f: _SEV_ORDER.get(f["severity"], 99))
    counts: dict[str, int] = {}
    for f in findings:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1
    first_ts = min((f.get("ts", 0) for f in findings), default=0)
    ttf = round(first_ts - session.started, 1) \
        if first_ts and session.started else None

    lines = [
        f"# Penetration Test Report - {session.id}",
        "",
        f"- **Target:** `{session.dir.name.split('-', 2)[-1]}` ({session.dir.name})",
        f"- **Date:** {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(session.started))}",
        f"- **Duration:** {_duration(session)}s",
        f"- **Agent model:** {cfg.model}",
        f"- **Requests sent:** {session._seq}",
        "",
        "## Executive summary",
        "",
        summary or "_No agent summary was recorded._",
        "",
    ]
    meta = {}
    mp = session.dir / "meta.json"
    if mp.exists():
        try:
            meta = json.loads(mp.read_text(encoding="utf-8"))
        except Exception:
            meta = {}
        if not isinstance(meta, dict):
            meta = {}
    if meta.get("operator"):
        lines.insert(6, f"- **Operator:** {meta['operator']}")
    lines += [
        "| Severity | Count |",
        "|---|---|",
    ]
    for sev in SEVERITIES:
        if counts.get(sev):
            lines.append(f"| {_SEV_LABEL[sev]} | {counts[sev]} |")
    if not findings:
        lines.append("| - | 0 |")
    def _o(f):
        return f.get("owasp") or _owasp_of(
            f.get("cwe") or _cwe_of(f.get("category")))
    owasp_counts: dict[str, list] = {}
    for f in findings:
        if _o(f):
            owasp_counts.setdefault(_o(f), []).append(f["id"])
    if owasp_counts:
        lines += ["", "| OWASP Top 10 (2021) | Findings |", "|---|---|"]
        for o in sorted(owasp_counts):
            lines.append(f"| {o} | {', '.join(owasp_counts[o])} |")
    lines += [
        "",
        "## Engagement constraints",
        "",
        f"- **Scope hosts:** {_join_list(meta.get('scope'), '(target only)')}",
        f"- **Excluded paths:** {_join_list(meta.get('exclude_paths'), 'none')}",
        f"- **Budgets:** {meta.get('max_turns', '?')} turns, "
        f"{meta.get('max_requests', '?')} requests, {meta.get('rate_rps', '?')} rps",
        f"- **Proxy:** {'yes' if meta.get('proxy') else 'no'} · "
        f"**TLS verify:** {'yes' if meta.get('tls_verify') else 'no'}",
        f"- **Tool surface:** {_tool_surface(meta)}",
        "",
    ]

    lines += ["", "## Findings", ""]
    for f in findings:
        lines += [
            f"### {f['id']} - {f['title']}",
            "",
            f"- **Severity:** {_SEV_LABEL.get(f['severity'], f['severity'])}",
            *([f"- **CVSS:** `{f['cvss']}`"] if f.get("cvss") else []),
            f"- **Category:** {f['category']}",
            *([f"- **CWE:** `{f.get('cwe') or _cwe_of(f['category'])}`"]
              if f.get("cwe") or _cwe_of(f.get("category")) else []),
            *([f"- **OWASP:** {f.get('owasp') or _owasp_of(f.get('cwe') or _cwe_of(f['category']))}"]
              if f.get("owasp") or _owasp_of(f.get("cwe") or _cwe_of(f.get("category"))) else []),
            f"- **Endpoint:** {_code(f['url'])}",
            f"- **Evidence:** {', '.join(f['evidence_ids'])}",
            "",
            f"**Description**  ",
            f"{f['description']}",
            "",
            "**Proof (verbatim excerpt)**  ",
            _fence(f["evidence_excerpt"]),
            f["evidence_excerpt"][:1200],
            _fence(f["evidence_excerpt"]),
            "",
            "**Remediation**  ",
            f"{f['remediation']}",
            "",
        ]
        for rid in f["evidence_ids"]:
            entry = session.get_exchange(rid)
            if not entry or "request" not in entry:
                continue
            req, resp = entry["request"], entry.get("response") or {}
            # transcripts written before header redaction still hold live
            # operator secrets - re-redact at render so the shareable
            # report never carries them
            req_headers = _redact_headers(req.get("headers") or {}, set())
            block = "\n".join(
                [f"{req.get('method')} {req.get('url')}"]
                + [f"{k}: {v}" for k, v in req_headers.items()]
                + (["", str(req["body"])[:800]] if req.get("body") else [])
                + ["", f"HTTP/{resp.get('status')}"]
                + [f"{k}: {v}" for k, v
                   in list(_redact_headers(
                       resp.get("headers") or {}, set()).items())[:15]]
                + ["", _excerpt(resp.get("body", ""),
                                f["evidence_excerpt"])[:1500]])
            lines += [
                f"<details><summary>Transcript {rid}: {req.get('method')} "
                f"{req.get('url')} -> {resp.get('status')}</summary>",
                "",
                _fence(block) + "http",
                block,
                _fence(block),
                "</details>",
                "",
            ]

    agents = extra.get("agents")
    if agents:
        lines += [
            "## Agent metrics",
            "",
            "| Agent | Role | Status | Turns | Requests | Tokens in/out | LLM calls | Findings |",
            "|---|---|---|---|---|---|---|---|",
        ]
        by_agent: dict[str, int] = {}
        for f in findings:
            if f.get("agent"):
                by_agent[f["agent"]] = by_agent.get(f["agent"], 0) + 1
        for name, a in agents.items():
            tok = a.get("tokens") or {}
            lines.append(
                f"| {name} | {a.get('role', '')} | {a.get('status', '')} | "
                f"{a.get('turns', 0)} | {a.get('requests', 0)} | "
                f"{tok.get('in', 0)}/{tok.get('out', 0)} | "
                f"{a.get('llm_calls', 0)} | {by_agent.get(name, 0)} |")
        if ttf is not None:
            lines += ["", f"**Time to first finding:** {ttf}s", ""]

    lines += ["", "## Test coverage", ""]
    lines.append("| Tool | Requests |")
    lines.append("|---|---|")
    for tool, n in coverage["requests_by_tool"].items():
        lines.append(f"| {tool} | {n} |")
    lines += ["",
              f"**Probe families run:** "
              f"{', '.join(coverage['probes']) or 'none'}",
              "",
              f"**Endpoints exercised ({len(coverage['endpoints'])}):**", ""]
    for ep in coverage["endpoints"][:80]:
        lines.append(f"- {_code(ep)}")
    if len(coverage["endpoints"]) > 80:
        lines.append(f"- _...and {len(coverage['endpoints']) - 80} more "
                     "(see summary.json)_")
    lines.append("")

    lines += [
        "## Methodology",
        "",
        "Autonomous agent run: recon (fingerprint, crawl, js_recon) -> input",
        "mapping -> hypothesis-driven probes (matched true/false pairs,",
        "baseline-diffed) -> verification -> evidence-gated findings.",
        f"The complete request/response transcript is in `transcript.jsonl`",
        f"({session._seq} entries). Working notes are in `notes.md`.",
        "",
        "_All findings cite verbatim response excerpts verified against the",
        "recorded transcript at write time._",
    ]

    notes_path = session.dir / "notes.md"
    if notes_path.exists():
        notes = notes_path.read_text(encoding="utf-8", errors="replace")
        if notes.strip():
            f_ = _fence(notes)
            lines += [
                "",
                "<details><summary>Appendix: agent working notes "
                "(audit)</summary>",
                "",
                f_,
                notes[:20000],
                f_,
                "</details>",
            ]

    path = session.dir / "report.md"
    with path.open("w", encoding="utf-8", newline="") as fh:
        fh.write("\n".join(lines))
    summary_json = {
        "session": session.id,
        "findings": findings,
        "counts": counts,
        "requests": session._seq,
        "duration_s": _duration(session),
        "time_to_first_finding_s": ttf,
        "coverage": coverage,
        # anchoring the last chain link makes tail truncation detectable:
        # verify compares the transcript's final link against this value
        "transcript_chain_head": getattr(session, "_last_chain", ""),
        **extra,
    }
    from ..session import _atomic_write
    _atomic_write(session.dir / "summary.json",
                  json.dumps(summary_json, indent=2, ensure_ascii=False))
    try:
        from .html import render_html
        render_html(session, cfg, summary, extra)
    except Exception:
        pass  # html is a convenience; the markdown report is canonical
    try:
        from .sarif import render_sarif
        render_sarif(session)
    except Exception:
        pass  # sarif is CI-integrations glue; never block the report
    return path
