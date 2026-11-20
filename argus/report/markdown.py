"""Render findings + transcript into an audit-ready markdown report."""
from __future__ import annotations

import json
import re
import time
import urllib.parse
from pathlib import Path

from .. import __version__
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


def _h(value) -> str:
    """HTML-escape a value going into one of report.md's raw HTML elements.

    Markdown's fenced blocks are safe - a viewer does not parse their
    contents - but `<details><summary>` is an element this renderer opens
    itself, and what goes inside it IS parsed. Quotes included, because the
    value lands in element content that a viewer may be re-serialising into
    an attribute elsewhere.
    """
    import html as _html
    return _html.escape(str("" if value is None else value), quote=True)


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


def _verification_coverage(findings: list | None) -> dict:
    """How many findings each verification layer actually REACHED.

    MEASURED ON THIS REPOSITORY'S OWN SEALED EVIDENCE, which is why this
    exists: across four sessions and 16 findings, 14 proven and 2 candidate,
    every finding carried a CWE and cited evidence ids - and ZERO had been
    read by a second model, and zero had been re-verified against the
    target. Both layers existed, were tested, and had never touched a real
    finding.

    Nothing in any report said so. A reader saw `proven` beside each
    finding and had no way to learn that `proven` was the whole of the
    verification. The three layers answer three different questions:

      the matrix   did the target produce the quoted bytes?
      a judge      do those bytes demonstrate the class claimed?
      a replay     does the target still do it?

    A verdict carrying an `error` is NOT coverage for either layer - the
    question was asked and did not arrive - and an `inconclusive` replay is
    not coverage, for the same reason.
    """
    rows = [f for f in (findings or []) if isinstance(f, dict)]
    total = len(rows)

    def _judged(f: dict) -> bool:
        hist = [v for v in (f.get("judges") or []) if isinstance(v, dict)]
        if not hist and isinstance(f.get("judge"), dict):
            hist = [f["judge"]]
        return any(not v.get("error") for v in hist)

    def _replayed(f: dict) -> bool:
        hist = [r for r in (f.get("replays") or []) if isinstance(r, dict)]
        if not hist and isinstance(f.get("replay"), dict):
            hist = [f["replay"]]
        return any(r.get("outcome") in ("reproduced", "not_reproduced")
                   for r in hist)

    judged = [f for f in rows if _judged(f)]
    replayed = [f for f in rows if _replayed(f)]
    disputed = [f for f in judged if f.get("disputed")]
    failed = [f for f in replayed if f.get("replay_failed")]
    return {
        "findings": total,
        "graded": sum(1 for f in rows if f.get("grade")),
        "cross_read": len(judged),
        "cross_read_disputed": len(disputed),
        "re_verified": len(replayed),
        "re_verification_failed": len(failed),
        "not_cross_read": [str(f.get("id") or "") for f in rows
                           if not _judged(f)],
        "not_re_verified": [str(f.get("id") or "") for f in rows
                            if not _replayed(f)],
    }


def _coverage(session: Session, findings: list | None = None) -> dict:
    """What the run exercised, and what it looked for and did not settle.

    Endpoints touched (method + path + param names, values stripped), probe
    families run, requests per tool - and `open_proof_gaps`, which is the
    only one of the four that is a subtraction rather than a tally. See
    `_open_proof_gaps`: the others say what ran, and a reader of a report
    wants to know what was looked for and came back empty.
    """
    tools: dict[str, int] = {}
    endpoints: set[str] = set()
    probes: set[str] = set()
    with session._lock:  # straggler workers may still append mid-render
        entries = list(session._transcript.values())
    for e in entries:
        if not isinstance(e, dict) or e.get("kind") == "artifacts_digest":
            continue  # the seal is bookkeeping, not exercised surface
        tool = str(e.get("tool") or e.get("kind") or "?")
        # Only exchanges, under a column headed "Requests" and documented
        # in docs/EXPERIMENTS.md as "wire requests per tool - shows where
        # budget went". It counted every RECORD, so `jwt_forge`, which
        # mints a token offline and opens no socket, appeared with a
        # request count - and the table then disagreed with the total
        # printed above it in the other direction. Budget is wire
        # requests, so a tool that spends none contributes none.
        if isinstance(e.get("response"), dict):
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
            "probes": sorted(probes),
            "open_proof_gaps": _open_proof_gaps(entries, findings),
            "verification": _verification_coverage(findings)}


