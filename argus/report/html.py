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
from .markdown import (_coverage, _GRADE_MEANING, _GRADE_ORDER, _SEV_ORDER)

_GRADE_COLOR = {"proven": "#1e7b34", "candidate": "#b8860b",
                "unproven": "#6b7280", "refused": "#4b5563",
                "ungraded": "#6b7280"}


def _proof_html(f: dict) -> str:
    """The grade, its requirement and the checks, on the card itself.

    report.md carried this and report.html did not, so a reader handed the
    styled file - which is the one meant for a presentation - saw a critical
    finding with nothing saying it was a candidate.
    """
    verdict = f.get("proof") if isinstance(f.get("proof"), dict) else {}
    if not verdict:
        return ""
    rows = "".join(
        f"<li>{'&#10003;' if c.get('ok') else '&#10007;'} "
        f"{_esc(c.get('check', ''))}"
        + (f" &mdash; <i>{_esc(c.get('detail', ''))}</i>"
           if c.get("detail") else "") + "</li>"
        for c in verdict.get("checks") or [])
    req = _esc(verdict.get("requirement") or "")
    return ("<details><summary><b>Proof grade: "
            f"{_esc(f.get('grade', '?'))}</b></summary>"
            + (f"<p class='meta'>Requirement for "
               f"{_esc(verdict.get('vuln_class') or '')}: {req}</p>" if req else "")
            + f"<ul>{rows}</ul></details>")

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


def _started_text(session: Session) -> str:
    """The start time, or a value a reader can tell is absent.

    `session.started` is 0.0 on a reopen whose meta.json is missing,
    corrupt or lacks the stamp. `markdown.py` guards that and prints
    "unknown (this session's meta.json carries no start time)"; this file
    and `sarif.py` did not, so the same session dated itself
    `1969-12-31 19:00:00` here and `1970-01-01T00:00:00Z` there, over a
    report carrying six real findings. The date is what an authorisation
    reviewer checks against the window the engagement was authorised for,
    and a 1970 stamp is not a missing value a consumer can detect - it is a
    definite wrong answer, in local time here and UTC there, so the two
    artifacts did not even agree with each other.
    """
    if session.started and session.started > 0:
        return time.strftime('%Y-%m-%d %H:%M:%S',
                             time.localtime(session.started))
    return "unknown (this session's meta.json carries no start time)"


def _judge_html(f: dict) -> str:
    """What cross-verification decided, in the artifact the client reads.

    `judge.apply_verdict` writes five fields - `judges`, `judge`,
    `disputed`, `severity_claimed`, `class_disputed` - and this renderer
    read none of them. Measured by driving the sequence `argus judge`
    performs: report.md printed "DISPUTED by cross-verification", while
    report.html showed an unqualified green `PROOF: PROVEN` and contained
    no occurrence of "disput" at all. A severity the judge lowered
    vanished the same way: the reduced value was shown with no record that
    it had ever been claimed higher.

    Cross-verification exists so a second model's disagreement reaches a
    human. In the one artifact handed to that human it reached nobody.
    """
    j = f.get("judge") if isinstance(f.get("judge"), dict) else {}
    disputed = bool(f.get("disputed"))
    claimed = f.get("severity_claimed")
    klass = f.get("class_disputed")
    if not (j or disputed or claimed or klass):
        return ""
    bits = []
    if disputed:
        bits.append("<b>DISPUTED by cross-verification</b>"
                    + (f" ({_esc(j.get('judge_model') or '')})"
                       if j.get("judge_model") else ""))
    elif j:
        bits.append("Cross-verification: "
                    + ("agreed" if j.get("agrees") else "no verdict")
                    + (f" ({_esc(j.get('judge_model') or '')})"
                       if j.get("judge_model") else ""))
    if j.get("reason"):
        bits.append(f"Reason: <i>{_esc(str(j['reason'])[:600])}</i>")
    miss = [str(m) for m in (j.get("missing") or [])]
    if miss:
        bits.append("Would settle it: "
                    + ", ".join(_esc(m) for m in miss[:8]))
    if klass:
        bits.append(f"Class disputed: read as <code>{_esc(str(klass))}</code>")
    if claimed:
        bits.append(f"Severity was claimed <code>{_esc(str(claimed))}</code>"
                    + (" (unrated before the judge)"
                       if f.get("severity_was_unrated") else "")
                    + f", shown as <code>{_esc(f.get('severity') or '')}</code>")
    style = ("border-left:6px solid #c0392b;background:#fdf2f0"
             if disputed else "border-left:6px solid #999;background:#f4f4f4")
    return (f"<div style=\"{style};padding:.6rem .9rem;margin:.8rem 0\">"
            + "<br>".join(bits) + "</div>")


