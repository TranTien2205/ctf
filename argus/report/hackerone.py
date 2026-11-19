"""A HackerOne-shaped report: one section per finding, with the PoC.

The existing renderers answer "what did this engagement find". A bug-bounty
triager asks something narrower and in a fixed order: what is it, how bad,
how do I reproduce it, and show me the bytes. This renders that shape.

Three refusals, and all three came out of reading what the recorder actually
holds rather than out of taste:

**NO SYNTHESISED `curl`.** A replay command composed from a recorded
exchange would carry `•••redacted•••` where twelve request header names and
`Set-Cookie` are masked, so it would be wrong to read AND wrong to send -
and a reader would reasonably assume a command in a PoC was the command that
ran. The literal recorded request is printed instead. Where the client
captured raw wire bytes (`request_text`), those are the PoC, because they
are what went out.

**NO URL IN ANY ATTRIBUTE.** Every byte in a finding is target-influenced,
and this file is served under `sandbox; default-src 'none'`. Text nodes only
means a hostile value has nowhere to go even if the escaping were wrong -
the same reasoning the operator console uses for having no `innerHTML` at
all rather than escaped `innerHTML`.

**ABSENCE IS PRINTED.** `html.py` renders a missing field as an empty cell -
an empty `<pre></pre>` under "Proof (verbatim excerpt)" - which reads as "no
proof" when it means "no field". Here every section that cannot be built
says which piece was missing. A finding may cite an EVENT id that has no
request at all (the shipped sample's jwt finding does), and that is a
sentence, not a blank box.

One more thing taken from `markdown.py` and not from `html.py`: the response
excerpt is CENTRED on the quoted evidence. `html.py` prints
`response.body[:4000]` from the start, so on a longer body whose proving
bytes are later, the HTML report omits the proof while the markdown report
shows it.
"""

from __future__ import annotations

from pathlib import Path

from .html import _esc, _GRADE_COLOR, _SEV_COLOR

__all__ = ["render_hackerone"]

#: Window around the quoted evidence. Smaller than html.py's 4000-byte
#: prefix because this one is centred: a triager needs the proving bytes and
#: their neighbourhood, not the top of the page.
_WINDOW = 1400

#: Request bytes to show. A PoC is one request; a body longer than this is
#: not making the case better.
_REQ_CAP = 2600

_CSS = """
:root{--bg:#fff;--fg:#17202b;--mut:#5d6b7a;--line:#dde3ea;--panel:#f7f9fb;
      --accent:#0b5fa5;color-scheme:light}
@media(prefers-color-scheme:dark){:root{--bg:#10151b;--fg:#e8eef4;--mut:#9fb0c0;
      --line:#243040;--panel:#172029;--accent:#64b5f6;color-scheme:dark}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);line-height:1.6;font-size:15px;
     font-family:system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}
.wrap{max-width:900px;margin:0 auto;padding:0 max(16px,env(safe-area-inset-left,0px))}
h1{font-size:26px;margin:28px 0 6px;line-height:1.25}
h2{font-size:20px;margin:0 0 4px;line-height:1.3}
h3{font-size:13px;letter-spacing:.09em;text-transform:uppercase;color:var(--mut);
   margin:20px 0 7px}
p{margin:0 0 10px;max-width:70ch}
.sub{color:var(--mut);font-size:13.5px;margin-bottom:26px}
.rep{border:1px solid var(--line);border-radius:10px;padding:18px 20px;margin:0 0 22px;
     background:var(--bg)}
.badges{display:flex;flex-wrap:wrap;gap:7px;margin:9px 0 4px}
.b{font-size:12px;font-weight:650;padding:3px 9px;border-radius:999px;color:#fff;
   font-family:ui-monospace,Menlo,Consolas,monospace}
.b-out{background:transparent;border:1px solid var(--line);color:var(--mut)}
dl{display:grid;grid-template-columns:auto 1fr;gap:4px 14px;margin:10px 0 0;
   font-size:14px}
dt{color:var(--mut);white-space:nowrap}
dd{margin:0;min-width:0;overflow-wrap:anywhere;font-family:ui-monospace,Menlo,Consolas,monospace;
   font-size:13px}
ol{margin:0 0 10px;padding-left:1.35em}
li{margin:5px 0}
pre{background:var(--panel);border:1px solid var(--line);border-radius:7px;
    padding:11px 13px;overflow-x:auto;font-size:12.5px;line-height:1.5;margin:0 0 10px;
    font-family:ui-monospace,Menlo,Consolas,monospace;white-space:pre-wrap;
    overflow-wrap:anywhere}
.absent{color:var(--mut);font-size:13.5px;font-style:italic;margin:0 0 10px}
.rid{font-family:ui-monospace,Menlo,Consolas,monospace;font-size:12px;color:var(--mut)}
footer{color:var(--mut);font-size:12.5px;padding:18px 0 34px;border-top:1px solid var(--line);
       margin-top:24px}
"""