def _open_proof_gaps(entries, findings) -> list[dict]:
    """Probes that ran and produced nothing, named rather than dropped.

    Everything above this function counts what RAN: requests per tool,
    endpoints touched, probes used. None of it answers the question a
    reader of a report actually has, which is what was looked for and not
    found - and the difference between "nothing was looked for" and
    "something was looked for and came back empty" is the whole of a
    coverage claim. The data for it was already here; nobody subtracted.

    A probe run that produced no finding is not the same as a clean
    endpoint. It is a candidate that was opened and never closed, and it
    has exactly three honest ends: a finding, a recorded reason it is
    ruled out, or this list. Dropping it silently is how a report comes to
    say "6 findings" about a run where fourteen other things were tried
    and nobody can say what happened to them.

    Deliberately NOT a judgement about the target. A gap here says the
    evidence does not settle the question, which is a statement about this
    run - the same thing the proof matrix says when it grades `candidate`,
    at the level of the whole engagement rather than one claim.
    """
    from argus.decide import PROBE_CLASS
    from argus.proof import _endpoint_shape

    def _shape(entry_or_url) -> str:
        # `_endpoint_shape` collapses identifiers, so /api/user/1 and
        # /api/user/3 are one endpoint. Without that, a probe that walked
        # three ids and a finding that named one left two "gaps" that were
        # the same endpoint already settled - the measurement inventing
        # work rather than reporting it.
        if isinstance(entry_or_url, dict):
            return _endpoint_shape(entry_or_url)
        return _endpoint_shape({"request": {"url": str(entry_or_url or "")}})

    probed: dict[tuple, list] = {}
    for e in entries:
        if not isinstance(e, dict) or not isinstance(e.get("response"), dict):
            continue
        klass = PROBE_CLASS.get(str(e.get("tool") or ""))
        if not klass:
            continue
        req = e.get("request")
        if not isinstance(req, dict) or not req.get("url"):
            continue
        key = (_shape(e), klass)
        if key[0]:
            probed.setdefault(key, []).append(e)

    # A finding settles every endpoint it CITES, not only the one named in
    # its `url`. One disclosure finding covering `/.env` and `/.git/HEAD`
    # named the first and cited both; counting only the name reported the
    # second as unexamined, which is the opposite of true.
    by_id = {str(e.get("id")): e for e in entries if isinstance(e, dict)}
    settled = set()
    for f in findings or ():
        if not isinstance(f, dict):
            continue
        klass = str(f.get("vuln_class") or "")
        if not klass:
            continue
        shapes = {_shape(str(f.get("url") or ""))}
        for rid in f.get("evidence_ids") or ():
            cited = by_id.get(str(rid))
            if cited is not None:
                shapes.add(_shape(cited))
        settled |= {(sh, klass) for sh in shapes if sh}

    from argus.proof import (negative_settles, anything_got_through, spec_for,
                             status_of, _REFUSED_STATUSES)

    # Whether anything in this run got past a refusal at all. A WAF
    # answering 401/403 to everything makes every probe result say nothing
    # about the target, and the first version of this reported such a run
    # as having no gaps - "nothing was left open" about an engagement
    # where nothing was tested.
    got_through = anything_got_through(entries)

    gaps = []
    for (shape, klass), runs in sorted(probed.items()):
        if (shape, klass) in settled:
            continue            # a finding settled it, either way
        spec = spec_for(klass)
        if spec is not None and negative_settles(spec, runs, got_through):
            continue            # the matrix says this negative IS an answer
        refused = [r for r in runs if status_of(r) in _REFUSED_STATUSES]
        gap = {"endpoint": shape, "vuln_class": klass, "requests": len(runs)}
        if refused and len(refused) == len(runs):
            # Not "we tested and cannot tell" - we never got to test. The
            # two read identically in a list of endpoints and mean
            # opposite things to whoever reads the report next.
            gap["blocked"] = True
            gap["detail"] = (f"every request was refused "
                             f"({sorted({status_of(r) for r in refused})})")
        gaps.append(gap)
    return gaps


def _dur_text(session: Session) -> str:
    """The duration as the report prints it, or "unknown"."""
    value = _duration(session)
    return "unknown" if value is None else f"{value}s"


def _duration(session: Session) -> float | None:
    """Run duration: reuse the value stored in summary.json on first render
    so a re-rendered report shows the run's real length, not time-since."""
    try:
        prev = json.loads((session.dir / "summary.json").read_text(
            encoding="utf-8"))
        if prev.get("duration_s") is not None:
            return float(prev["duration_s"])
    except Exception:
        pass
    # `started` has to be a real stamp. On the forensic reopen path it is
    # initialised to 0.0 and only overwritten when meta.json exists, parses
    # and carries a truthy `started` - and that `except: pass` is deliberate
    # so a damaged session is still reportable. summary.json is written BY
    # this renderer, so on the FIRST report of a session whose meta.json is
    # missing, corrupt, or lacking `started`, both sources were absent and
    # this returned `time.time() - 0.0`: a duration of about 1.76e9 seconds,
    # printed as the run's length. Fifty-six years, in a report whose whole
    # job is to be checkable.
    #
    # 0.0 is not a duration anyone can act on, so say nothing instead of
    # saying something false. `None` here, and both readers below render it
    # as "unknown" rather than printing a number.
    if not session.started or session.started <= 0:
        return None
    return round(time.time() - session.started, 1)


