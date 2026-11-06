"""Render findings + transcript into an audit-ready markdown report."""
from __future__ import annotations

import json
import time
from pathlib import Path

from ..config import Config
from ..session import SEVERITIES, Session

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


def render_report(session: Session, cfg: Config, summary: str = "") -> Path:
    findings = sorted(session.findings,
                      key=lambda f: _SEV_ORDER.get(f["severity"], 99))
    counts: dict[str, int] = {}
    for f in findings:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1

    lines = [
        f"# Penetration Test Report - {session.id}",
        "",
        f"- **Target:** `{session.dir.name.split('-', 2)[-1]}` ({session.dir.name})",
        f"- **Date:** {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(session.started))}",
        f"- **Duration:** {round(time.time() - session.started, 1)}s",
        f"- **Agent model:** {cfg.model}",
        f"- **Requests sent:** {session._seq}",
        "",
        "## Executive summary",
        "",
        summary or "_No agent summary was recorded._",
        "",
        "| Severity | Count |",
        "|---|---|",
    ]
    for sev in SEVERITIES:
        if counts.get(sev):
            lines.append(f"| {_SEV_LABEL[sev]} | {counts[sev]} |")
    if not findings:
        lines.append("| - | 0 |")

    lines += ["", "## Findings", ""]
    for f in findings:
        lines += [
            f"### {f['id']} - {f['title']}",
            "",
            f"- **Severity:** {_SEV_LABEL.get(f['severity'], f['severity'])}",
            f"- **Category:** {f['category']}",
            f"- **Endpoint:** `{f['url']}`",
            f"- **Evidence:** {', '.join(f['evidence_ids'])}",
            "",
            f"**Description**  ",
            f"{f['description']}",
            "",
            "**Proof (verbatim excerpt)**  ",
            "```",
            f["evidence_excerpt"][:1200],
            "```",
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
            lines += [
                f"<details><summary>Transcript {rid}: {req.get('method')} "
                f"{req.get('url')} -> {resp.get('status')}</summary>",
                "",
                "```http",
                f"{req.get('method')} {req.get('url')}",
            ]
            for k, v in (req.get("headers") or {}).items():
                lines.append(f"{k}: {v}")
            if req.get("body"):
                lines += ["", str(req["body"])[:800]]
            lines += [
                "",
                f"HTTP/{resp.get('status')}",
            ]
            for k, v in list((resp.get("headers") or {}).items())[:15]:
                lines.append(f"{k}: {v}")
            lines += [
                "",
                _excerpt(resp.get("body", ""), f["evidence_excerpt"])[:1500],
                "```",
                "</details>",
                "",
            ]

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

    path = session.dir / "report.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    summary_json = {
        "session": session.id,
        "findings": findings,
        "counts": counts,
        "requests": session._seq,
    }
    (session.dir / "summary.json").write_text(
        json.dumps(summary_json, indent=2, ensure_ascii=False))
    return path
