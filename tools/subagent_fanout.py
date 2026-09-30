#!/usr/bin/env python3
"""Fan a white-box challenge out to one subagent per mechanism layer, safely.

Why this exists. A layered white-box challenge is walked one layer at a time,
and that is the measured time sink: the diemthi attempt closed eleven layers
serially, each by a cheap read-only measurement that did not depend on any
other. Those are independent, so they can run at once.

What makes that dangerous rather than merely fast is the control loop. If every
subagent calls `tools/hooks.py post-probe` itself, they race on one state.json
and burn the per-class probe budget in parallel -- defeating the exact rule
`tools/decide.py` exists to enforce. And a subagent's prose is a hypothesizer
output with no evidentiary weight, so merging its conclusions directly would put
model text where a captured response belongs.

So this tool draws the boundary mechanically:

  --contract            the single source of truth for what a subagent returns.
                        The agent definitions point here instead of restating it,
                        so the contract cannot drift from the validator.
  --brief SOURCE        run tools/novel_plan.py and emit one brief per layer,
                        each carrying its own falsifier, its probe ceiling, and
                        the layers a previous attempt already measured dead.
  --validate REPORT     refuse a report that claims more than it measured.
  --merge REPORTS...    validate, rank, and print the hooks.py commands for the
                        MAIN thread to run. This tool never writes state.json;
                        hooks stay the only write gate.

Roles, in the AGENTS.md sense: a subagent is a `reader` and a `writer`. It never
gets to be the machine that verifies.
"""
import argparse
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import chain_match  # noqa: E402  -- the strong-match short-circuit needs its scorer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ATTEMPTS = os.path.join(ROOT, "knowledge", "attempts")
NOVEL_PLAN = os.path.join(ROOT, "tools", "novel_plan.py")

WRITE_METHODS = ("POST", "PUT", "DELETE", "PATCH")
TRANSPORTS = ("ok", "timeout", "reset", "error", "empty")
# tools/hooks.py:39 is the authority and spells the negative verdict `falsifies`;
# this contract shipped `refutes`, so --merge emitted a command hooks.py refuses.
# Be liberal about what a subagent reports and canonical about what is emitted.
VERDICTS = ("confirms", "refutes", "falsifies", "inconclusive")
HOOKS_VERDICT = {"confirms": "confirms", "inconclusive": "inconclusive",
                 "refutes": "falsifies", "falsifies": "falsifies"}
KINDS = ("surface", "class", "impact", "transport")
# a layer gets five probes, the same ceiling decide.py enforces per class
PROBE_CEILING = 5

CONTRACT = {
    "_what": "the JSON a ctf-layer-prober subagent returns, one object per layer",
    "_rules": [
        "evidence MUST be a verbatim substring of response_excerpt from the same probe",
        "LIMIT: the validator checks evidence-inside-excerpt, NOT "
        "excerpt-inside-response -- it never sees the response, so a hand-typed "
        "excerpt containing a typo passes. Measured: a subagent mistyped one word "
        "of a Vietnamese 404 body and --validate accepted the report, because the "
        "evidence substring it chose sat outside the typo. Paste the excerpt from "
        "the tool's own output, never from memory -- tools/web/http_probe.py holds "
        "the request and the response together for exactly this reason",
        "verdict=confirms requires evidence_kind class or impact and transport ok",
        "a timeout, reset, empty body or error is transport evidence and can never confirm",
        "a login redirect, a registration success or a rendered form is surface evidence",
        "read-only probes only: a write-shaped request needs the main thread, not a subagent",
        "at most %d probes; on exhaustion report falsifier_outcome not-measured and stop" % PROBE_CEILING,
    ],
    "layer_id": "<the id novel_plan gave this layer>",
    "challenge": "<challenge name as state.py knows it>",
    "class": "<bug class id from knowledge/bug-classes.json, or null if undecided>",
    "files_read": ["path/to/file.js:120", "..."],
    "probes": [{
        "request": "GET /api/thing?x=1   (or the full http_probe.py command)",
        "transport": "|".join(TRANSPORTS),
        "status": 200,
        "response_excerpt": "<verbatim bytes from the response, not a summary>",
        "evidence": "<the substring of response_excerpt that proves the point>",
        "evidence_kind": "|".join(KINDS),
        "verdict": "|".join(VERDICTS),
    }],
    "falsifier_outcome": "held | broken | not-measured",
    "_verdict_note": ("report confirms|refutes|inconclusive; --merge rewrites `refutes` "
                      "to `falsifies`, which is the word tools/hooks.py accepts"),
    "conclusion": "<one sentence, labelled hypothesis, no evidentiary weight>",
    "cost_minutes": 0,
}