_GRADE_ORDER = {"proven": 0, "candidate": 1, "unproven": 2, "refused": 3}
_GRADE_MEANING = {
    "proven": "the class-specific artifact and its control are on record",
    "candidate": "a real signal; a named check is still missing",
    "unproven": "nothing in the cited evidence meets the requirement",
    "refused": "this system does not prove this class",
    "ungraded": "recorded before grading existed",
}


def _proof_block(f: dict) -> list[str]:
    """What this finding still needs, in the report itself."""
    verdict = f.get("proof") or {}
    if not verdict:
        return []
    out = [f"**Proof grade: {f.get('grade', '?')}**  ", ""]
    # A second model read the evidence. It cannot change the grade - that
    # belongs to the matrix - so the only way its disagreement reaches a
    # reader is by being printed here, next to the grade it disputes.
    # Read the HISTORY, so a later agreement cannot present itself as the
    # whole story over a finding an earlier judge disputed.
    history = [v for v in (f.get("judges") or []) if isinstance(v, dict)]
    if not history and isinstance(f.get("judge"), dict):
        history = [f["judge"]]
    disputes = [v for v in history if not v.get("agrees") and not v.get("error")]
    judged = disputes[0] if disputes else (history[-1] if history else {})
    if judged and len(history) > 1:
        out += [f"> ({len(history)} judges read this evidence: "
                + ", ".join(
                    f"{v.get('judge_model', '?')} "
                    + ("no verdict" if v.get("error") else
                       "agreed" if v.get("agrees") else "disputed")
                    for v in history) + ")", ""]
    if not history:
        # ABSENCE PRINTED. Without this line a finding nobody cross-read is
        # indistinguishable from one this format does not discuss, and the
        # grade above it reads as the whole verification. It is not: the
        # matrix proved the BYTES - a fabricated excerpt fails "the target
        # produced the quoted bytes" and cannot reach `proven` - and nobody
        # checked the READING, which is where a wrong class or an inflated
        # severity lives.
        out += ["> **Cross-verification: not performed** - the proof grade "
                "above is the matrix reading the recorded bytes. No model "
                "from another family has read this evidence, so the class "
                "and severity are this run's own reading of it.", ""]
    if judged:
        model = str(judged.get("judge_model") or "a second model")
        if judged.get("error"):
            out += [f"> **Cross-verification: no verdict** ({model}) - "
                    f"{judged['error']}", ""]
        elif judged.get("agrees"):
            out += [f"> **Cross-verification: agreed** ({model}) - "
                    f"{judged.get('reason', '')}", ""]
        else:
            out += [f"> **DISPUTED by cross-verification** ({model}) - "
                    f"{judged.get('reason', '')}", ""]
            if judged.get("missing"):
                out += ["> Would settle it: "
                        + "; ".join(str(m) for m in judged["missing"]), ""]
        if f.get("class_disputed"):
            out += [f"> The judge reads this evidence as "
                    f"`{f['class_disputed']}`, not `"
                    f"{(f.get('proof') or {}).get('vuln_class', '?')}`.", ""]
        if f.get("severity_claimed"):
            out += [f"> Severity lowered from `{f['severity_claimed']}` on "
                    f"the judge's reading.", ""]
    # THE THIRD LAYER, per finding. `argus replay` writes `replay`/`replays`
    # and a one-way `replay_failed` into findings.json, and no renderer read
    # any of it - so a verification layer's outcome reached no reader at
    # all, which is the same defect as the silence about the judge one layer
    # over, introduced in the hour after fixing that one.
    rhist = [r for r in (f.get("replays") or []) if isinstance(r, dict)]
    if not rhist and isinstance(f.get("replay"), dict):
        rhist = [f["replay"]]
    real = [r for r in rhist
            if r.get("outcome") in ("reproduced", "not_reproduced")]
    if not real:
        why = ""
        incon = [r for r in rhist if r.get("outcome") == "inconclusive"]
        if incon:
            why = f" - {incon[-1].get('reason', '')}"
        out += [f"> **Re-verification: not performed**{why}. The target has "
                "not been asked whether it still does this.", ""]
    else:
        # A failure to reproduce is a one-way door and outranks a later
        # success: a target answering differently on two replays is
        # information about the target, not a correction.
        failed = [r for r in real if r.get("outcome") == "not_reproduced"]
        shown = failed[0] if failed else real[-1]
        if failed:
            out += ["> **DID NOT REPRODUCE** - "
                    f"{shown.get('reason', '')}", ""]
        else:
            out += ["> **Re-verified against the target: reproduced** - "
                    f"{shown.get('reason', '')}", ""]
            # AN EARLIER ATTEMPT THAT COULD NOT ASK IS PART OF THE ANSWER.
            # Measured on a live session: a finding whose first replay was
            # inconclusive - the recorded request carried a credential and
            # the transcript keeps only its digest - and which reproduced
            # once the credential was supplied. The report showed only
            # "reproduced", so a reader could not tell it apart from one
            # that reproduced unauthenticated.
            #
            # That difference is material. For whoever triages this, "it
            # still works, with a valid session" is a different finding from
            # "it still works for anyone", and the history already held the
            # distinction - a commit message of mine claimed a reader could
            # see it, which was true of findings.json and not of the report.
            earlier = [r for r in rhist
                       if r.get("outcome") == "inconclusive"]
            if earlier:
                out += ["> An earlier re-verification could not reach the "
                        f"target: {earlier[0].get('reason', '')}", ""]
    if verdict.get("requirement"):
        out += [f"_Requirement for {verdict.get('vuln_class', '')}:_ "
                f"{verdict['requirement']}", ""]
    for check in verdict.get("checks") or []:
        mark = "x" if check.get("ok") else " "
        detail = f" - {check['detail']}" if check.get("detail") else ""
        out.append(f"- [{mark}] {check.get('check', '')}{detail}")
    out.append("")
    return out


