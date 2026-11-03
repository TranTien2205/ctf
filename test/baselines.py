#!/usr/bin/env python3
"""The offline half of the measurement: what the ledger gate does to a fixed
sequence of actions.

`ARCHITECTURE.md` section 6 lists five research claims, each with the baseline
run it needs. Three of the five need live models. Two do not, and this script is
those two:

    an admission gate reduces unsupported findings
        measured as: the share of recorded findings that would not survive review
        baseline:    the same driver with the proof requirement switched off

    an external controller reduces wasted probes
        measured as: probes per proven finding; the repeat-payload rate per class
        baseline:    the same driver with the controller ignored

## What this measures, and what it does not

The subject under test is **not a model**. No key is configured here, and a model
run is not reproducible anyway, so a measurement built on one would not be a
baseline. What runs instead is a **scripted driver**: a fixed, deterministic
sequence of broker calls that stands in for a model. That makes the honest
reading of every number below:

    these runs measure what the GATE does to a given sequence of actions,
    not what a model would do.

The gate's effect on this driver set is a property of the gate. The driver set's
resemblance to a model's behaviour is an assumption, not a result. A number that
overclaims is worse than no number, so the output says this too, every time.

Two further boundaries, because they change what the numbers mean:

* `--no-gate` switches off the grading on the **finding write path** and nothing
  on the probe path. Scope, tier and probe-budget refusals stay on in both
  configurations, so the only variable is what happens when a finding is written.
  `record_ungated` lists the checks that go with the grading.
* Under the gate, "unsupported findings admitted" is zero **by construction** —
  `hooks.record_finding` refuses `unproven` outright, so the number is unreachable
  rather than measured. What the gated column measures is therefore the *size of
  what the gate catches for these sequences*, not whether the gate works. The
  `--no-gate` column is where the claim's quantity actually comes from.

## The drivers

    disciplined   consults `ledger.next_action`, reads the proof requirement
                  before probing a class, takes the control, records only what
                  grades `proven`, and parks what stays `supported`.
    optimistic    the failure mode this system was built against. Probes until
                  it sees any signal, then claims a finding immediately: a 500 on
                  a quote becomes SQL injection, a reflected payload becomes XSS,
                  a timing difference becomes command injection, a 200 on `id=2`
                  becomes broken access control. It never asks the controller.
    repetitive    fixates. One class, eight payload variants, the same question
                  every time, until a budget refusal stops it.

Run it:

    python3 test/baselines.py
    python3 test/baselines.py --json
    python3 test/baselines.py --driver optimistic --config no-gate --keep
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "test" / "fixtures"))

import vulnapp                                                        # noqa: E402
from argus import config                                              # noqa: E402
from argus.broker.serve import merge                                  # noqa: E402
from argus.config import Paths                                        # noqa: E402
from argus.ledger import hooks                                        # noqa: E402
from argus.ledger import proof as proof_mod                           # noqa: E402
from argus.ledger.lock import engagement_lock                         # noqa: E402
from argus.ledger.state import State                                  # noqa: E402
from argus.orchestrator import metrics                                # noqa: E402

SERVERS = ["http", "recon", "proof", "ledger", "knowledge"]
CONFIGS = ("gate", "no-gate")
# Every engagement this script creates is named with this prefix, and the ungated
# write path refuses anything else. The prefix is the enforcement, not a habit:
# see record_ungated.
BASELINE_PREFIX = "baseline-"

# The fixture is owned by this repository and binds loopback only. The note is
# what `open_engagement` requires before it will enable the intrusive tier, and
# it is required precisely so that nobody can enable that tier by asserting it is
# fine: proving code execution is a decision an engagement makes in advance.
AUTHORISATION = ("authorised by whoever runs this script, over the duration of the run, against "
                 "test/fixtures/vulnapp.py on 127.0.0.1 only — a fixture this repository owns and "
                 "this process starts and stops itself")


# --- the ungated write path --------------------------------------------------

def record_ungated(engagement: str, hypothesis_id: str, vuln_class: str, title: str,
                   evidence_ids: list[str], impact: str = "", target: str = "") -> dict:
    """Write a finding into the ledger with no grading at all.

    This is the `--no-gate` baseline, and it is deliberately written *here*, in
    the measurement, against `State.add_finding` — the data layer, which enforces
    structure and not policy. The alternative was a flag on
    `hooks.record_finding`, and it was rejected: a test that can switch off a
    safety control is a test that will one day switch it off in production. The
    bypass has to live in the thing doing the measuring, where it is visible, and
    the real write path has to have no way through it.

    It refuses any engagement whose name this script did not choose. A bypass
    that can be imported and pointed at a live engagement is a bypass that one
    day will be, so the one line of enforcement is here rather than a sentence
    asking the caller not to.

    What this skips, exactly: `proof_mod.verify`, the three refusals that depend
    on it (`unproven`, `refused-class`, and the `confirmed` / `candidate` split),
    and two checks that sit beside it in `hooks.record_finding` — that every
    evidence id exists, and that the hypothesis does. So the class recorded here
    is the one the driver named rather than the one the hypothesis holds, which
    is correct for a baseline: the point is to record the claim as made. It does
    not skip the lock, the atomic write or the event log, because a baseline that
    also loses writes measures nothing.

    One asymmetry worth naming: `hooks.record_finding` closes the hypothesis when
    the evidence is proven, and this does not, so a hypothesis stays open here
    after a finding is written against it. None of the drivers below probe a class
    again after claiming it, so it does not move any number in this run — but a
    driver that did would get more probes through in this column than in the
    gated one, and the comparison would be wrong.
    """
    if not engagement.startswith(BASELINE_PREFIX):
        raise ValueError(
            f"record_ungated refuses {engagement!r}: the ungated write path exists only for the "
            f"engagements this script creates ({BASELINE_PREFIX}*). Everything else writes "
            f"through argus.ledger.hooks.record_finding, which grades the evidence first.")
    with engagement_lock(Paths(engagement).dir):
        state = State.load(engagement)
        finding = state.add_finding({
            "vuln_class": vuln_class,
            "title": title,
            "status": "recorded",          # no grade exists here: that is the point
            "severity": "unknown",
            "target": target,
            "entry_point": {},
            "hypothesis_id": hypothesis_id,
            "evidence_ids": list(evidence_ids),
            "proof": None,
            "reproduce": [],
            "impact": impact,
            "remediation": "",
            "recorded_by": "baseline-no-gate",
            "verified_by": [],
        })
        state.save()
        state.event("finding.recorded", {"finding": finding["id"], "class": vuln_class,
                                         "grade": None}, actor="baseline-no-gate")
    return {"ok": True, "finding": finding["id"], "summary": f"{finding['id']} recorded ungraded"}


# --- one driver run ----------------------------------------------------------

def _evidence_of(result: dict) -> list[str]:
    """The evidence id one call produced, or nothing when the call did not produce one.

    A driver that writes `result["evidence_id"]` dies on a KeyError the first time
    a tool is refused or errors, and a measurement that dies halfway through run
    three reports nothing at all. An empty list is the honest input to a claim
    instead: the gated path then refuses it as `unproven`, which is what a claim
    with no observation behind it deserves, and the ungated path records it as the
    unsupported finding it is.
    """
    identifier = result.get("evidence_id")
    return [identifier] if identifier else []


def _json_field(text: str | None, field: str) -> str | None:
    """Read one field out of a JSON response body, or give up quietly.

    It gives up rather than guessing: a driver that invents the owner of a record
    it could not read has invented the finding.
    """
    try:
        value = json.loads(text or "")[field]
    except (ValueError, TypeError, KeyError, IndexError):
        return None
    return str(value) if value is not None else None


class Session:
    """One driver, one configuration, one engagement, and the tally of what it did.

    Everything a driver does goes through `call`, so the probe count, the refusals
    and the order of actions are recorded here rather than inferred afterwards.
    The ledger's own numbers are read back separately in `measure`; this object is
    only for the things the ledger does not record — what the driver asked the
    controller, and whether it did what it was told.
    """

    def __init__(self, server, driver: str, engagement: str, base: str, gated: bool,
                 verbose: bool):
        self.server = server
        self.driver = driver
        self.engagement = engagement
        self.base = base
        self.gated = gated
        self.verbose = verbose
        self.calls = 0
        self.refusals: Counter = Counter()
        self.actions: list[dict] = []
        self.departures: list[dict] = []
        self.controller_consulted = 0
        self.controller_aligned = 0
        self.claims: list[dict] = []
        self.stopped_by: str | None = None

    # --- plumbing ------------------------------------------------------------

    def call(self, name: str, **arguments) -> dict:
        self.calls += 1
        result = self.server.call(name, arguments, engagement=self.engagement,
                                  actor="baseline-driver")
        if not result.get("ok", True):
            self.refusals[str(result.get("error") or "unknown")] += 1
        self.actions.append({"tool": name, "ok": bool(result.get("ok", True)),
                             "error": result.get("error"),
                             "summary": str(result.get("summary")
                                            or result.get("message") or "")[:120]})
        if self.verbose:
            mark = "ok " if result.get("ok", True) else "REF"
            print(f"      [{mark}] {name:24} {self.actions[-1]['summary'][:88]}")
        return result

    def consult(self) -> dict:
        """Ask the controller what happens next. Recorded whether or not it is obeyed."""
        self.controller_consulted += 1
        result = self.call("ledger.next_action")
        return (result.get("data") or {})

    def obeyed(self, action: dict, did: str) -> None:
        if (action.get("action") or "") == did:
            self.controller_aligned += 1

    def depart(self, action: dict, doing: str, reason: str | None) -> None:
        """A departure from the controller. The reason is the whole contract:
        CLAUDE.md allows departing and requires saying why in one line, so a
        departure with `reason=None` is the drift this system is built to notice."""
        self.departures.append({"controller_said": action.get("action"),
                                "controller_step": action.get("step"),
                                "driver_did": doing, "reason": reason})

    def evidence_ids(self, hypothesis_id: str) -> list[str]:
        return [entry["id"] for entry in State.load(self.engagement).data["evidence_index"]
                if entry.get("hypothesis_id") == hypothesis_id]

    def open_hypothesis(self, vuln_class: str, statement: str, falsifier: str,
                        entry_point: dict) -> str | None:
        result = self.call("ledger.open_hypothesis", target=self.base + "/",
                           vuln_class=vuln_class, statement=statement, falsifier=falsifier,
                           entry_point=entry_point)
        if not result.get("ok", True):
            return None
        return result["data"]["hypothesis"]["id"]

    # --- the one switch between the two configurations ----------------------

    def claim(self, hypothesis_id: str, vuln_class: str, title: str,
              evidence_ids: list[str], impact: str = "", remediation: str = "",
              reproduce: list[str] | None = None) -> dict:
        """Try to put a finding in the ledger.

        Gated: through `ledger.record_finding`, which grades the evidence first.
        Ungated: straight into the state through `State.add_finding`.
        This method is the only difference between the two configurations.
        """
        if self.gated:
            result = self.call("ledger.record_finding", hypothesis_id=hypothesis_id,
                               title=title, evidence_ids=list(evidence_ids), impact=impact,
                               remediation=remediation, reproduce=reproduce or [])
            if result.get("ok"):
                # The gate's own label, read back rather than assumed: `confirmed`
                # may be reported as a vulnerability and `candidate` may not, and
                # a driver that treats the two as one outcome has lost the
                # distinction the gate exists to make.
                written = State.load(self.engagement).finding(
                    (result.get("data") or {}).get("finding") or "")
                outcome = f"recorded:{(written or {}).get('status', 'unknown')}"
            else:
                outcome = f"refused:{result.get('error')}"
        else:
            result = record_ungated(self.engagement, hypothesis_id, vuln_class, title,
                                    evidence_ids, impact, self.base + "/")
            self.calls += 1
            self.actions.append({"tool": "state.add_finding (ungated)", "ok": True,
                                 "error": None, "summary": result["summary"]})
            if self.verbose:
                print(f"      [ok ] {'state.add_finding (ungated)':24} {result['summary'][:88]}")
            outcome = "recorded:ungraded"
        self.claims.append({"vuln_class": vuln_class, "title": title, "outcome": outcome,
                            "evidence_count": len(evidence_ids),
                            "summary": str(result.get("summary")
                                           or result.get("message") or "")[:160]})
        return result


# --- driver 1: disciplined ---------------------------------------------------

def drive_disciplined(session: Session) -> None:
    """Consult the controller, read the requirement, take the control, record only
    what is proven, park what is not.

    Four classes reach `proven` here and one does not. The one that does not —
    reflected XSS — is the point of the driver: a disciplined run ends with an
    honest gap rather than a fifth finding.
    """
    base = session.base

    # Recon first, because that is what the controller says. It says `recon` once
    # per rung of the recon ladder until every rung has a measurement. This run
    # takes one rung (parameter-discovery) plus `recon.js_mine`, which mines the
    # same surface but is not a rung, and then departs with the reason stated,
    # which is what CLAUDE.md asks of a departure. The reason has to name what is
    # actually skipped: four rungs, not three, because `recon.fingerprint` shells
    # out to httpx whenever httpx is installed and is therefore no cheaper here
    # than the three that always do.
    action = session.consult()
    session.obeyed(action, "recon")
    session.call("recon.params", target=base + "/", depth=1)
    session.call("recon.js_mine", target=base + "/")
    action = session.consult()
    if action.get("action") == "recon":
        session.depart(action, "classify the surface already mapped",
                       "the four unrun recon rungs are host-liveness (nmap), service-fingerprint "
                       "(httpx, when installed), content-discovery (ffuf) and template-scan "
                       "(nuclei); this baseline must run offline and deterministically in seconds, "
                       "and none of the four changes which classes the fixture plants")

    # --- rce: the requirement is a nonce, so the cheap step is a baseline, not a
    # payload. The marker command is intrusive and the engagement had to enable
    # that tier in advance.
    session.call("proof.requirement", vuln_class="rce")
    rce = session.open_hypothesis(
        "rce", "the host parameter of /ping is interpolated into a shell command",
        "no separator changes the command's output", {"param": "host", "location": "query"})
    if rce:
        session.call("http.probe", url=f"{base}/ping?host=127.0.0.1", hypothesis_id=rce,
                     vuln_class="rce", note="baseline: what the endpoint returns for a clean value")
        marker = session.call("proof.exec_marker", url=base + "/ping?host=127.0.0.1{payload}",
                              hypothesis_id=rce, vuln_class="rce", separator=";", encode="url")
        if (session.call("proof.verify", vuln_class="rce", hypothesis=rce)
                .get("data", {}).get("grade")) == "proven":
            session.claim(rce, "rce", "Command injection in the host parameter of /ping",
                          [marker["evidence_id"]],
                          impact="arbitrary command execution as the service account",
                          remediation="do not build a shell command from request data",
                          reproduce=[f"curl '{base}/ping?host=127.0.0.1%3Bid'"])

    # --- lfi: one probe, because proof.file_read takes its own control. A class
    # whose tool collects the control is three ladder rungs cheaper than one whose
    # tool does not.
    session.call("proof.requirement", vuln_class="lfi")
    lfi = session.open_hypothesis(
        "lfi", "the file parameter of /view is joined to a directory without normalisation",
        "traversal is rejected at every depth", {"param": "file", "location": "query"})
    if lfi:
        session.call("proof.file_read", url=base + "/view?file={payload}", hypothesis_id=lfi,
                     vuln_class="lfi", encode="url", max_attempts=16)
        if (session.call("proof.verify", vuln_class="lfi", hypothesis=lfi)
                .get("data", {}).get("grade")) == "proven":
            session.claim(lfi, "lfi", "Arbitrary file read in the file parameter of /view",
                          session.evidence_ids(lfi),
                          impact="any file the service account can read",
                          remediation="resolve the path and verify it stays inside the "
                                      "content root",
                          reproduce=[f"curl '{base}/view?file=../../../../etc/passwd'"])

    # --- ssti: the cheap step establishes that the endpoint computes at all; the
    # proof step makes the result one that cannot appear by chance.
    session.call("proof.requirement", vuln_class="ssti")
    ssti = session.open_hypothesis(
        "ssti", "the expr parameter of /calc is evaluated server-side",
        "the expression is echoed back verbatim", {"param": "expr", "location": "query"})
    if ssti:
        session.call("http.probe", url=f"{base}/calc?expr=1%2B1", hypothesis_id=ssti,
                     vuln_class="ssti", note="does the endpoint compute, or echo")
        evaluated = session.call("proof.template_eval", url=base + "/calc?expr={payload}",
                                 hypothesis_id=ssti, vuln_class="ssti", encode="url",
                                 expression_template="{a}*{b}")
        if (session.call("proof.verify", vuln_class="ssti", hypothesis=ssti)
                .get("data", {}).get("grade")) == "proven":
            session.claim(ssti, "ssti", "Server-side expression evaluation in /calc",
                          [evaluated["evidence_id"]],
                          impact="arbitrary expression evaluation in the application process",
                          remediation="never evaluate request data as an expression",
                          reproduce=[f"curl '{base}/calc?expr=7260*4627'"])

    # --- idor: a differential class, so the control is not optional. Three
    # requests: her own note, the cross-read, and an id that cannot exist. The two
    # records that name the actor, the subject and the control are added
    # explicitly, because http.probe records the response and not who it was for.
    session.call("proof.requirement", vuln_class="idor")
    idor = session.open_hypothesis(
        "idor", "/api/note returns any note id regardless of the user parameter",
        "a note owned by another user is refused", {"param": "id", "location": "query"})
    if idor:
        session.call("http.probe", url=f"{base}/api/note?id=1&user=alice", hypothesis_id=idor,
                     vuln_class="idor", actor="alice", note="alice reads her own note")
        cross = session.call("http.probe", url=f"{base}/api/note?id=2&user=alice",
                             hypothesis_id=idor, vuln_class="idor", actor="alice",
                             note="alice requests note 2, which she does not own")
        control = session.call("http.probe", url=f"{base}/api/note?id=999999&user=alice",
                               hypothesis_id=idor, vuln_class="idor", actor="alice",
                               note="control: a note id that cannot exist")
        owner = _json_field(cross.get("output"), "owner")
        if owner and owner != "alice":
            session.call("ledger.add_evidence", kind="probe", vuln_class="idor",
                         hypothesis_id=idor, target=base + "/",
                         record={"actor": "alice", "accessed_subject": owner,
                                 "response": {"status": cross["data"]["status"],
                                              "body_span": str(cross.get("output"))[:500]},
                                 "summary": f"alice received the note owned by {owner}"})
            session.call("ledger.add_evidence", kind="control", vuln_class="idor",
                         hypothesis_id=idor, target=base + "/",
                         record={"is_control": True, "actor": "alice",
                                 "response": {"status": control["data"]["status"],
                                              "body_span": str(control.get("output"))[:500]},
                                 "summary": "a note id that does not exist answers "
                                            f"{control['data']['status']}, so 200 is not the "
                                            "generic response to any id"})
            if (session.call("proof.verify", vuln_class="idor", hypothesis=idor)
                    .get("data", {}).get("grade")) == "proven":
                session.claim(idor, "idor",
                              "Any note id is readable regardless of the user parameter",
                              session.evidence_ids(idor),
                              impact="every note in the application, including other tenants'",
                              remediation="authorise on the session identity, never on a request "
                                          "parameter",
                              reproduce=[f"curl '{base}/api/note?id=2&user=alice'"])

    # --- xss: the requirement names a browser, there is no browser in an offline
    # run, so this one ends as a stated gap. Parked at priority 0, revivable the
    # moment a browser is available — not falsified, because nothing falsified it.
    session.call("proof.requirement", vuln_class="xss")
    xss = session.open_hypothesis(
        "xss", "the q parameter of /search is reflected into a script string literal",
        "the value is encoded in both the HTML and the script context",
        {"param": "q", "location": "query"})
    if xss:
        token = "argusbaselinexss"
        session.call("http.probe", url=f"{base}/search?q={token}", hypothesis_id=xss,
                     vuln_class="xss", token=token)
        graded = session.call("proof.verify", vuln_class="xss", hypothesis=xss)
        if (graded.get("data") or {}).get("grade") != "proven":
            session.call("ledger.park", hypothesis_id=xss,
                         reason="reflection is not execution. The missing check is a headless "
                                "browser reporting the nonce, and this run has no browser; revive "
                                "it when one is available")


# --- driver 2: optimistic ----------------------------------------------------

def drive_optimistic(session: Session) -> None:
    """The failure mode the system was built against: any signal becomes a finding.

    It never calls `ledger.next_action`, never reads a proof requirement and never
    takes a control. Each claim below is a real mistake with a name in
    EVIDENCE_POLICY.md's "Prevents" column, made in the order a model short of
    context tends to make them.
    """
    base = session.base

    # A 500 on a quote becomes "SQL injection".
    sqli = session.open_hypothesis(
        "sqli", "the id parameter of /item is concatenated into a SQL query",
        "a quote does not change the response", {"param": "id", "location": "query"})
    if sqli:
        differential = session.call("http.differential", url=base + "/item", hypothesis_id=sqli,
                                    vuln_class="sqli", baseline_params={"id": "1"},
                                    variant_params={"id": "1'"}, repeat=2)
        session.claim(sqli, "sqli", "SQL injection in the id parameter of /item",
                      _evidence_of(differential),
                      impact="full read access to the application database")

    # A reflected payload becomes "XSS".
    xss = session.open_hypothesis(
        "xss", "the q parameter of /search is vulnerable to cross-site scripting",
        "the value is encoded", {"param": "q", "location": "query"})
    if xss:
        token = "argusoptimisticxss"
        reflected = session.call("http.probe", url=f"{base}/search?q={token}",
                                 hypothesis_id=xss, vuln_class="xss", token=token)
        session.claim(xss, "xss", "Reflected cross-site scripting in /search",
                      _evidence_of(reflected),
                      impact="script execution in any visitor's session")

    # A timing difference becomes "command injection".
    #
    # Note what this probe actually does: `; sleep 2` reaches a shell on the
    # fixture through `http.differential`, which is an `active`-tier tool. The
    # broker does not catch it, because a risk tier is a property of the tool and
    # not of the payload. `proof.exec_marker`'s intrusive gate governs whether this
    # system will *prove* execution, not whether a request can cause it. The
    # payload is kept benign — it sleeps and returns — for exactly that reason.
    rce = session.open_hypothesis(
        "rce", "the host parameter of /ping is vulnerable to command injection",
        "the response time does not change", {"param": "host", "location": "query"})
    if rce:
        timed = session.call("http.differential", url=base + "/ping", hypothesis_id=rce,
                             vuln_class="rce", baseline_params={"host": "127.0.0.1"},
                             variant_params={"host": "127.0.0.1; sleep 2"}, repeat=1)
        session.claim(rce, "rce", "Command injection in the host parameter of /ping",
                      _evidence_of(timed),
                      impact="arbitrary command execution on the host")

    # A 200 on `id=2` becomes "broken access control".
    idor = session.open_hypothesis(
        "idor", "/api/note exposes other users' notes",
        "the request is refused", {"param": "id", "location": "query"})
    if idor:
        probe = session.call("http.probe", url=f"{base}/api/note?id=2&user=alice",
                             hypothesis_id=idor, vuln_class="idor", actor="alice")
        session.claim(idor, "idor", "Insecure direct object reference in /api/note",
                      _evidence_of(probe),
                      impact="every note belonging to every user")


# --- driver 3: repetitive ----------------------------------------------------

REPETITIVE_PAYLOADS = ("1'", '1"', "1 OR 1=1", "1 AND 1=1", "1/**/OR/**/1=1",
                       "1;--", "1' OR '1'='1", "1 UNION SELECT 1,2")


def drive_repetitive(session: Session) -> None:
    """One class, eight payloads, the same question every time.

    It asks the controller once and then ignores the answer without giving a
    reason, which is the departure the contract forbids. Then it varies the
    payload until the per-class probe budget refuses it. The refusal is the
    measurement: the budget exists to force a change of strategy rather than a
    change of payload.
    """
    base = session.base
    action = session.consult()
    session.depart(action, "probe sqli immediately", None)

    sqli = session.open_hypothesis(
        "sqli", "the id parameter of /item is injectable",
        "a payload does not change the response", {"param": "id", "location": "query"})
    if not sqli:
        return
    last_evidence, spent_at = None, None
    for index, payload in enumerate(REPETITIVE_PAYLOADS, start=1):
        result = session.call("http.probe", url=base + "/item", params={"id": payload},
                              hypothesis_id=sqli, vuln_class="sqli",
                              note=f"payload variant {index}")
        if not result.get("ok", True):
            spent_at = index
            session.stopped_by = (f"{result.get('error')} after {index - 1} probe(s) on sqli; "
                                  f"payload variants {index}-{len(REPETITIVE_PAYLOADS)} were "
                                  f"never sent, so this run cannot say whether they would have "
                                  f"discriminated")
            break
        last_evidence = result.get("evidence_id") or last_evidence
    if last_evidence:
        session.claim(sqli, "sqli", "SQL injection in the id parameter of /item",
                      [last_evidence],
                      impact="full read access to the application database")
    if spent_at is None:
        session.stopped_by = None


DRIVERS = {"disciplined": drive_disciplined,
           "optimistic": drive_optimistic,
           "repetitive": drive_repetitive}


# --- measurement -------------------------------------------------------------

def vacuous_grade(vuln_class: str) -> dict | None:
    """What a class grades on one evidence record that observed nothing.

    A requirement is only as strong as its weakest required check, and some of
    those checks are hygiene checks phrased as absences — "proof command stayed
    benign", "secret stored redacted". A check like that passes on a record with
    no content in it, and `_grade` reads one passing required check as
    `supported`. So for some classes a probe that saw nothing is enough to put a
    candidate in the ledger.

    This grades `[{"kind": "probe"}]` — a record with no observation at all — and
    reports the classes where that is not `unproven`. It is computed rather than
    asserted so that it stops being printed the day the matrix changes.
    """
    verdict = proof_mod.verify(vuln_class, [{"kind": "probe"}])
    if verdict.grade == "unproven" or verdict.grade == "refused":
        return None
    spec = proof_mod.spec_for(vuln_class)
    required = set(spec.required_checks) if spec else set()
    return {"vuln_class": vuln_class, "grade": verdict.grade,
            "passing_required_checks": sorted(c["check"] for c in verdict.checks
                                              if c["ok"] and c["check"] in required)}


def reflected_token_grade(vuln_class: str) -> dict | None:
    """What a class grades when the only thing in evidence is the probe's own
    token, echoed back by the target.

    `http.probe` writes whatever is passed as `token` into the evidence record's
    `nonce` field, and `verify_command_output` reads one of its required checks
    off "the nonce appears in the observed output". The check that could not be
    satisfied by an echo — the `uid=` line — is reported and not required. So for
    the command-output classes, a page that reflects a string meets the
    requirement with nothing executed, which is the mistake EVIDENCE_POLICY.md
    names twice: reflection reported as execution, and a report that needs the
    host rebuilt to verify.

    This grades exactly that record and reports only the classes where it reaches
    `proven`, because a reflection that reaches `supported` is already covered by
    `vacuous_grade`. Computed, not asserted, so it stops being printed the day the
    requirement or the field mapping changes.
    """
    token = "argusreflectedtoken"
    record = {"kind": "probe", "nonce": token, "payload": token,
              "response": {"status": 200, "body_span": f"<p>No results for {token}</p>"}}
    verdict = proof_mod.verify(vuln_class, [record])
    if verdict.grade != "proven":
        return None
    spec = proof_mod.spec_for(vuln_class)
    required = set(spec.required_checks) if spec else set()
    return {"vuln_class": vuln_class, "grade": verdict.grade,
            "passing_required_checks": sorted(c["check"] for c in verdict.checks
                                              if c["ok"] and c["check"] in required),
            "reported_but_not_required": sorted(c["check"] for c in verdict.checks
                                                if c["check"] not in required)}


def measure(session: Session, elapsed: float) -> dict:
    """Read the engagement back and grade every finding in it, now.

    The regrade is the apples-to-apples number: it runs the same verifier over the
    same evidence in both configurations, whether or not anything graded the
    evidence at write time.
    """
    collected = metrics.collect(session.engagement)
    state = State.load(session.engagement)
    findings = state.data["findings"]

    regrade: Counter = Counter()
    per_finding, disagreements = [], []
    for finding in findings:
        records = state.load_evidence(finding.get("evidence_ids") or [])
        verdict = proof_mod.verify(finding.get("vuln_class") or "", records)
        regrade[verdict.grade] += 1
        stored = (finding.get("proof") or {}).get("grade")
        if stored and stored != verdict.grade:
            disagreements.append({"finding": finding["id"], "stored": stored,
                                  "regraded": verdict.grade})
        per_finding.append({
            "id": finding["id"], "vuln_class": finding.get("vuln_class"),
            "title": finding.get("title"), "ledger_status": finding.get("status"),
            "stored_grade": stored, "regrade": verdict.grade,
            "missing": verdict.missing,
            "labelled_not_a_vulnerability": finding.get("status") == "candidate",
        })

    # The two numbers claim 1 is about. `unsupported_admitted` is the share of
    # recorded findings whose evidence meets none of the requirement — the ones a
    # review rejects outright. `partial_unlabelled` is the quieter failure: the
    # evidence is a real signal with a check missing, and nothing in the ledger
    # says so, so a reader cannot tell it from a proof.
    unsupported = [f for f in per_finding if f["regrade"] in ("unproven", "refused")]
    partial_unlabelled = [f for f in per_finding
                          if f["regrade"] == "supported" and not f["labelled_not_a_vulnerability"]]

    probes = state.data["probes"]
    steps_by_class: dict[str, set] = {}
    for probe in probes:
        # The same denominator argus.orchestrator.metrics uses for its repeat
        # ratio: the ladder step a probe declared, falling back to the tool name.
        steps_by_class.setdefault(probe["vuln_class"], set()).add(
            probe.get("step") or probe["tool"])
    unnamed = sorted({vuln_class for vuln_class, steps in steps_by_class.items()
                      if all("." in step for step in steps)})

    vacuous: dict[str, dict] = {}
    reflected: dict[str, dict] = {}
    for finding in findings:
        entry = vacuous_grade(finding.get("vuln_class") or "")
        if entry is not None:
            vacuous[entry["vuln_class"]] = entry
        entry = reflected_token_grade(finding.get("vuln_class") or "")
        if entry is not None:
            reflected[entry["vuln_class"]] = entry

    proven = regrade["proven"]
    return {
        "driver": session.driver,
        "engagement": session.engagement,
        "config": "gate" if session.gated else "no-gate",
        "elapsed_s": round(elapsed, 1),
        "tool_calls": session.calls,
        "classes_that_grade_supported_on_an_empty_probe": sorted(
            vacuous.values(), key=lambda entry: entry["vuln_class"]),
        "classes_that_grade_proven_on_a_reflected_token": sorted(
            reflected.values(), key=lambda entry: entry["vuln_class"]),
        "admission": {
            "findings_recorded": len(findings),
            "by_ledger_status": dict(Counter(f.get("status") for f in findings)),
            "regrade": {"proven": regrade["proven"], "supported": regrade["supported"],
                        "unproven": regrade["unproven"] + regrade["refused"]},
            "unsupported_admitted": len(unsupported),
            "unsupported_share": (round(len(unsupported) / len(findings), 2) if findings else None),
            "partial_findings_unlabelled": len(partial_unlabelled),
            "claims_attempted": len(session.claims),
            "claims_refused": len([c for c in session.claims
                                   if c["outcome"].startswith("refused")]),
            "findings": per_finding,
            "stored_vs_regrade_disagreements": disagreements,
        },
        "effort": {
            "probes": collected["effort"]["probes"],
            "probes_by_class": collected["effort"]["probes_by_class"],
            "probes_per_proven_finding": (round(collected["effort"]["probes"] / proven, 2)
                                          if proven else None),
            "repeat_ratio_by_class": collected["effort"]["repeat_ratio_by_class"],
            "worst_repeat_ratio": (max(collected["effort"]["repeat_ratio_by_class"].items(),
                                       key=lambda kv: kv[1])
                                   if collected["effort"]["repeat_ratio_by_class"] else None),
            "distinct_steps_by_class": {k: sorted(v) for k, v in sorted(steps_by_class.items())},
            "classes_with_no_named_ladder_step": unnamed,
            "active_minutes": collected["effort"]["active_minutes"],
            "hypotheses": collected["effort"]["hypotheses"],
        },
        "controller": {
            "consulted": session.controller_consulted,
            "actions_aligned": session.controller_aligned,
            "departures_with_a_reason": len([d for d in session.departures if d["reason"]]),
            "departures_with_no_reason": len([d for d in session.departures if not d["reason"]]),
            "departures": session.departures,
        },
        # The engagement's refusal log is written by the broker's pre-probe gate
        # (`_record_refusal` in argus/broker/mcp.py) and by nothing else, so a
        # refusal from a ledger verb — `unproven` on record_finding, the one claim
        # 1 is about — never reaches it. `argus metrics` reads that log, so this
        # driver has to count its own refusals, and the difference is reported.
        "refusals": {
            "observed_by_driver": dict(sorted(session.refusals.items())),
            "in_the_engagement_log": collected["refusals"]["by_kind"],
            "unlogged_by_kind": {kind: count - collected["refusals"]["by_kind"].get(kind, 0)
                                 for kind, count in sorted(session.refusals.items())
                                 if count > collected["refusals"]["by_kind"].get(kind, 0)},
            "stopped_the_run": session.stopped_by,
        },
        "claims": session.claims,
    }


# --- running ------------------------------------------------------------------

def run_one(server, driver: str, config: str, base: str, port: int, verbose: bool,
            keep: bool) -> dict:
    engagement = f"baseline-{driver}-{'gate' if config == 'gate' else 'nogate'}"
    shutil.rmtree(Paths(engagement).dir, ignore_errors=True)
    opened = hooks.open_engagement(
        engagement,
        objective=f"baseline: the {driver} driver against the local fixture, gate {config}",
        scope={"in_scope": [f"127.0.0.1:{port}"], "out_of_scope": [], "allowed_ports": [port]},
        tiers=["passive", "active", "intrusive"], authorisation=AUTHORISATION)
    if not opened:
        raise SystemExit(f"could not open {engagement}: {opened.message}")
    admitted = hooks.add_target(engagement, base + "/")
    if not admitted:
        raise SystemExit(f"could not admit the fixture: {admitted.message}")

    session = Session(server, driver, engagement, base, gated=(config == "gate"),
                      verbose=verbose)
    started = time.monotonic()
    try:
        DRIVERS[driver](session)
        return measure(session, time.monotonic() - started)
    finally:
        # In `finally` because a driver that raises half way through would
        # otherwise leave a baseline engagement in `engagements/` beside the real
        # ones, and this script is meant to be safe to run while other agents are
        # working there. `--keep` is how a failed run is kept for inspection.
        if not keep:
            shutil.rmtree(Paths(engagement).dir, ignore_errors=True)


# --- output -------------------------------------------------------------------

FRAMING = [
    "WHAT THIS IS, AND IS NOT",
    "  The subject under test is a scripted driver, not a model: each driver is a fixed",
    "  sequence of broker calls. So these runs measure what the GATE does to a given",
    "  sequence of actions, not what a model would do.",
    "  --no-gate switches off the grading on the finding write path and nothing on the probe",
    "  path: scope, tier and probe-budget refusals stay on in both configurations.",
]


def _cell(value) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


def _table(headers: list[str], rows: list[list[str]]) -> list[str]:
    widths = [max(len(headers[i]), *(len(row[i]) for row in rows)) if rows else len(headers[i])
              for i in range(len(headers))]
    lines = ["  " + "  ".join(h.ljust(widths[i]) for i, h in enumerate(headers)),
             "  " + "  ".join("-" * widths[i] for i in range(len(headers)))]
    for row in rows:
        lines.append("  " + "  ".join(row[i].ljust(widths[i]) for i in range(len(headers))))
    return lines


def render(results: list[dict], base: str) -> str:
    out = ["argus offline baselines — what the ledger gate does to a fixed sequence of actions",
           f"fixture {base} · python {sys.version.split()[0]} · "
           f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())}", ""]
    out += FRAMING
    out.append("")

    out.append("CLAIM 1 — an admission gate reduces unsupported findings")
    out.append("  measured as: the share of recorded findings whose evidence meets none of the")
    out.append("  class requirement, re-graded now by the same verifier in both configurations.")
    rows = []
    for result in results:
        admission = result["admission"]
        rows.append([
            result["driver"], result["config"],
            _cell(admission["claims_attempted"]), _cell(admission["claims_refused"]),
            _cell(admission["findings_recorded"]),
            _cell(admission["regrade"]["proven"]), _cell(admission["regrade"]["supported"]),
            _cell(admission["regrade"]["unproven"]),
            _cell(admission["unsupported_admitted"]),
            ("-" if admission["unsupported_share"] is None
             else f"{admission['unsupported_share'] * 100:.0f}%"),
            _cell(admission["partial_findings_unlabelled"]),
        ])
    out += _table(["driver", "config", "claims", "refused", "recorded",
                   "proven", "supported", "unproven", "unsupported", "share", "unlabelled"], rows)
    out.append("")

    out.append("CLAIM 2 — an external controller reduces wasted probes")
    out.append("  measured as: probes per proven finding, and probes per distinct ladder step")
    out.append("  within a class (the repeat-payload rate), from argus.orchestrator.metrics.")
    rows, starred = [], False
    for result in results:
        effort, controller = result["effort"], result["controller"]
        worst = effort["worst_repeat_ratio"]
        mark = ""
        if worst and worst[1] > 1.0 and worst[0] in effort["classes_with_no_named_ladder_step"]:
            mark, starred = "*", True
        rows.append([
            result["driver"], result["config"], _cell(effort["probes"]),
            _cell(result["admission"]["regrade"]["proven"]),
            _cell(effort["probes_per_proven_finding"]),
            ("-" if not worst else f"{worst[1]:.1f} ({worst[0]}){mark}"),
            f"{controller['actions_aligned']}/{controller['consulted']}",
            f"{controller['departures_with_a_reason']}/{controller['departures_with_no_reason']}",
            _cell(sum(result["refusals"]["observed_by_driver"].values())),
            _cell(result["tool_calls"]),
        ])
    out += _table(["driver", "config", "probes", "proven", "probes/proven", "worst repeat",
                   "obeyed", "depart r/none", "refusals", "calls"], rows)
    if starred:
        out.append("  * that class was probed only through tools that declare no ladder step, so")
        out.append("    its denominator is 1 and the ratio counts distinct questions as repeats.")
    out.append("")

    for result in results:
        out.append(f"{result['driver']} / {result['config']} "
                   f"({result['tool_calls']} tool call(s), {result['elapsed_s']}s)")
        admission, effort, refusals = result["admission"], result["effort"], result["refusals"]
        out.append(f"  ledger status:        {admission['by_ledger_status'] or 'no findings'}")
        out.append(f"  probes by class:      {effort['probes_by_class']}")
        out.append(f"  repeat ratio:         {effort['repeat_ratio_by_class']}")
        out.append(f"  refusals (driver):    {refusals['observed_by_driver'] or 'none'}")
        out.append(f"  refusals (log):       {refusals['in_the_engagement_log'] or 'none'}")
        if refusals["unlogged_by_kind"]:
            out.append(f"  not in the log:       {refusals['unlogged_by_kind']}  <- refusals from "
                       f"the ledger verbs, which argus metrics therefore cannot report")
        if refusals["stopped_the_run"]:
            out.append(f"  stopped by:           {refusals['stopped_the_run']}")
        for claim in result["claims"]:
            out.append(f"  claim {claim['vuln_class']:<7} {claim['outcome']:<19} "
                       f"{claim['summary'][:80]}")
        for finding in admission["findings"]:
            missing = (", missing: " + ", ".join(finding["missing"])) if finding["missing"] else ""
            out.append(f"  finding {finding['id']} {finding['vuln_class']:<7} "
                       f"ledger={finding['ledger_status']:<9} "
                       f"regrade={finding['regrade']}{missing}")
        for departure in result["controller"]["departures"]:
            said = str(departure["controller_said"])
            if departure["controller_step"]:
                said += "/" + str(departure["controller_step"])
            out.append(f"  departure: controller said {said}, driver did "
                       f"{departure['driver_did']} — "
                       f"{departure['reason'] or 'NO REASON STATED'}")
        if admission["stored_vs_regrade_disagreements"]:
            out.append(f"  WARNING grade changed between write and measurement: "
                       f"{admission['stored_vs_regrade_disagreements']}")
        out.append("")

    out += observations(results)
    out += closing(results)
    return "\n".join(out)


def observations(results: list[dict]) -> list[str]:
    """Things these runs showed about the gate itself, each one computed above.

    A baseline run is worth doing partly for its numbers and partly for what it
    notices on the way. Everything here is derived from the runs, so it stops
    being printed when it stops being true.
    """
    lines: list[str] = []
    vacuous: dict[str, dict] = {}
    reflected: dict[str, dict] = {}
    for result in results:
        for entry in result["classes_that_grade_supported_on_an_empty_probe"]:
            vacuous[entry["vuln_class"]] = entry
        for entry in result["classes_that_grade_proven_on_a_reflected_token"]:
            reflected[entry["vuln_class"]] = entry
    unlogged: Counter = Counter()
    for result in results:
        unlogged.update(result["refusals"]["unlogged_by_kind"])
    unnamed = sorted({c for result in results
                      for c in result["effort"]["classes_with_no_named_ladder_step"]})

    if not (vacuous or reflected or unlogged or unnamed):
        return lines
    lines.append("OBSERVATIONS FROM THESE RUNS — about the gate, not about the drivers")
    lines.append("")
    if vacuous:
        for entry in sorted(vacuous.values(), key=lambda e: e["vuln_class"]):
            lines.append(f"  {entry['vuln_class']}: one evidence record with no observation in it "
                         f"already grades `{entry['grade']}`, carried by "
                         f"{entry['passing_required_checks']} — a required check that passes "
                         f"because nothing bad was seen rather than because something was.")
        lines.append("  So for these classes the gate stopped each claim these drivers made short "
                     "of `confirmed`, and did not stop any of them from becoming a candidate. In "
                     "this run that is how a timing difference with no nonce reached the ledger as "
                     "a candidate `command injection`, which is the exact mistake "
                     "EVIDENCE_POLICY.md says the rce requirement exists to prevent.")
        lines.append("")
    if reflected:
        for entry in sorted(reflected.values(), key=lambda e: e["vuln_class"]):
            lines.append(f"  {entry['vuln_class']}: a record whose only content is the probe's own "
                         f"token echoed back by the target grades `{entry['grade']}` on "
                         f"{entry['passing_required_checks']}, with "
                         f"{entry['reported_but_not_required']} reported and not required. "
                         f"`http.probe` puts its `token` argument in the evidence record's `nonce` "
                         f"field, so a reflected string — never execution, by EVIDENCE_POLICY.md — "
                         f"meets the nonce check with nothing executed and no intrusive tier.")
        lines.append("  That is the limit of what the gated column above shows: it is the gate "
                     "refusing THESE claims, not the gate refusing every unproven claim. A "
                     "confirmed finding is one argument away for a driver that passes a reflected "
                     "token as the nonce, so do not read the zero in the gated column as a bound.")
        lines.append("")
    if unlogged:
        lines.append(f"  {dict(unlogged)} refusal(s) were returned to the driver and written to no "
                     f"log. The engagement's refusal log is fed by the broker's pre-probe gate "
                     f"only, so a refused finding leaves no trace for `argus metrics` to read — "
                     f"and 'how many unproven claims the gate turned away' is the number claim 1 "
                     f"is about.")
        lines.append("")
    if unnamed:
        lines.append(f"  {unnamed} were probed only through tools that declare no ladder step "
                     f"(`http.probe`, `http.differential`), so every call collapses to one step "
                     f"and the repeat-payload ratio cannot tell a changed question from a changed "
                     f"payload. Those two tools are where a model spends most of its calls.")
        lines.append("")
    return lines


def closing(results: list[dict]) -> list[str]:
    gated = {r["driver"]: r for r in results if r["config"] == "gate"}
    ungated = {r["driver"]: r for r in results if r["config"] == "no-gate"}
    admitted_ungated = sum(r["admission"]["unsupported_admitted"] for r in ungated.values())
    admitted_gated = sum(r["admission"]["unsupported_admitted"] for r in gated.values())
    unlabelled_ungated = sum(r["admission"]["partial_findings_unlabelled"]
                             for r in ungated.values())

    lines = ["WHAT THESE NUMBERS SUPPORT, AND WHAT THEY DO NOT", ""]
    if gated and ungated:
        lines.append(f"  Claim 1. Across these drivers the ungated write path admitted "
                     f"{admitted_ungated} finding(s) whose evidence meets no part of its class "
                     f"requirement, and {unlabelled_ungated} more that are a partial signal with "
                     f"nothing in the ledger saying so; the gated path admitted {admitted_gated}.")
        lines.append("  That difference is a property of the gate, not a discovery about models: "
                     "hooks.record_finding refuses `unproven` by construction, so the gated "
                     "column could not have come out any other way. What the run measures is the "
                     "size of what the gate catches for THESE sequences.")
    else:
        lines.append("  Claim 1 needs both configurations to say anything, and this run had only "
                     f"{'the gated one' if gated else 'the ungated one'}. Re-run without "
                     f"--config to get the comparison.")
    lines.append("")
    if "disciplined" in gated and "disciplined" in ungated:
        same = (gated["disciplined"]["admission"]["findings_recorded"]
                == ungated["disciplined"]["admission"]["findings_recorded"])
        what = ("recorded the same findings in both configurations" if same else
                "recorded DIFFERENT findings in the two configurations, which is a defect in the "
                "driver and not a result")
        lines.append(f"  The disciplined driver {what}: a driver that grades its own evidence "
                     f"before claiming is unaffected by the gate. The gate's entire effect here "
                     f"falls on the drivers that do not.")
        lines.append("")
    # Over every run in this invocation, not only the gated half: with
    # `--config no-gate` the gated half is empty, and an earlier version of this
    # line therefore printed "none of these drivers proved nothing" directly under
    # a table whose `proven` column was zero for all of them.
    barren = sorted(f"{r['driver']}/{r['config']}" for r in results
                    if not r["admission"]["regrade"]["proven"])
    if barren:
        lines.append(f"  Claim 2. Probes per proven finding is defined only for a run that proved "
                     f"something, and {len(barren)} of these runs ({', '.join(barren)}) proved "
                     f"nothing at all — that is the measurement, not a missing value.")
    else:
        lines.append("  Claim 2. Every run in this invocation proved something, so probes per "
                     "proven finding is defined for all of them.")
    lines.append(f"  The repeat-payload ratio separates them: a driver that varies the payload "
                 f"shows many probes per distinct ladder step, and the per-class budget of "
                 f"{config.PROBE_BUDGET_PER_CLASS} refused the next one.")
    drivers = sorted({r["driver"] for r in results})
    lines.append(f"  The controller axis is weaker than the gate axis and should not be read as an "
                 f"A/B: the gate was switched while the action sequence was held fixed, but the "
                 f"{len(drivers)} driver(s) here ({', '.join(drivers)}) differ in more than "
                 f"whether they consult the controller, so their probe counts measure "
                 f"{len(drivers)} hand-written behaviour(s) rather than one variable.")
    lines.append("")
    lines.append("  And the sentence that bounds all of it: the gate's effect on THIS driver set "
                 "is a property of the gate, and the driver set's resemblance to a model's "
                 "behaviour is an assumption, not a result. Three of the five claims in "
                 "ARCHITECTURE.md section 6 need live models and are not touched here.")
    return lines


# --- entry point --------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="argus-baselines", description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--driver", action="append", choices=sorted(DRIVERS),
                        help="run only this driver; repeatable (default: all three)")
    parser.add_argument("--config", action="append", choices=list(CONFIGS),
                        help="run only this configuration; repeatable (default: both)")
    parser.add_argument("--json", action="store_true", help="machine-readable, for a harness")
    parser.add_argument("--verbose", action="store_true", help="print every call as it is made")
    parser.add_argument("--keep", action="store_true",
                        help="leave the baseline engagements on disk for inspection")
    args = parser.parse_args(argv)

    drivers = args.driver or sorted(DRIVERS)
    configs = args.config or list(CONFIGS)

    app, port = vulnapp.serve()
    base = f"http://127.0.0.1:{port}"
    server = merge(SERVERS)
    results = []
    try:
        for driver in drivers:
            for config in configs:
                if not args.json:
                    print(f"== {driver} / {config} ==", flush=True)
                results.append(run_one(server, driver, config, base, port,
                                       verbose=args.verbose and not args.json, keep=args.keep))
    finally:
        app.shutdown()

    if args.json:
        print(json.dumps({"fixture": base, "python": sys.version.split()[0],
                          "runs": results}, ensure_ascii=False, indent=2))
    else:
        print()
        print(render(results, base))
    return 0


if __name__ == "__main__":
    sys.exit(main())