# ------------------------------------------------------------------ prior work

def load_attempts():
    """Every layer a previous attempt measured dead, with its measurement."""
    out = []
    if not os.path.isdir(ATTEMPTS):
        return out
    for name in sorted(os.listdir(ATTEMPTS)):
        if not name.endswith(".json"):
            continue
        try:
            with open(os.path.join(ATTEMPTS, name), encoding="utf-8") as fh:
                payload = json.load(fh)
        except (OSError, ValueError):
            continue
        for dead in payload.get("layers_measured_dead", []):
            out.append({
                "from_challenge": payload.get("challenge") or name,
                "layer": dead.get("layer", ""),
                "mechanism": dead.get("mechanism", ""),
                "measurement": dead.get("what_was_measured", ""),
                "reopen_if": dead.get("precondition_that_would_reopen", ""),
            })
    return out


STOP = set("""a an the and or of to in on for with without by from is are was were be been
this that these those it its as at into than then so such not no any all one two more most
only just also very same other another which who whom whose what when where why how if
before after during while every each both few many much some own than too can could would
should may might must will shall do does did done have has had having""".split())


def terms(text):
    return {w for w in re.findall(r"[a-z0-9_.$-]{3,}", (text or "").lower()) if w not in STOP}


def prior_dead_for(layer, attempts, floor=2):
    """Dead layers that share distinctive vocabulary with this one.

    Deliberately a HINT, not a filter: auto-dropping a layer because a different
    challenge closed something that reads similar is how a live layer gets
    skipped. The subagent is told what was already measured and why, and decides
    whether its own falsifier is the same one.
    """
    mine = terms(layer.get("layer", "") + " " + layer.get("first_probe", "") + " " +
                 layer.get("id", ""))
    hits = []
    for dead in attempts:
        shared = mine & terms(dead["layer"] + " " + dead["mechanism"])
        if len(shared) >= floor:
            hits.append({"from_challenge": dead["from_challenge"], "layer": dead["layer"],
                         "shared_terms": sorted(shared)[:6],
                         "measurement": dead["measurement"][:400],
                         "reopen_if": dead["reopen_if"][:240]})
    hits.sort(key=lambda h: -len(h["shared_terms"]))
    return hits[:3]


# ----------------------------------------------------------------------- brief

def run_novel_plan(source):
    proc = subprocess.run([sys.executable, NOVEL_PLAN, source, "--json"],
                          capture_output=True, text=True, timeout=300)
    if proc.returncode != 0:
        raise SystemExit("novel_plan.py failed (%d): %s" % (proc.returncode,
                                                            proc.stderr.strip()[:400]))
    return json.loads(proc.stdout)


def briefs(source, challenge=None, target=None):
    plan = run_novel_plan(source)
    attempts = load_attempts()
    out = []
    for layer in plan.get("layers", []):
        out.append({
            "layer_id": layer.get("id"),
            "layer": layer.get("layer"),
            "challenge": challenge,
            "target": target,
            "read_these_first": layer.get("files", []),
            "first_probe": layer.get("first_probe"),
            "falsifier": layer.get("falsifier"),
            "probe_ceiling": PROBE_CEILING,
            "already_measured_dead_elsewhere": prior_dead_for(layer, attempts),
            "forbidden": [
                "any write-shaped request (POST/PUT/DELETE/PATCH) -- hand it back instead",
                "calling tools/hooks.py or tools/state.py: the main thread owns the ledger",
                "claiming a bug class; return the measurement and let the machine decide",
                "reporting a timeout, a reset or an empty body as anything but transport",
            ],
            "return": "exactly the JSON from `python3 tools/subagent_fanout.py --contract`",
        })
    return {"mode": "fanout-brief", "source": plan.get("source"),
            "files_read_by_planner": plan.get("files_read"),
            "layers": len(out), "briefs": out,
            "boundaries": plan.get("boundaries", []),
            "note": "run these in parallel; each brief is independent by construction, "
                    "and every report comes back through --validate before it counts"}