def _target_of(session, meta: dict | None) -> str:
    """What was tested, from the record, with the derivation last.

    Order matters: `meta.json` is written by the run and is the only
    statement of the target that the run itself made. The directory parse
    stays as a last resort because a very old session may predate the key,
    and printing nothing would be worse than printing the convention - but
    it is marked, so a reader can tell a recorded target from a guess.
    """
    if isinstance(meta, dict):
        recorded = str(meta.get("target") or "").strip()
        if recorded:
            return recorded
    for attr in ("target",):
        value = str(getattr(session, attr, "") or "").strip()
        if value:
            return value
    derived = session.dir.name.split("-", 2)[-1]
    return f"{derived} (from the directory name; meta.json names no target)"


def _record_state(session) -> list[str]:
    """Whether this report's own record still verifies, stated in the report.

    MEASURED. A hand-edited severity reaches the deliverable as fact: a
    finding edited from medium to critical in findings.json renders as
    "Severity: Critical", raises the critical count in the tally by one,
    and sits beside its unchanged "proof: candidate" with nothing saying
    the file was edited after sealing.

    The seal catches it - `argus verify` reports the file as edited - and
    the render warns on stderr. Neither reaches the document. A report read
    away from the terminal that produced it could not say whether its own
    record verifies, which is the same shape as a diff whose caveat went to
    stderr while its conclusion went to stdout.

    `findings_bad` does not catch this and should not be asked to: it
    validates EVIDENCE - that the cited ids exist and the excerpt is
    verbatim - and an edited severity leaves the evidence intact. Severity
    is partly a judgement, so editing it is not necessarily tampering. What
    is not optional is saying that the file changed.

    Stated in BOTH directions, because a line that appears only on failure
    teaches a reader that its absence means verified.
    """
    from ..session import verify_transcript

    try:
        v = verify_transcript(session.dir)
    except Exception:                                         # noqa: BLE001
        return ["_The verification state of this record could not be read._"]

    problems = []
    if not v.get("chained"):
        problems.append("the transcript hash chain does not verify")
    if v.get("tail_truncated"):
        problems.append("the transcript tail is truncated")
    if v.get("bad_lines"):
        problems.append(f"{len(v['bad_lines'])} transcript line(s) unparseable")
    for key, text in (("artifact_mismatch", "edited since the run was sealed"),
                      ("unsealed_additions", "added after the run was sealed "
                                             "and covered by no digest")):
        named = v.get(key)
        if named:
            problems.append(f"{', '.join(sorted(named))} {text}")
    if v.get("resealed_over_mismatch"):
        problems.append("this record was re-sealed over a mismatch, so the "
                        "current digests do not attest the original run")

    if not problems:
        return [f"_Record verified: {v.get('entries', 0)} chained transcript "
                f"entries, {v.get('findings_checked', 0)} findings "
                "re-validated against them, artifacts matching their "
                "digests._"]
    return ["> **This record does not verify.** "
            + "; ".join(problems)
            + ". Everything above is reported from it anyway, so read it as "
              "a claim about the file rather than about the target - "
              "`argus verify` gives the detail."]