def _req_lines(entry: dict) -> tuple[str, bool]:
    """The request as a triager should see it, and whether it is raw wire.

    `request_text` is what the client captured going out, already redacted.
    When it is absent the request is rebuilt from the recorded parts - and
    that rebuild is labelled, because a reader must not take a
    reconstruction for a capture.
    """
    req = (entry or {}).get("request") or {}
    text = req.get("request_text")
    if isinstance(text, str) and text.strip():
        return text[:_REQ_CAP], bool(req.get("raw"))
    method = str(req.get("method") or "?")
    url = str(req.get("url") or "?")
    out = [f"{method} {url}"]
    for key, value in (req.get("headers") or {}).items():
        if isinstance(value, (list, tuple)):
            for one in value:
                out.append(f"{key}: {one}")
        else:
            out.append(f"{key}: {value}")
    body = req.get("body")
    if isinstance(body, str) and body:
        out.append("")
        out.append(body[:_REQ_CAP])
    return "\n".join(out)[:_REQ_CAP], False


def _resp_window(entry: dict, quote: str) -> tuple[str, str]:
    """The response, centred on the quoted bytes. `(text, note)`."""
    resp = (entry or {}).get("response") or {}
    status = resp.get("status")
    head = [f"HTTP {status}" if status else "HTTP (no status recorded)"]
    for key, value in (resp.get("headers") or {}).items():
        if isinstance(value, (list, tuple)):
            for one in value:
                head.append(f"{key}: {one}")
        else:
            head.append(f"{key}: {value}")
    body = resp.get("body")
    body = body if isinstance(body, str) else ""
    note = ""
    if not body:
        return "\n".join(head), "the recorded response has no body"
    at = body.find(quote) if quote else -1
    if at < 0:
        shown = body[:_WINDOW]
        note = ("shown from the start of the body: the quoted excerpt was not "
                "found in it verbatim")
    else:
        start = max(0, at - _WINDOW // 3)
        shown = body[start:start + _WINDOW]
        if start:
            shown = "...\n" + shown
        if start + _WINDOW < len(body):
            shown = shown + "\n..."
        note = f"centred on the quoted bytes, at offset {at} of {len(body)}"
    return "\n".join(head) + "\n\n" + shown, note


def _steps(session, rids: list[str]) -> tuple[list[str], list[str]]:
    """Reproduction steps DERIVED from the cited exchanges, and the gaps.

    Nothing is authored here. argus stores no "steps" field - a search of the
    tree finds none - so inventing prose would be exactly the thing this
    whole system refuses. A step is a request that was really sent, in the
    order it was recorded.
    """
    steps, gaps = [], []
    for rid in rids:
        entry = session.get_exchange(rid)
        if entry is None:
            gaps.append(f"{rid} is cited but is not in the transcript")
            continue
        req = entry.get("request") or {}
        method, url = req.get("method"), req.get("url")
        if not method or not url:
            kind = str(entry.get("tool") or entry.get("kind") or "event")
            gaps.append(f"{rid} is a {kind} event, which carries no request - "
                        "its output is evidence but it is not a step")
            continue
        body = req.get("body")
        extra = ""
        if isinstance(body, str) and body.strip():
            extra = f" with body {body[:160]}"
        steps.append(f"{method} {url}{extra}")
    return steps, gaps


def _badges(finding: dict) -> str:
    """The badge row, as its own unit.

    Extracted from `_one` because it is a pure function of the finding
    and because the defect it now guards was invisible per renderer:
    markdown discussed the second reading, html returned an empty
    string for its absence, and this artifact - the one that leaves the
    machine for a bug-bounty reader - printed a PROOF badge and never
    mentioned cross-verification at all. A unit nobody can call alone
    is a unit nobody tests alone.
    """
    sev = str(finding.get("severity") or "")
    grade = str(finding.get("grade") or "")
    out: list[str] = []
    out.append('<div class="badges">')
    if sev:
        out.append(f'<span class="b" style="background:{_SEV_COLOR.get(sev, "#666")}">'
                   f'{_esc(sev.upper())}</span>')
    if grade:
        out.append(f'<span class="b" style="background:{_GRADE_COLOR.get(grade, "#666")}">'
                   f'PROOF: {_esc(grade.upper())}</span>')
    # A badge for the second reading, beside the badge for the first. The
    # PROOF badge is the matrix on the recorded BYTES: a fabricated excerpt
    # fails "the target produced the quoted bytes" and cannot reach
    # `proven`. It says nothing about whether the READING is right, and on
    # the artifact that leaves this machine for a bug-bounty reader, a proof
    # badge with no second opinion beside it reads as more verification than
    # was done. So the absence is a badge too.
    history = [v for v in (finding.get("judges") or []) if isinstance(v, dict)]
    if not history and isinstance(finding.get("judge"), dict):
        history = [finding["judge"]]
    real = [v for v in history if not v.get("error")]
    if not real:
        out.append('<span class="b" style="background:#6b6b6b">'
                   'NOT CROSS-VERIFIED</span>')
    else:
        disputes = [v for v in real if not v.get("agrees")]
        shown = disputes[0] if disputes else real[-1]
        who = str(shown.get("judge_model") or "another family")
        if disputes:
            out.append('<span class="b" style="background:#c0392b">'
                       f'DISPUTED BY {_esc(who.upper())}</span>')
        else:
            out.append('<span class="b" style="background:#2b7a4b">'
                       f'CROSS-VERIFIED BY {_esc(who.upper())}</span>')
    for label, key in (("CVSS", "cvss"), ("CWE", "cwe"), ("OWASP", "owasp")):
        value = str(finding.get(key) or "")
        if value:
            out.append(f'<span class="b b-out">{label} {_esc(value)}</span>')
    out.append("</div>")
    return "".join(out)


def _one(session, finding: dict) -> str:
    fid = str(finding.get("id") or "")
    title = str(finding.get("title") or "")
    sev = str(finding.get("severity") or "")
    grade = str(finding.get("grade") or "")
    rids = [str(r) for r in (finding.get("evidence_ids") or [])]
    quote = str(finding.get("evidence_excerpt") or "")

    out = ['<article class="rep">']
    out.append(f"<h2>{_esc(fid)}{' &mdash; ' if fid and title else ''}"
               f"{_esc(title) or '<em>no title was recorded</em>'}</h2>")

    out.append(_badges(finding))


    out.append("<dl>")
    out.append(f"<dt>Asset</dt><dd>{_esc(finding.get('url') or '(not recorded)')}</dd>")
    out.append(f"<dt>Class</dt><dd>{_esc(finding.get('vuln_class') or finding.get('category') or '(not recorded)')}</dd>")
    out.append(f"<dt>Evidence</dt><dd>{_esc(', '.join(rids) or '(none cited)')}</dd>")
    out.append("</dl>")

    out.append("<h3>Summary</h3>")
    desc = str(finding.get("description") or "")
    out.append(f"<p>{_esc(desc)}</p>" if desc else
               '<p class="absent">No description was recorded for this finding.</p>')

    out.append("<h3>Steps to reproduce</h3>")
    steps, gaps = _steps(session, rids)
    if steps:
        out.append("<ol>" + "".join(f"<li>{_esc(s)}</li>" for s in steps) + "</ol>")
    else:
        out.append('<p class="absent">No cited exchange carries a request, so '
                   'no step can be derived. Nothing is composed here: argus '
                   'stores no reproduction prose, and inventing it is the one '
                   'thing this report will not do.</p>')
    for gap in gaps:
        out.append(f'<p class="absent">{_esc(gap)}</p>')

    out.append("<h3>Proof of concept</h3>")
    shown_any = False
    for rid in rids:
        entry = session.get_exchange(rid)
        if entry is None:
            continue
        req = (entry.get("request") or {})
        if not req.get("method") and not req.get("request_text"):
            output = str((entry.get("response") or {}).get("body") or "")
            if output:
                shown_any = True
                kind = str(entry.get("tool") or "event")
                out.append(f'<p class="rid">{_esc(rid)} &mdash; {_esc(kind)} '
                           "event; it has no request, so this is its recorded "
                           "output only</p>")
                out.append(f"<pre>{_esc(output[:_WINDOW])}</pre>")
            continue
        shown_any = True
        req_text, raw = _req_lines(entry)
        label = ("raw wire bytes, as sent" if raw else
                 "rebuilt from the recorded request parts")
        out.append(f'<p class="rid">{_esc(rid)} request &mdash; {label}</p>')
        out.append(f"<pre>{_esc(req_text)}</pre>")
        resp_text, note = _resp_window(entry, quote)
        out.append(f'<p class="rid">{_esc(rid)} response &mdash; {_esc(note)}</p>')
        out.append(f"<pre>{_esc(resp_text)}</pre>")
    if not shown_any:
        out.append('<p class="absent">None of the cited ids resolved to a '
                   'recorded exchange, so there is no proof of concept to '
                   'show. A citation that does not resolve is a defect in the '
                   'finding, not a weak proof.</p>')

    if quote:
        out.append("<h3>Quoted evidence</h3>")
        out.append(f"<pre>{_esc(quote[:_WINDOW])}</pre>")

    proof = finding.get("proof") or {}
    missing = [str(m) for m in (proof.get("missing") or [])]
    if grade and grade != "proven":
        out.append("<h3>Why this is not graded proven</h3>")
        req_sentence = str(proof.get("requirement") or "")
        if req_sentence:
            out.append(f"<p>{_esc(req_sentence)}</p>")
        if missing:
            out.append("<ol>" + "".join(f"<li>{_esc(m)}</li>" for m in missing)
                       + "</ol>")
        else:
            out.append('<p class="absent">The grade is below proven and no '
                       'missing check was recorded, which is itself worth a '
                       'look.</p>')

    out.append("<h3>Remediation</h3>")
    rem = str(finding.get("remediation") or "")
    out.append(f"<p>{_esc(rem)}</p>" if rem else
               '<p class="absent">No remediation is offered. This system does '
               'not generate fix advice it has not observed to work, and an '
               'invented one would be the same failure as an invented '
               'finding.</p>')
    out.append("</article>")
    return "\n".join(out)


def render_hackerone(session, cfg, summary: str = "",
                     extra: dict | None = None) -> Path:
    """Write `report-h1.html` beside the other artifacts and return its path."""
    from ..session import _atomic_write, sanitized_findings

    findings = sanitized_findings(session.findings)
    order = {"proven": 0, "candidate": 1, "unproven": 2, "refused": 3}
    sev_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    findings.sort(key=lambda f: (order.get(str(f.get("grade") or ""), 9),
                                 sev_order.get(str(f.get("severity") or ""), 9)))

    target = str(getattr(session, "target", "") or "")
    body = [f"<style>{_CSS}</style>", '<div class="wrap">',
            "<h1>Vulnerability reports</h1>",
            f'<p class="sub">{_esc(target)} &middot; session '
            f"{_esc(getattr(session, 'id', ''))} &middot; "
            f"{len(findings)} report(s), strongest proof first</p>"]
    if not findings:
        body.append('<p class="absent">This session recorded no findings. '
                    'That is a result: the classes that were tried and '
                    'settled nothing are listed in the main report.</p>')
    for finding in findings:
        body.append(_one(session, finding))
    body.append("<footer>Every request and response above is quoted from this "
                "session's recorded transcript. No command here was composed: "
                "a replay command built from a redacted record would be wrong "
                "to read and wrong to send, so none is offered. Credential "
                "values are masked at record time and never recovered.</footer>")
    body.append("</div>")

    out = (session.dir / "report-h1.html")
    _atomic_write(out, "<!doctype html>\n<html lang=\"en\"><head>"
                       "<meta charset=\"utf-8\">"
                       "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
                       f"<title>Reports - {_esc(getattr(session, 'id', ''))}</title>"
                       "</head><body>\n" + "\n".join(body) + "\n</body></html>\n")
    return out