# ---------------------------------------------------------------- web families

TAXONOMY = os.path.join(ROOT, "knowledge", "bug-classes.json")
# One family per subagent under .claude/agents/. The grouping is by PROBE, not by
# name: two classes belong together when the same first probe distinguishes them,
# which is why sqli and nosqli share a family (one probe decides whether the value
# stayed a string or became an object) while xss and csrf do not share one with
# ssrf. `write_shaped` marks the family whose winning probe cannot be read-only;
# that one is proposed by the subagent and executed by the main thread.
WEB_FAMILIES = [
    {"family": "recon", "agent": "ctf-web-recon", "classes": [],
     "skills": ["skills/web-info-disclosure/SKILL.md", "skills/web-triage/SKILL.md"],
     "why_first": "the endpoint inventory every other family probes against; a missed "
                  "endpoint is the most common cause of a stuck web challenge here"},
    {"family": "bundle", "agent": "ctf-web-bundle", "classes": [],
     "skills": ["skills/web-source-map/SKILL.md"],
     "why_first": "when the front-end bundle is the only source, this IS the source read"},
    {"family": "injection", "agent": "ctf-web-injection",
     "classes": ["web-sqli", "web-nosqli", "web-command-injection", "web-ssti", "web-graphql"]},
    {"family": "objects", "agent": "ctf-web-objects",
     "classes": ["web-prototype-pollution", "web-deserialization", "web-logic-flaw"]},
    {"family": "fetch", "agent": "ctf-web-fetch",
     "classes": ["web-ssrf", "web-open-redirect", "web-request-smuggling"]},
    {"family": "files", "agent": "ctf-web-files",
     "classes": ["file-read-primitives", "web-file-upload", "web-xxe"]},
    {"family": "session", "agent": "ctf-web-session",
     "classes": ["web-auth-session", "web-oauth-sso", "web-idor"]},
    {"family": "parser", "agent": "ctf-web-parser",
     "classes": ["web-parser-differential", "web-cache-poisoning"]},
    {"family": "client", "agent": "ctf-web-client",
     "classes": ["web-xss", "web-csrf", "web-cors", "web-xs-leaks"]},
    {"family": "race", "agent": "ctf-web-race", "write_shaped": True,
     "classes": ["web-race-condition", "web-logic-flaw"]},
]
# vendored third-party code inflates a signal's apparent breadth -- 40 "matches"
# for one signal were once all a single handout's vendor/ directory -- so a
# family's reading list must not be filled with someone else's library
SKIP_DIRS = {"node_modules", "vendor", ".git", "__pycache__", "dist", "build",
             "site-packages", ".venv", "venv"}
SKIP_EXT = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".woff", ".woff2", ".ttf", ".eot",
            ".pdf", ".zip", ".gz", ".tar", ".so", ".pyc", ".map", ".min.js", ".lock"}
MAX_FILE_BYTES = 512 * 1024


def load_taxonomy():
    try:
        with open(TAXONOMY, encoding="utf-8") as fh:
            return {c["id"]: c for c in json.load(fh)["classes"]}
    except (OSError, ValueError, KeyError):
        return {}


def source_files(source):
    """Every readable text file in the handout, minus vendored third-party code."""
    out = []
    for base, dirs, files in os.walk(source):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            if any(name.endswith(e) for e in SKIP_EXT):
                continue
            path = os.path.join(base, name)
            try:
                if os.path.getsize(path) > MAX_FILE_BYTES:
                    continue
                with open(path, encoding="utf-8", errors="replace") as fh:
                    out.append((path, fh.read()))
            except OSError:
                continue
    return out


