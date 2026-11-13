"""Self-contained HTML report: the same audit data as report.md, styled for
reading in a browser / pasting into slide decks. No external assets."""
from __future__ import annotations

import html
import time
from pathlib import Path

from .. import __version__

from ..session import (Session, SEVERITIES, _cwe_of, _owasp_of,
                        sanitized_findings)
from .markdown import _tool_surface
from ..config import Config
from .markdown import _coverage, _SEV_ORDER

_SEV_COLOR = {"critical": "#7c1d1d", "high": "#c0392b", "medium": "#e67e22",
              "low": "#2980b9", "info": "#7f8c8d"}

_CSS = """
body{font-family:system-ui,Segoe UI,Arial,sans-serif;margin:2rem auto;
max-width:960px;color:#222;line-height:1.5}
h1{border-bottom:3px solid #333;padding-bottom:.4rem}
h2{margin-top:2rem;border-bottom:1px solid #ccc;padding-bottom:.2rem}
.meta{color:#555;font-size:.9rem}
table{border-collapse:collapse;margin:.6rem 0}
td,th{border:1px solid #bbb;padding:.3rem .8rem;text-align:left}
.badge{display:inline-block;color:#fff;border-radius:4px;
padding:.1rem .5rem;font-size:.8rem;font-weight:600}
.finding{border:1px solid #ddd;border-left:6px solid #999;border-radius:6px;
padding:1rem 1.2rem;margin:1rem 0;background:#fafafa}
pre{background:#1e1e1e;color:#ddd;padding:.7rem;border-radius:6px;
overflow-x:auto;font-size:.82rem;white-space:pre-wrap}
details{margin:.4rem 0}
summary{cursor:pointer;color:#0366d6}
code{background:#eee;padding:.05rem .3rem;border-radius:3px}
"""


def _esc(s) -> str:
    return html.escape(str(s or ""))


