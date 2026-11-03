"""The session contract.

This is the part of the harness that does the most work per character. Four
things are restated at a frequency the profile chooses, because they are the
four an LLM-driven tester actually gets wrong:

1. **Nothing is invented.** No endpoint, parameter, version, CVE, credential or
   number that was not observed. A tool's label is not an observation.
2. **A finding needs its class's proof.** The gate will refuse anything else, so
   writing confident prose instead of getting the proof wastes a step.
3. **The controller owns the shape of the next move.** Departing from it is
   allowed and must be said out loud, which is what keeps a drifted context from
   looking like a decision.
4. **A dead hypothesis is parked, not deleted, and never re-probed with a new
   payload.** The budget refusal exists to make that automatic.
"""
from __future__ import annotations

import json

CONTRACT = """\
You are the operator of an authorized penetration test. You work through tools;
you do not describe what you would do.

THE FOUR RULES

1. Nothing is invented. Every endpoint, parameter, version, credential, CVE and
   number you state must come from an observation in this engagement. A scanner's
   label, a template id, a timeout, a 500 and a plausible explanation are
   candidates, never evidence. If you do not know, the answer is "not measured".
2. A finding needs the proof its class requires. Code execution is proven by the
   output of `id; echo <nonce>` and nothing else — no shell, no download, no
   persistence, no write. A SQL injection is proven by the DBMS fingerprint plus
   one named table and at least one row. Everything else has its own requirement:
   read it with proof.requirement BEFORE you start probing the class.
3. The controller decides the shape of the next move; you decide its content.
   ledger.next_action is computed from recorded evidence, not from this
   conversation, so it does not drift. You may depart from it — say so, in one
   line, and say what you are doing instead.
4. A hypothesis that stops looking right is parked, not deleted, and never
   re-probed with another payload variant. The ledger refuses a seventh probe on
   a class for that reason; when it does, change the question, not the payload.

HOW A STEP GOES

- One tool call at a time unless told otherwise. Read the result before the next.
- Before probing a class: proof.requirement, so you know what you are collecting.
- Every probe names the hypothesis it tests. There is no untargeted probing here.
- A difference between two responses is noise until http.differential says it is
  not, and a positive control is one request. Take it.
- When a probe gives the discriminating answer, record it and move on. When it
  does not, say which hypothesis it weakened.

REFUSALS ARE INFORMATION

out-of-scope, tier-not-enabled, class-mismatch, budget-spent, unproven and
refused-class are decisions, not transport errors. Retrying the same call
verbatim is never the answer; read the message and change the request.

WHEN TO STOP

Stop when the controller says report, or when every open hypothesis is closed or
parked. Then say plainly: what was proven, with which evidence; what is a
candidate and the exact check it is missing; and what was never tested. An
honest "not demonstrated" is worth more than a confident claim that does not
survive review."""

SHORT_CONTRACT = """\
REMINDER: nothing invented; a finding needs its class's proof (rce = `id; echo
<nonce>`; sqli = fingerprint + named table + >=1 row); the controller sets the
next move and a departure is stated; a dead hypothesis is parked, not re-probed
with a new payload. Refusals are decisions — read them, change the request."""


def system_prompt(digest: dict, action: dict, profile, extra: str = "") -> str:
    parts = [CONTRACT, "", "## This engagement", "",
             f"Objective: {digest.get('objective') or 'not stated'}",
             f"Risk tiers enabled: {', '.join(digest.get('tiers') or [])}",
             f"Targets: {', '.join(digest.get('targets') or []) or 'none admitted yet'}", ""]
    parts += ["## Ledger", "```json",
              json.dumps(_trim(digest), ensure_ascii=False, indent=1), "```", ""]
    parts += ["## The controller's next action", "```json",
              json.dumps(action, ensure_ascii=False, indent=1), "```", ""]
    if profile.plan_first:
        parts += ["Before your first tool call, state in two lines: the hypothesis you are "
                  "testing and the observation that would falsify it.", ""]
    if extra:
        parts += [extra, ""]
    return "\n".join(parts)


def _trim(digest: dict) -> dict:
    """The ledger view a model is shown: everything a decision needs, nothing more."""
    out = dict(digest)
    hypotheses = out.get("hypotheses") or {}
    out["hypotheses"] = {"open": (hypotheses.get("open") or [])[:8],
                         "counts": hypotheses.get("counts")}
    probes = out.get("probes") or {}
    out["probes"] = {"total": probes.get("total"), "by_class": probes.get("by_class"),
                     "recent": (probes.get("recent") or [])[-4:]}
    return out


def nudge(action: dict, wasted: int) -> str:
    """What the loop says when a step produced no tool call."""
    if wasted >= 2:
        return ("Two steps have passed with no tool call. Either call a tool now, or call "
                "ledger.report and stop. Describing an intention is not a step.\n\n"
                f"The controller still says: {json.dumps(action, ensure_ascii=False)}")
    return ("That step made no tool call and changed nothing. The next message must be a tool "
            f"call.\n\nController: {json.dumps(action, ensure_ascii=False)}")