def signal_hits(files, patterns, source, cap=6):
    """file:line for each source_signal that actually fires, deduplicated."""
    hits, seen = [], set()
    for raw in patterns or []:
        try:
            rx = re.compile(raw, re.I)
        except re.error:
            continue
        for path, text in files:
            for i, line in enumerate(text.splitlines(), 1):
                if rx.search(line):
                    key = (os.path.relpath(path, source), i)
                    if key in seen:
                        continue
                    seen.add(key)
                    hits.append({"file": "%s:%d" % key, "signal": raw,
                                 "line": line.strip()[:160]})
                    break                      # one hit per file per signal is enough
            if len(hits) >= cap:
                return hits
    return hits


def web_briefs(source=None, target=None, challenge=None, write_budget=0):
    """One brief per web family, built from the taxonomy's own fields.

    This is the sweep the ten web subagents were written for. Unlike --brief, which
    splits a handout into novel_plan's generic layers, this splits it by BUG CLASS
    FAMILY, because that is what the agents under .claude/agents/ctf-web-* are
    specialised on and what decides which probe each one sends first.
    """
    tax = load_taxonomy()
    attempts = load_attempts()
    files = source_files(source) if source and os.path.isdir(source) else []

    card = None
    if source and os.path.isdir(source):
        try:
            cards = chain_match.load_chains(chain_match.CHAINS)
            text = chain_match.read_source(source)
            stats = chain_match.load_signal_stats()
            ranked = []
            for c in cards:
                if "_error" in c:
                    continue
                scored = chain_match.score_card(c, text, text.lower(), stats)
                if scored:
                    ranked.append(scored)
            ranked.sort(key=lambda r: -(r.get("match_weight") or 0.0))
            strong = [r for r in ranked if r.get("status") == "candidate"]
            if strong:
                card = {"id": strong[0]["id"], "status": strong[0]["status"],
                        "match_confidence": strong[0].get("match_confidence"),
                        "do_this_instead": "run that card's first_confirming_probe before "
                                           "sweeping: a known answer beats ten parallel "
                                           "guesses. python3 tools/chain_match.py --source "
                                           "%s --record %s" % (source, challenge or "<name>")}
        except (OSError, ValueError) as exc:
            # only real unavailability is swallowed. A broad `except Exception` here
            # reported a NameError as "chain_match unavailable", which is precisely
            # the silent-handler failure this tool refuses in a subagent's report.
            card = {"error": "chain library unreadable: %s" % exc}

    briefs = []
    for spec in WEB_FAMILIES:
        classes = []
        hits = []
        for cid in spec["classes"]:
            cls = tax.get(cid)
            if not cls:
                classes.append({"id": cid, "_missing_from_taxonomy": True})
                continue
            classes.append({
                "id": cid,
                "evidence_level": cls.get("evidence_level"),
                "verified_by": len(cls.get("verified_by") or []),
                "first_probe": cls.get("first_probe"),
                "falsifier": cls.get("falsifier"),
                "skill": cls.get("skill"),
                "blast_radius": cls.get("blast_radius"),
                "confusable_with": cls.get("confusable_with") or [],
            })
            if files:
                hits += signal_hits(files, cls.get("source_signals"), source, cap=4)
        prior = prior_dead_for({"layer": spec["family"], "id": spec["family"],
                                "first_probe": " ".join(
                                    c.get("first_probe") or "" for c in classes
                                    if isinstance(c, dict))}, attempts)
        briefs.append({
            "family": spec["family"],
            "spawn_agent": spec["agent"],
            "challenge": challenge,
            "target": target,
            "write_shaped": bool(spec.get("write_shaped")),
            "why_first": spec.get("why_first"),
            "classes": classes,
            "skills": spec.get("skills") or sorted(
                {c["skill"] for c in classes if isinstance(c, dict) and c.get("skill")}),
            "source_signals_that_fired": hits,
            "probe_ceiling": PROBE_CEILING,
            "already_measured_dead_elsewhere": prior,
            # A blanket "no writes" made every family useless past recon: measured on
            # Speednet, where register, login, devForgotPassword, resetPassword and
            # verifyTwoFactor were ALL POSTs, so no family could run a single step and
            # the solve happened with no subagent at all. The ledger rule and the
            # target rule were being enforced by one sentence; they are different.
            # The ledger rule stays absolute. The target rule becomes a budget the
            # main thread grants, with the blast radius attached.
            "write_budget": write_budget,
            # a named per-agent directory outside this repository, because two agents
            # choosing the same scratch path already destroyed each other's work here
            "workspace": os.path.join(
                os.environ.get("CTF_WORKSPACE", "/home/kali/ctf-work"), "challenges",
                challenge or "unnamed", "agents", spec["agent"]),
            "workspace_rights": "full: create, overwrite and organise anything under the "
                                "workspace root. The ctf-v2 repository is read-only for "
                                "you, and tools/hooks.py and tools/state.py are off-limits",
            "forbidden": [
                "calling tools/hooks.py or tools/state.py: the main thread owns the "
                "ledger, and parallel writers would spend the per-class probe budget",
                "claiming a bug class; return the measurement and let the machine decide",
                "reporting a timeout, a reset or an empty body as anything but transport",
                "any write beyond write_budget, and any write at all when it is 0",
                "a write that deletes, bulk-updates, or touches an object you did not "
                "create -- those come back to the main thread whatever the budget says",
            ],
            "write_rules": [
                "report EVERY write you make, with its exact request, in your report",
                "prefer a read-only oracle: omit the fields that cause a write and read "
                "what the endpoint returns",
                "keep concurrency at 1 unless the brief says otherwise, and measure any "
                "rate limiter BEFORE raising it -- a 429 at the proxy blocks every other "
                "request to the instance, not just yours",
                "clean up anything you created and say what you left behind",
            ],
            "return": "exactly the JSON from `python3 tools/subagent_fanout.py --contract`",
        })

    ordered = sorted(briefs, key=lambda b: (
        0 if b["family"] in ("recon", "bundle") else (2 if b["write_shaped"] else 1),
        -len(b["source_signals_that_fired"]), b["family"]))
    return {
        "mode": "fanout-web",
        "source": source, "target": target, "challenge": challenge,
        "files_scanned": len(files),
        "strong_chain_match": card,
        "families": len(ordered),
        "launch_order": [b["family"] for b in ordered],
        "briefs": ordered,
        "how_to_use": [
            "If strong_chain_match is set, do NOT sweep -- run that card's probe first.",
            "Spawn the read-only families in parallel; they cannot interfere with each other.",
            "A family whose source_signals_that_fired is empty is the cheapest to park, not "
            "the cheapest to run: nothing in the handout points at it.",
            "write_budget is 0 unless you pass --write-budget: with 0 every family is "
            "read-only and hands a write back. Raise it when the instance is yours and "
            "the surface past recon is write-shaped, which is the common case.",
            "Collect every report, then: --validate each, then --merge them.",
        ],
        "note": "every class field above is read from knowledge/bug-classes.json, not "
                "restated here; a class absent from the taxonomy is flagged, not invented",
    }