def render_html(session: Session, cfg: Config, summary: str = "",
                extra: dict | None = None) -> Path:
    # `extra` was in this signature and read nowhere in the body, while
    # `markdown.render_report` passed it in. Measured: rendering the same
    # session twice, once with `extra["error"]` set exactly as `loop.py`
    # sets it and once without, produced two report.html files IDENTICAL
    # after normalising the session id and timestamps - the dead run's page
    # said "No findings recorded." and footered "every finding cites
    # verbatim response bytes verified against the recorded transcript",
    # with no mention of the failure. report.md differed correctly by its
    # banner. The fix for "a dead run looks clean" landed in one of three
    # readers, and the one it missed is the one the client is handed.
    extra = dict(extra or {})
    run_error = str(extra.get("error") or "").strip()
    banner = (
        "<div style=\"border:3px solid #7c1d1d;background:#fdecea;"
        "padding:1rem 1.2rem;margin:1rem 0;border-radius:6px\">"
        "<b style=\"color:#7c1d1d\">RUN DID NOT COMPLETE.</b> "
        f"<code>{_esc(run_error)}</code><br>"
        "Every figure on this page describes an incomplete run. Findings "
        "may be missing because the run stopped, not because the target is "
        "clean.</div>") if run_error else ""
    coverage = _coverage(session)
    findings = sorted(sanitized_findings(session.findings),
                      key=lambda f: (_GRADE_ORDER.get(f.get("grade", ""), 9),
                                     _SEV_ORDER.get(f["severity"], 99)))
    counts: dict[str, int] = {}
    grades: dict[str, int] = {}
    for f in findings:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1
        # an ungraded row was counted nowhere, so it appeared as a card with no
        # line in the table that is supposed to summarise the cards
        key = f.get("grade") or "ungraded"
        grades[key] = grades.get(key, 0) + 1

    grade_rows = "".join(
        f"<tr><td><span class='badge' style='background:"
        f"{_GRADE_COLOR.get(g, '#999')}'>{g.upper()}</span></td>"
        f"<td>{grades[g]}</td><td>{_GRADE_MEANING.get(g, '')}</td></tr>"
        for g in ("proven", "candidate", "unproven", "refused", "ungraded")
        if grades.get(g))

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
            + (f"<span class='badge' style='background:"
               f"{_GRADE_COLOR.get(f.get('grade', ''), '#999')}'>"
               f"PROOF: {_esc(f.get('grade', '')).upper()}</span> &nbsp; "
               if f.get("grade") else "")
            + ("<span class='badge' style='background:#7c1d1d'>DISPUTED"
               "</span> &nbsp; " if f.get("disputed") else "")
            + f"<b>Category:</b> {_esc(f['category'])} &nbsp; "
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
            f"{ex}<p><b>Remediation</b><br>{_esc(f['remediation'])}</p>"
            f"{_judge_html(f)}{_proof_html(f)}</div>")

    meta = {}
    meta_read = False
    mp = session.dir / "meta.json"
    if mp.is_file():
        try:
            import json as _j
            meta = _j.loads(mp.read_text(encoding="utf-8"))
            meta_read = True
        except Exception:
            meta = {}
        if not isinstance(meta, dict):
            meta, meta_read = {}, False
    from .markdown import _join_list
    # Same fallbacks-to-negatives as markdown.py had: see the long note
    # there. "TLS verify: no" and "Tool surface: all" are claims about how
    # the engagement was conducted, and a missing meta.json makes them
    # wrongly in the direction of a broader test than was run.
    _unk = "not recorded"
    constraints = (
        ("<p style=\"border-left:6px solid #e67e22;background:#fdf6ec;"
         "padding:.6rem .9rem\"><b>Engagement constraints are not on "
         "record for this session:</b> <code>meta.json</code> is missing "
         "or unreadable, so the values below are unknown rather than "
         "defaults.</p>" if not meta_read else "")
        + f"<p><b>Scope hosts:</b> {_esc(_join_list(meta.get('scope'), '(target only)') if meta_read else _unk)}<br>"
        f"<b>Excluded paths:</b> {_esc(_join_list(meta.get('exclude_paths'), 'none') if meta_read else _unk)}<br>"
        f"<b>Budgets:</b> {_esc(meta.get('max_turns','?'))} turns, "
        f"{_esc(meta.get('max_requests','?'))} requests, {_esc(meta.get('rate_rps','?'))} rps<br>"
        f"<b>Proxy:</b> {('yes' if meta.get('proxy') else 'no') if meta_read else _unk} · "
        f"<b>TLS verify:</b> {('yes' if meta.get('tls_verify') else 'no') if meta_read else _unk}<br>"
        f"<b>Tool surface:</b> {_esc(_tool_surface(meta) if meta_read else _unk)}</p>")

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
{banner}
<p class="meta"><b>Session:</b> {_esc(session.id)}<br>
<b>Date:</b> {_esc(_started_text(session))}<br>
<b>Agent model:</b> {_esc(cfg.model)} &nbsp; <b>Requests:</b> {session.requests_sent} &nbsp; <b>Argus:</b> {_esc(str(meta.get('argus_version') or __version__))}{('<br><b>Operator:</b> ' + _esc(meta['operator'])) if meta.get('operator') else ''}</p>
<h2>Executive summary</h2>
<p>{_esc(summary) or '<i>No agent summary recorded.</i>'}</p>
<table><tr><th>Severity</th><th>Count</th></tr>{sev_rows}</table>
<h2>Engagement constraints</h2>
{constraints}
<h2>Proof grades</h2>
<table><tr><th>Grade</th><th>Count</th><th>Meaning</th></tr>
{grade_rows or '<tr><td>-</td><td>0</td><td></td></tr>'}</table>
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