def _grade_line(findings: list | None) -> str:
    """How many findings are graded, stated rather than assumed.

    `ungraded` is a real bucket in `_GRADE_MEANING` - "recorded before
    grading existed" - so a session resumed from an older run, or a
    findings.json written by a previous version, holds rows the matrix never
    graded. Saying "every finding is graded" over such a row tells the
    reader the opposite of the table four lines below it.
    """
    rows = [f for f in (findings or []) if isinstance(f, dict)]
    graded = [f for f in rows if str(f.get("grade") or "").strip()]
    missing = len(rows) - len(graded)
    if not rows or not missing:
        return ("Every finding is graded against the proof requirement for "
                "its class")
    carries = "carries" if missing == 1 else "carry"
    return (f"{len(graded)} of {len(rows)} findings are graded against the "
            f"proof requirement for their class, and {missing} {carries} no "
            "grade at all - counted as `ungraded` above, never as a verdict "
            "about its evidence" if missing == 1 else
            f"{len(graded)} of {len(rows)} findings are graded against the "
            f"proof requirement for their class, and {missing} {carries} no "
            "grade at all - counted as `ungraded` above, never as a verdict "
            "about their evidence")


def render_report(session: Session, cfg: Config, summary: str = "",
                  extra: dict | None = None) -> Path:
    extra = dict(extra or {})
    # a re-render (`argus report`) must not drop run metrics the original
    # render recorded (mode, llm_calls, llm_tokens, agents) - they land as
    # top-level summary keys, so carry forward every key the canonical
    # schema does not own, under any freshly supplied ones
    # Every key this render RECOMPUTES. A key missing from this set is carried
    # forward from the previous summary.json and then overwritten - or not,
    # depending on merge order - and `grades` was missing, so a re-render after
    # the findings changed reported the old grade counts.
    _BASE = {"session", "findings", "counts", "grades", "requests",
             "duration_s", "time_to_first_finding_s", "coverage",
             "transcript_chain_head", "agent_summary"}
    _prev = session.dir / "summary.json"
    if _prev.exists():
        try:
            _old = json.loads(_prev.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            _old = None
        if isinstance(_old, dict):
            extra = {**{k: v for k, v in _old.items() if k not in _BASE},
                     **extra}
    findings = sorted(sanitized_findings(session.findings),
                      key=lambda f: (_GRADE_ORDER.get(f.get("grade", ""), 9),
                                     _SEV_ORDER.get(f["severity"], 99)))
    # after `findings`, because an open gap is defined by its ABSENCE from
    # them: a probe that ran and settled nothing. Computing coverage first
    # would have to guess at that, and guessing is how the tally stayed a
    # tally.
    coverage = _coverage(session, findings)
    grades: dict[str, int] = {}
    for f in findings:
        grades[f.get("grade") or "ungraded"] = \
            grades.get(f.get("grade") or "ungraded", 0) + 1
    counts: dict[str, int] = {}
    for f in findings:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1
    first_ts = min((f.get("ts", 0) for f in findings), default=0)
    ttf = round(first_ts - session.started, 1) \
        if first_ts and session.started else None

    meta = {}
    meta_read = False
    mp = session.dir / "meta.json"
    if mp.exists():
        try:
            meta = json.loads(mp.read_text(encoding="utf-8"))
            meta_read = True
        except Exception:
            meta = {}
        if not isinstance(meta, dict):
            meta, meta_read = {}, False
    lines = [
        f"# Penetration Test Report - {session.id}",
        "",
        # THE RECORD, NOT THE FILENAME. This read
        # `session.dir.name.split('-', 2)[-1]`, so the Target line - the
        # report's claim about WHAT WAS TESTED, which in an
        # authorised-testing system is the authorisation boundary - was
        # parsed out of the directory name. It was right only by
        # coincidence of the naming convention, and measured across every
        # sealed session in this repository, 0 of 5 rendered correctly:
        #
        #   directory          meta.json                   derived
        #   sample-session     http://127.0.0.1:43673      "session"
        #   argus-lab          http://192.168.223.221:8777 "lab"
        #   argus-lab-team     http://192.168.223.221:8777 "team"
        #   dvwa               http://192.168.223.221:8081 "dvwa"
        #   bwapp              http://192.168.223.221:8080 "bwapp"
        #
        # The two that look right drop the scheme and the port, and a
        # session directory that is renamed, copied or moved names
        # something that was never tested. `meta.json` holds the real
        # target in all five, which is why `argus replay` reads it there.
        #
        # The directory name is kept in parentheses: it identifies the
        # artifact, which is a different question from what was tested.
        f"- **Target:** `{_target_of(session, meta)}` ({session.dir.name})",
        # `started` is 0.0 on a reopen whose meta.json is missing, corrupt
        # or lacks the stamp, and this line printed `1970-01-01 00:00:00`
        # for it - the same defect as the duration below, one line up.
        f"- **Date:** "
        f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(session.started))}"
        if session.started and session.started > 0 else
        "- **Date:** unknown (this session's meta.json carries no start time)",
        f"- **Duration:** {_dur_text(session)}",
        f"- **Agent model:** {cfg.model}",
        # the build that produced the session - falls back to this
        # renderer's on old artifacts without a stamp
        f"- **Argus version:** {meta.get('argus_version') or __version__}",
        f"- **Requests sent:** {session.requests_sent}",
        "",
        # The run's terminal error, above everything else, because every
        # number below it describes a run that may not have happened. A
        # session that died on its first API call rendered a report
        # indistinguishable from a clean one with no findings: 0 requests,
        # 0 findings, an empty findings table. The reader has to be told
        # before reading the table, not after.
        *( [f"> **RUN DID NOT COMPLETE.** `{extra.get('error')}`", "",
            "> Every figure below describes an incomplete run. Findings may",
            "> be missing because the run stopped, not because the target",
            "> is clean.", ""]
           if extra.get("error") else []),
        "## Executive summary",
        "",
        summary or "_No agent summary was recorded._",
        "",
    ]
    if meta.get("operator"):
        lines.insert(6, f"- **Operator:** {meta['operator']}")
    _cost = extra.get("llm_cost") if isinstance(
        extra.get("llm_cost"), dict) else {}
    if _cost:
        _usd = _cost.get("usd")
        if _usd is None:
            # naming the reason beats printing 0.00, which reads as free
            _line = (f"- **Model cost:** not priced - "
                     f"{_cost.get('basis', 'no price available')}")
        else:
            _tok = extra.get("llm_tokens") or {}
            # `unpriced` is read HERE too, not only on the None branch. A
            # team total is the sum of the agents that could be priced, and
            # this branch printed it as the run's cost while ignoring the
            # list naming the ones that could not - so a reader saw a
            # definite figure with nothing saying it was partial.
            #
            # The sweep refused this as a state no run can reach, which was
            # true of the live tree at the time: it needed an agent whose
            # MODEL is absent from the table, and the spawn path cannot
            # produce one. Making a crashed worker unpriced earlier in this
            # stretch - because pricing its missing tokens at $0.00 was
            # worse - is what made it reachable, so the refusal was correct
            # and is now out of date. A fix that creates the precondition
            # for another finding has to close it too.
            _unpriced = _cost.get("unpriced") or []
            _partial = (f" - PARTIAL: {len(_unpriced)} agent(s) could not "
                        f"be priced ({', '.join(str(u) for u in _unpriced)})"
                        if isinstance(_unpriced, list) and _unpriced else "")
            _line = (
                f"- **Model cost:** ${_usd:.4f} USD "
                f"({_tok.get('in', 0)} in / {_tok.get('out', 0)} out / "
                f"{_tok.get('cache_read', 0)} cache-read tokens, "
                f"model table v{_cost.get('table_version', 0)}){_partial}")
        lines.insert(7 if meta.get("operator") else 6, _line)
    lines += [
        "| Severity | Count |",
        "|---|---|",
    ]
    for sev in SEVERITIES:
        if counts.get(sev):
            lines.append(f"| {_SEV_LABEL[sev]} | {counts[sev]} |")
    if not findings:
        lines.append("| - | 0 |")
    if grades:
        lines += ["", "| Proof grade | Count | Meaning |", "|---|---|---|"]
        for g in ("proven", "candidate", "unproven", "refused", "ungraded"):
            if grades.get(g):   # "ungraded" is counted above, not skipped
                lines.append(f"| **{g}** | {grades[g]} | {_GRADE_MEANING[g]} |")

    # WHAT THE GRADE IS NOT. A number nobody can see is not a measurement,
    # and this is the one a reader most needs: measured across this
    # repository's own four sealed sessions, all 16 findings were graded,
    # all 16 cited evidence, and ZERO had been read by a second model or
    # re-verified against the target. Both layers existed, were tested, and
    # had never touched a real finding - and no report said so, so `proven`
    # read as the whole of the verification when it is one third of it.
    vc = _verification_coverage(findings)
    if vc["findings"]:
        lines += ["", "| Verification | Findings | What it answers |",
                  "|---|---|---|",
                  f"| graded by the matrix | {vc['graded']}/{vc['findings']} "
                  "| did the target produce the quoted bytes |",
                  f"| read by a second model | {vc['cross_read']}/"
                  f"{vc['findings']} | do those bytes demonstrate the class "
                  "claimed |",
                  f"| re-verified against the target | {vc['re_verified']}/"
                  f"{vc['findings']} | does the target still do it |"]
        if vc["cross_read_disputed"]:
            lines.append(f"| disputed by a second model | "
                         f"{vc['cross_read_disputed']}/{vc['findings']} | "
                         "printed next to the grade it disputes |")
        if vc["re_verification_failed"]:
            lines.append(f"| did not reproduce | "
                         f"{vc['re_verification_failed']}/{vc['findings']} | "
                         "not a retraction - see the finding |")
        gaps = []
        if not vc["cross_read"]:
            gaps.append("No finding here has been read by a model from "
                        "another family. `argus judge <session>` does that; "
                        "it can dispute or lower, never promote.")
        if not vc["re_verified"]:
            gaps.append("No finding here has been re-verified against the "
                        "target. `argus replay <session>` does that; an "
                        "authenticated target needs the credential supplied "
                        "again with `--header`.")
        if gaps:
            lines += [""] + [f"> {g}" for g in gaps]
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
        # Every one of these falls back to a definite NEGATIVE - "(target
        # only)", "none", "no", "no", "all" - and `argus report` needs only
        # transcript.jsonl, so it renders happily with meta.json absent.
        # Measured on a real demo session: with meta.json deleted this block
        # is identical to the one rendered with it present, except for the
        # budgets degrading to `?`. A run constrained by a scope list, an
        # exclusion and a tool subset re-renders as unrestricted, and
        # "TLS verify: no" / "Tool surface: all" are claims about how the
        # engagement was CONDUCTED - wrong in the direction of a broader,
        # less careful test than was run, or for scope a narrower one than
        # was authorised. The only existing signal was a stderr line at
        # render time; the re-render then re-seals and `argus verify`
        # prints OK and exits 0.
        #
        # So the absence is stated where the claims would have gone. An
        # empty-but-present meta.json still reads as "(target only)",
        # because that file recording no scope IS the claim that none was
        # set.
        *( ["- **Engagement constraints are not on record for this "
            "session:** `meta.json` is missing or unreadable, so the scope "
            "list, exclusions, budgets, proxy, TLS and tool surface below "
            "cannot be stated. They are NOT defaults - they are unknown."]
           if not meta_read else []),
        f"- **Scope hosts:** {_join_list(meta.get('scope'), '(target only)') if meta_read else 'not recorded'}",
        f"- **Excluded paths:** {_join_list(meta.get('exclude_paths'), 'none') if meta_read else 'not recorded'}",
        f"- **Budgets:** {meta.get('max_turns', '?')} turns, "
        f"{meta.get('max_requests', '?')} requests, {meta.get('rate_rps', '?')} rps",
        f"- **Proxy:** {('yes' if meta.get('proxy') else 'no') if meta_read else 'not recorded'} · "
        f"**TLS verify:** {('yes' if meta.get('tls_verify') else 'no') if meta_read else 'not recorded'}",
        f"- **Tool surface:** {_tool_surface(meta) if meta_read else 'not recorded'}",
        "",
    ]

    lines += ["", "## Findings", ""]
    for f in findings:
        lines += [
            f"### {f['id']} - {f['title']}",
            "",
            f"- **Severity:** {_SEV_LABEL.get(f['severity'], f['severity'])}",
            *([f"- **CVSS:** `{f['cvss']}`"] if f.get("cvss") else []),
            f"- **Category:** {f['category']}"
            + (f" · **proof: {f['grade']}**" if f.get("grade") else ""),
            *([f"- **CWE:** `{f.get('cwe') or _cwe_of(f['category'])}`"]
              if f.get("cwe") or _cwe_of(f.get("category")) else []),
            *([f"- **OWASP:** {f.get('owasp') or _owasp_of(f.get('cwe') or _cwe_of(f['category']))}"]
              if f.get("owasp") or _owasp_of(f.get("cwe") or _cwe_of(f.get("category"))) else []),
            f"- **Endpoint:** {_code(f['url'])}",
            f"- **Evidence:** {', '.join(f['evidence_ids'])}",
            "",
            "**Description**  ",
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
            *_proof_block(f),
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
                # `_h` because this is a raw HTML element THIS renderer
                # opens, and report.md cannot be rendered with raw HTML
                # disabled - its own `<details>` blocks and the notes
                # appendix depend on it, so any viewer that shows these
                # collapsible sections also parses whatever the target put
                # in the URL. The target chooses those bytes: the crawler
                # follows its hrefs and the probes build URLs from its
                # parameter names. Driven end to end, a loopback target
                # serving `<a href='/p?x="><script>alert(document.domain)'
                # ...>` produced a live `<script>` tag inside this
                # `<summary>`. report.html escapes the same value with
                # `_esc`; this file had no equivalent.
                f"<details><summary>Transcript {_h(rid)}: "
                f"{_h(req.get('method'))} {_h(req.get('url'))} -> "
                f"{_h(resp.get('status'))}</summary>",
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

    # Everything above says what RAN. This says what was looked for and not
    # settled, which is the half of a coverage claim a reader cannot get
    # from a tally. A report that lists six findings and says nothing about
    # the probes that came back empty is not describing its own coverage;
    # it is describing its successes.
    gaps = coverage.get("open_proof_gaps") or []
    lines += ["", f"### Open proof gaps ({len(gaps)})", ""]
    if not gaps:
        lines += ["Every probe that ran either produced a finding or hit a "
                  "class whose negative result settles it. Nothing was left "
                  "open.", ""]
    else:
        lines += ["These were probed and neither proved nor ruled out. They "
                  "are **not** clean results: a probe that found nothing is "
                  "only evidence of absence for a class whose negative is "
                  "conclusive, and the matrix names those explicitly "
                  "(`ruled_out_by`). Everything else that came back empty "
                  "is listed here rather than dropped.", "",
                  "| Endpoint | Class | Requests | Why it is not an answer |",
                  "|---|---|---|---|"]
        from argus.proof import spec_for
        blocked = [g for g in gaps if g.get("blocked")]
        if blocked:
            lines[-4:-4] = []
            lines += ["", f"**{len(blocked)} of these were never tested.** "
                      "Every request to them was refused, so the result says "
                      "nothing about the target - only about our access. A "
                      "run refused everywhere produces no findings and, "
                      "before this was separated out, no gaps either: a "
                      "report reading *nothing was left open* about an "
                      "engagement where nothing was opened.", ""]
        for g in gaps[:60]:
            spec = spec_for(str(g.get("vuln_class") or ""))
            why = (g.get("detail", "never tested - every request refused")
                   if g.get("blocked")
                   else "the matrix records no negative that settles this class"
                   if spec is None or not spec.ruled_out_by
                   else f"settled only by: {spec.ruled_out_by}")
            lines.append(f"| {_code(str(g.get('endpoint')))} "
                         f"| `{g.get('vuln_class')}` | {g.get('requests')} "
                         f"| {why} |")
        if len(gaps) > 60:
            lines.append(f"| _...and {len(gaps) - 60} more_ | | | "
                         "_see summary.json_ |")
        lines.append("")

    lines += [
        "## Methodology",
        "",
        "Autonomous agent run: recon (fingerprint, crawl, js_recon) -> input",
        "mapping -> hypothesis-driven probes (matched true/false pairs,",
        "baseline-diffed) -> verification -> evidence-gated findings.",
        "The complete request/response transcript is in `transcript.jsonl`,",
        f"({session._seq} entries). Working notes are in `notes.md`.",
        "",
        # THE COUNT, NOT THE UNIVERSAL. Measured by planting a row with no
        # `grade` key in the sample session and re-rendering: the report
        # printed, four lines apart,
        #
        #   | **ungraded** | 1 | recorded before grading existed |
        #   Every finding is graded against the proof requirement for its class
        #
        # A deliverable stating a universal claim and, in the same document,
        # a count that contradicts it. The two neighbouring claims about
        # CITATION are deliberately left universal, because those ARE
        # enforced - `add_finding` refuses an excerpt that is not a verbatim
        # substring of a cited response, and `findings_bad` re-validates
        # every one on re-read. Grading is the one that can be absent.
        #
        # A number cannot quietly become false, which is the property this
        # whole system is built to have.
        _grade_line(findings),
        "(`argus proof <class>`): **proven** means the class-specific artifact",
        "and its control are both on record; **candidate** means a real signal",
        "with a named check still missing. A candidate is reported because it",
        "is worth re-testing, not because it is a result.",
        "",
        "_All findings cite verbatim response excerpts verified against the",
        "recorded transcript at write time._",
        "",
        *_record_state(session),
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

    from ..session import _atomic_write
    path = session.dir / "report.md"
    _atomic_write(path, "\n".join(lines))
    summary_json = {
        "session": session.id,
        "argus_version": __version__,
        "findings": findings,
        "counts": counts,
        "grades": grades,
        # Persisted so `argus report` can put it back. A re-render used to
        # replace the agent's summary with "_No agent summary was recorded._"
        # and then re-seal, so the delivered artifact was worse than the
        # original and digest-valid.
        "agent_summary": summary or "",
        "requests": session.requests_sent,
        # null, not a number: a reader of summary.json must be able to tell
        # "the run took no measurable time" from "nothing recorded when it
        # began"
        "duration_s": _duration(session),
        "time_to_first_finding_s": ttf,
        "coverage": coverage,
        # anchoring the last chain link makes tail truncation detectable:
        # verify compares the transcript's final link against this value
        "transcript_chain_head": getattr(session, "_last_chain", ""),
        **extra,
    }
    _atomic_write(session.dir / "summary.json",
                  json.dumps(summary_json, indent=2, ensure_ascii=False))
    try:
        from .html import render_html
        render_html(session, cfg, summary, extra)
    except Exception:
        pass  # html is a convenience; the markdown report is canonical
    try:
        # The bug-bounty shape: one section per finding, with the PoC. Same
        # convenience contract as the html one above - a failure here must
        # not cost the canonical markdown report.
        from .hackerone import render_hackerone
        render_hackerone(session, cfg, summary, extra)
    except Exception:
        pass
    try:
        from .sarif import render_sarif
        render_sarif(session, extra)
    except Exception:
        pass  # sarif is CI-integrations glue; never block the report
    return path