# -------------------------------------------------------------------- validate

def validate_report(report):
    """Return (problems, normalised). A problem is a refusal, not a warning."""
    bad = []
    if not isinstance(report, dict):
        return ["report is not a JSON object"], None
    for key in ("layer_id", "probes"):
        if key not in report:
            bad.append("missing required key %r" % key)
    probes = report.get("probes")
    if probes is None:
        probes = []
    if not isinstance(probes, list):
        bad.append("probes must be a list")
        probes = []
    outcome = report.get("falsifier_outcome")
    if outcome not in ("held", "broken", "not-measured", None):
        bad.append("falsifier_outcome %r is not held|broken|not-measured" % outcome)
    if len(probes) > PROBE_CEILING:
        bad.append("%d probes exceeds the ceiling of %d; a sixth variant of one idea "
                   "produces no new signal" % (len(probes), PROBE_CEILING))

    confirmed = []
    for i, probe in enumerate(probes, 1):
        tag = "probe %d" % i
        if not isinstance(probe, dict):
            bad.append("%s is not an object" % tag)
            continue
        verdict = probe.get("verdict")
        kind = probe.get("evidence_kind")
        transport = probe.get("transport", "ok")
        evidence = probe.get("evidence") or ""
        excerpt = probe.get("response_excerpt") or ""
        request = str(probe.get("request") or "")

        if verdict not in VERDICTS:
            bad.append("%s: verdict %r is not one of %s" % (tag, verdict, VERDICTS))
        if kind is not None and kind not in KINDS:
            bad.append("%s: evidence_kind %r is not one of %s" % (tag, kind, KINDS))
        if transport not in TRANSPORTS:
            bad.append("%s: transport %r is not one of %s" % (tag, transport, TRANSPORTS))

        # the verbatim rule, mechanically
        if evidence and excerpt and evidence not in excerpt:
            bad.append("%s: evidence is not a verbatim substring of response_excerpt -- "
                       "that is a summary, and a summary is not evidence" % tag)
        if evidence and not excerpt:
            bad.append("%s: evidence given with no response_excerpt to quote it from" % tag)

        method = request.strip().split(" ", 1)[0].upper()
        if method in WRITE_METHODS and not probe.get("write_ack"):
            bad.append("%s: write-shaped request (%s) from a subagent; hand it to the main "
                       "thread, which reads blast_radius and passes --write-ack" % (tag, method))

        if verdict == "confirms":
            if transport != "ok":
                bad.append("%s: transport %r can never confirm -- it is evidence about "
                           "availability, not about a bug" % (tag, transport))
            if kind not in ("class", "impact"):
                bad.append("%s: verdict confirms needs evidence_kind class or impact, got %r"
                           % (tag, kind))
            if not evidence.strip():
                bad.append("%s: verdict confirms with no evidence" % tag)
            if not bad:
                confirmed.append(i)
        if transport != "ok" and verdict != "inconclusive":
            bad.append("%s: transport %r must be recorded as inconclusive" % (tag, transport))

    normalised = {
        "layer_id": report.get("layer_id"),
        "challenge": report.get("challenge"),
        "class": report.get("class"),
        "probes": len(probes),
        "confirming_probes": confirmed,
        "falsifier_outcome": outcome,
        "files_read": len(report.get("files_read") or []),
        "cost_minutes": report.get("cost_minutes"),
        "conclusion_is_hypothesis": True,
    }
    return bad, normalised