def render_html(session: Session, cfg: Config, summary: str = "",
                extra: dict | None = None) -> Path:
    coverage = _coverage(session)
    findings = sorted(sanitized_findings(session.findings),
                      key=lambda f: _SEV_ORDER.get(f["severity"], 99))
    counts: dict[str, int] = {}
    for f in findings:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1

    sev_rows = "".join(
        f"<tr><td><span class='badge' style='background:{_SEV_COLOR[s]}'>"
        f"{s.upper()}</span></td><td>{counts[s]}</td></tr>"
        for s in SEVERITIES if counts.get(s)) or "<tr><td>-</td><td>0</td></tr>"

    cards = []
    for f in findings:
        ex = "".join(
            f"<details><summary>Transcript {_esc(rid)}: "
            f"{_esc((session.get_exchange(rid) or {}).get('request', {}).get('method'))} "
            f"{_esc((session.get_exchange(rid) or {}).get('request', {}).get('url'))} -> "
            f"{_esc(((session.get_exchange(rid) or {}).get('response') or {}).get('status'))}"
            f"</summary><pre>{_esc(((session.get_exchange(rid) or {}).get('response') or {}).get('body', '')[:4000])}</pre></details>"
            for rid in f["evidence_ids"])
        cards.append(
            f"<div class='finding' style='border-left-color:"
            f"{_SEV_COLOR.get(f['severity'], '#999')}'>"
            f"<h3>{_esc(f['id'])} - {_esc(f['title'])}</h3>"
            f"<p><span class='badge' style='background:"
            f"{_SEV_COLOR.get(f['severity'], '#999')}'>"
            f"{_esc(f['severity']).upper()}</span> "
            f"<b>Category:</b> {_esc(f['category'])} &nbsp; "
            f"<b>Endpoint:</b> <code>{_esc(f['url'])}</code>"
            + (f" &nbsp; <b>CVSS:</b> <code>{_esc(f['cvss'])}</code>"
               if f.get("cvss") else "")
            + (f" &nbsp; <b>CWE:</b> <code>{_esc(f.get('cwe') or _cwe_of(f.get('category')))}</code>"
               if f.get("cwe") or _cwe_of(f.get("category")) else "")
            + (f" &nbsp; <b>OWASP:</b> {_esc(f.get('owasp') or _owasp_of(f.get('cwe') or _cwe_of(f.get('category'))))}"
               if f.get("owasp") or _owasp_of(f.get("cwe") or _cwe_of(f.get("category"))) else "")
            + f"</p><p><b>Description</b><br>{_esc(f['description'])}</p>"
            f"<p><b>Proof (verbatim excerpt)</b></p>"
            f"<pre>{_esc(f['evidence_excerpt'][:1200])}</pre>"
            f"{ex}<p><b>Remediation</b><br>{_esc(f['remediation'])}</p></div>")

    meta = {}
    mp = session.dir / "meta.json"
    if mp.is_file():
        try:
            import json as _j
            meta = _j.loads(mp.read_text(encoding="utf-8"))
        except Exception:
            meta = {}
        if not isinstance(meta, dict):
            meta = {}
    from .markdown import _join_list
    constraints = (
        f"<p><b>Scope hosts:</b> {_esc(_join_list(meta.get('scope'), '(target only)'))}<br>"
        f"<b>Excluded paths:</b> {_esc(_join_list(meta.get('exclude_paths'), 'none'))}<br>"
        f"<b>Budgets:</b> {_esc(meta.get('max_turns','?'))} turns, "
        f"{_esc(meta.get('max_requests','?'))} requests, {_esc(meta.get('rate_rps','?'))} rps<br>"
        f"<b>Proxy:</b> {'yes' if meta.get('proxy') else 'no'} · "
        f"<b>TLS verify:</b> {'yes' if meta.get('tls_verify') else 'no'}<br>"
        f"<b>Tool surface:</b> {_esc(_tool_surface(meta))}</p>")

    ep_rows = "".join(f"<tr><td><code>{_esc(e)}</code></td></tr>"
                      for e in coverage["endpoints"])
    probe_row = ", ".join(f"<code>{_esc(p)}</code>"
                          for p in coverage["probes"]) or "-"
    tool_rows = "".join(f"<tr><td>{_esc(t)}</td><td>{n}</td></tr>"
                        for t, n in coverage["requests_by_tool"].items())

    notes_html = ""
    notes_path = session.dir / "notes.md"
    if notes_path.exists():
        notes = notes_path.read_text(encoding="utf-8", errors="replace")
        if notes.strip():
            notes_html = ("<details><summary>Appendix: agent working notes "
                          "(audit)</summary><pre>" + _esc(notes[:20000]) +
                          "</pre></details>")

    doc = f"""<!doctype html><html><head><meta charset="utf-8">
<title>Argus report - {_esc(session.id)}</title><style>{_CSS}</style></head>
<body>
<h1>Penetration Test Report</h1>
<p class="meta"><b>Session:</b> {_esc(session.id)}<br>
<b>Date:</b> {_esc(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(session.started)))}<br>
<b>Agent model:</b> {_esc(cfg.model)} &nbsp; <b>Requests:</b> {session._seq} &nbsp; <b>Argus:</b> {_esc(str(meta.get('argus_version') or __version__))}{('<br><b>Operator:</b> ' + _esc(meta['operator'])) if meta.get('operator') else ''}</p>
<h2>Executive summary</h2>
<p>{_esc(summary) or '<i>No agent summary recorded.</i>'}</p>
<table><tr><th>Severity</th><th>Count</th></tr>{sev_rows}</table>
<h2>Engagement constraints</h2>
{constraints}
<h2>Findings</h2>
{''.join(cards) or '<p><i>No findings recorded.</i></p>'}
<h2>Test coverage</h2>
<p><b>Probes exercised:</b> {probe_row}</p>
<table><tr><th>Endpoint touched</th></tr>{ep_rows}</table>
<table><tr><th>Tool</th><th>Requests</th></tr>{tool_rows}</table>
{notes_html}
<p class="meta">Generated by Argus v{_esc(__version__)} - every finding
cites verbatim response bytes verified against the recorded transcript.</p>
</body></html>"""

    path = session.dir / "report.html"
    from ..session import _atomic_write
    _atomic_write(path, doc)
    return path