def load_reports(paths):
    out = []
    for path in paths:
        try:
            with open(path, encoding="utf-8") as fh:
                out.append((path, json.load(fh)))
        except (OSError, ValueError) as exc:
            out.append((path, {"_unreadable": str(exc)}))
    return out


def merge(paths, challenge):
    """Validate every report, then print the commands the MAIN thread runs."""
    accepted, rejected, commands = [], [], []
    for path, report in load_reports(paths):
        rel = os.path.relpath(path, ROOT) if path.startswith(ROOT) else path
        if "_unreadable" in report:
            rejected.append({"report": rel, "problems": ["unreadable: " + report["_unreadable"]]})
            continue
        problems, norm = validate_report(report)
        if problems:
            rejected.append({"report": rel, "problems": problems})
            continue
        norm["report"] = rel
        accepted.append((norm, report))

    # a layer whose falsifier broke is worth the main thread's next probe; a layer
    # that held is worth recording as dead so nobody walks it twice
    def rank(pair):
        norm = pair[0]
        return (0 if norm["confirming_probes"] else 1,
                0 if norm["falsifier_outcome"] == "broken" else 1,
                norm["layer_id"] or "")

    accepted.sort(key=rank)
    for norm, report in accepted:
        name = challenge or norm["challenge"]
        if not name:
            continue
        cls = norm["class"] or "unknown"
        for i in norm["confirming_probes"]:
            probe = report["probes"][i - 1]
            commands.append(
                "python3 tools/hooks.py post-probe %s --class %s --verdict confirms "
                "--evidence-kind %s --evidence %s --request %s   "
                "# from %s; add --hypothesis-id before running" % (
                    name, cls, probe.get("evidence_kind"),
                    json.dumps(probe.get("evidence")), json.dumps(probe.get("request")),
                    norm["report"]))
        if not norm["confirming_probes"] and norm["probes"]:
            # a refutation is a measurement and is worth as much as a confirm here:
            # it is what lets the next attempt skip the layer instead of re-walking
            # it. Downgrading every non-confirming layer to `inconclusive` threw
            # that away, so emit the verdict the subagent actually measured.
            last = report["probes"][-1]
            commands.append(
                "python3 tools/hooks.py post-probe %s --class %s --verdict %s "
                "--evidence-kind %s --evidence %s   # layer %s, falsifier %s" % (
                    name, cls,
                    HOOKS_VERDICT.get(last.get("verdict") or "inconclusive", "inconclusive"),
                    last.get("evidence_kind") or "surface",
                    json.dumps(last.get("evidence") or
                               last.get("response_excerpt", "")[:200]),
                    norm["layer_id"], norm["falsifier_outcome"]))
    return {
        "mode": "fanout-merge",
        "challenge": challenge,
        "accepted": [n for n, _ in accepted],
        "rejected": rejected,
        "commands_for_the_main_thread": commands,
        "note": "this tool does not write state.json. Run the commands above, then "
                "python3 tools/decide.py <challenge> for the next action.",
        "reminder": "a layer whose falsifier HELD belongs in knowledge/attempts/ with its "
                    "measurement, or the next attempt walks it again",
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--contract", action="store_true",
                   help="print the JSON contract a subagent must return")
    g.add_argument("--brief", metavar="SOURCE",
                   help="handout directory: emit one brief per novel_plan layer")
    g.add_argument("--web", metavar="SOURCE", nargs="?", const="",
                   help="emit one brief per WEB bug-class family, one per ctf-web-* "
                        "subagent, built from the taxonomy's own first_probe and "
                        "falsifier. SOURCE is the handout directory and is optional: "
                        "without it the briefs carry no reading list")
    g.add_argument("--validate", metavar="REPORT", help="validate one subagent report")
    g.add_argument("--merge", nargs="+", metavar="REPORT",
                   help="validate several reports and emit the main thread's commands")
    ap.add_argument("--challenge", help="challenge name as tools/state.py knows it")
    ap.add_argument("--target", help="base URL, passed through into each brief")
    ap.add_argument("--write-budget", type=int, default=0, metavar="N",
                    help="how many write-shaped requests each family may send. 0 (the "
                         "default) keeps every family read-only. Raise it only after "
                         "reading the blast_radius, and only on an instance you own")
    a = ap.parse_args()

    if a.contract:
        print(json.dumps(CONTRACT, indent=2))
        return 0
    if a.brief:
        source = a.brief if os.path.isabs(a.brief) else os.path.join(ROOT, a.brief)
        if not os.path.isdir(source):
            print(json.dumps({"error": "not a directory", "source": a.brief}), file=sys.stderr)
            return 2
        print(json.dumps(briefs(source, a.challenge, a.target), indent=2, ensure_ascii=False))
        return 0
    if a.web is not None:
        source = None
        if a.web:
            source = a.web if os.path.isabs(a.web) else os.path.join(ROOT, a.web)
            if not os.path.isdir(source):
                print(json.dumps({"error": "not a directory", "source": a.web}),
                      file=sys.stderr)
                return 2
        print(json.dumps(web_briefs(source, a.target, a.challenge, a.write_budget),
                         indent=2, ensure_ascii=False))
        return 0
    if a.validate:
        try:
            with open(a.validate, encoding="utf-8") as fh:
                report = json.load(fh)
        except (OSError, ValueError) as exc:
            print(json.dumps({"accepted": False, "problems": ["unreadable: %s" % exc]}, indent=2))
            return 2
        problems, norm = validate_report(report)
        print(json.dumps({
            "accepted": not problems, "problems": problems, "normalised": norm,
            "what_this_does_not_check": "that response_excerpt is itself verbatim. "
            "The validator never sees the response, so an excerpt typed from "
            "memory passes whenever the evidence substring avoids the typo. "
            "Accepting a report is not accepting its excerpt.",
        }, indent=2, ensure_ascii=False))
        return 1 if problems else 0
    result = merge(a.merge, a.challenge)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if result["rejected"] else 0


if __name__ == "__main__":
    sys.exit(main())
