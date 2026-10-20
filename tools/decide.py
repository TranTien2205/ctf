#!/usr/bin/env python3
"""External decision controller for one challenge.

The agent proposes; this tool decides. It reads the per-challenge state and
returns the next action. It never writes state — hooks.py owns every write.

Rules, in priority order (from PROMPT.md and HYPOTHESIS_PROTOCOL.md):

1. no state file yet            -> start_recon (at most three recon commands)
2. flag present without live    -> verify_flag (a flag-shaped string is a
   response/artifact evidence      candidate, never a flag)
3. flag present with evidence   -> record_solve (chain card + classify_solve)
4. a confirmed hypothesis has   -> reopen_confirm (confirmations only exist
   no confirming probe+evidence     through hooks.py, never self-declared)
5. a class hit 5 probes or 15   -> switch_class (park that class at priority 0
   minutes and is not falsified     and open a different class; never a sixth
                                    variant of the same idea)
6. chain candidates whose card  -> run_probe with the card's confirming probe
   probe has not run yet           (reuse before novelty)
7. no hypothesis and no probe    -> new_hypothesis (classify before probing)
   recorded yet
8. an open hypothesis exists     -> run_probe for the highest-priority one
9. no open hypothesis, a known   -> search_writeup
   challenge/event name
10. nothing left                 -> stop_report with an honest summary

Budget math is shared with hooks.py through compute_budget().
"""
import argparse
import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import state as state_mod  # noqa: E402

PROBE_BUDGET = 5      # probes per mechanism class before a forced layer switch
MINUTE_BUDGET = 15    # active minutes per mechanism class before the same
IDLE_GAP_MINUTES = 20  # a longer gap between probes is parking, not work
CHALLENGE_PROBE_BUDGET = 25   # probes across every class before a challenge-level stop
CHALLENGE_MINUTE_BUDGET = 45  # active minutes across every class, per CLAUDE.md
FLAG_SOURCES = ("live-response", "artifact")

# The escalation ladder. The budgets above still hold and tools/hooks.py still
# refuses a probe past them -- that brake is what stops an agent spending an
# afternoon on payload variants, and it is not what made this system slow.
#
# What WAS wrong is that a spent budget returned `stop_report` and the challenge
# ended while obvious strategies remained untried: a chain card never matched, a
# writeup never searched, a specialised fleet never swept, a solver never handed
# the kill map. So an exhausted budget now changes STRATEGY instead of stopping.
# `stop_report` fires only when every rung below has actually been spent.
#
# Cheapest rung first. Each has a real command behind it, and
# `tools/state.py <name> --strategy-used <rung>` records that it was spent, so
# the controller never offers the same rung twice.
ESCALATION_LADDER = ("chain_match", "reclassify", "writeup_search",
                     "novel_plan", "fanout_sweep", "solver_handoff")


def load_taxonomy(path):
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {"classes": []}


def active_minutes(times, now, charge_tail=False):
    """Minutes actually worked, not minutes since the first probe.

    The old measure was ``now - first_probe``. Because probes are never removed,
    a challenge parked on Monday and resumed on Friday came back with every class
    already past the 15-minute budget, so decide.py answered switch_class for all
    of them and state.py --revive could never be acted on: the documented
    park/revive workflow was dead exactly when it mattered. Gaps longer than
    IDLE_GAP_MINUTES are parking and are not charged.

    charge_tail counts the time since the last probe. The challenge ceiling wants
    it, because time spent thinking still belongs to the challenge. A single
    class must not: otherwise a class probed once, twenty minutes before the
    agent moved on to another class, accrues those twenty minutes and is declared
    exhausted on work that happened somewhere else.
    """
    if not times:
        return 0.0
    ordered = sorted(times)
    total = 0.0
    for earlier, later in zip(ordered, ordered[1:]):
        gap = (later - earlier) / 60.0
        if gap <= IDLE_GAP_MINUTES:
            total += gap
    if charge_tail:
        tail = (now - ordered[-1]) / 60.0
        if tail <= IDLE_GAP_MINUTES:
            total += tail
    return total


def compute_budget(probes, now=None):
    """Per-class probe counts and active minutes worked on the class.

    Shared by decide.py and hooks.py so the two never disagree.
    """
    now = now if now is not None else time.time()
    table = {}
    for probe in probes:
        cls = probe.get("class") or "?"
        when = probe.get("time") or now
        entry = table.setdefault(cls, {"probes": 0, "first": when, "times": []})
        entry["probes"] += 1
        entry["first"] = min(entry["first"], when)
        entry["times"].append(when)
    for cls, entry in table.items():
        minutes = active_minutes(entry.pop("times"), now)
        entry["minutes"] = round(minutes, 1)
        entry["exhausted"] = (entry["probes"] >= PROBE_BUDGET
                              or minutes >= MINUTE_BUDGET)
    return table


def challenge_budget(probes, now=None):
    """The budget no per-class rule can enforce.

    The per-class cap is keyed on an agent-supplied class string, so relabelling
    the class resets it: 25 web classes x 5 probes is 125 probes with nothing
    saying stop. CLAUDE.md states a 45-minute ceiling per challenge in prose and
    no code implemented it. This is that ceiling.
    """
    now = now if now is not None else time.time()
    times = [p.get("time") or now for p in probes]
    minutes = active_minutes(times, now, charge_tail=True)
    return {"probes": len(probes),
            "minutes": round(minutes, 1),
            "probe_budget": CHALLENGE_PROBE_BUDGET,
            "minute_budget": CHALLENGE_MINUTE_BUDGET,
            "exhausted": (len(probes) >= CHALLENGE_PROBE_BUDGET
                          or minutes >= CHALLENGE_MINUTE_BUDGET)}


def falsified_classes(probes):
    return {p.get("class") for p in probes
            if p.get("verdict") == "falsifies" and p.get("class")}


# The fleets that exist on disk, by category, so `fanout_sweep` names a real
# command instead of a hopeful one. Keyed on the category state.py records.
FLEET_FOR_CATEGORY = {
    "web": ("--web", "skills/web-parallel-sweep/SKILL.md"),
    "dfir": ("--dfir", "skills/dfir-parallel-sweep/SKILL.md"),
    "forensics": ("--dfir", "skills/dfir-parallel-sweep/SKILL.md"),
}

# A category whose specialised solver fleet is spawned directly rather than
# through subagent_fanout. These are the agents in .claude/agents/.
SOLVERS_FOR_CATEGORY = {
    "crypto": ["ctf-crypto-recon", "ctf-crypto-rsa", "ctf-crypto-prng",
               "ctf-crypto-ecc", "ctf-crypto-symmetric"],
    "pwn": ["ctf-pwn-triage", "ctf-pwn-stack", "ctf-pwn-format",
            "ctf-pwn-heap", "ctf-pwn-rop"],
    "rev": ["ctf-rev-triage", "ctf-rev-native", "ctf-rev-managed",
            "ctf-rev-bytecode"],
    "osint": ["ctf-osint-image", "ctf-osint-identity", "ctf-osint-infra"],
    "misc": ["ctf-misc-jail", "ctf-misc-encoding"],
}


def next_escalation(name, current, budget, falsified):
    """The cheapest strategy this challenge has not yet spent.

    Returns (rung, rationale, commands) or None when the ladder is exhausted.
    A rung is offered only when its PRECONDITION holds, so the ladder never
    suggests searching for a writeup of a challenge whose name is unknown.
    """
    spent = set(current.get("strategies_used") or [])
    category = (current.get("category") or "").lower()
    considered = current.get("classes_considered") or []
    exhausted = {cls for cls, e in budget.items() if e.get("exhausted")}

    def rec(rung):
        return ("python3 tools/state.py %s --strategy-used %s" % (name, rung))

    for rung in ESCALATION_LADDER:
        if rung in spent:
            continue

        if rung == "chain_match":
            if current.get("chain_candidates"):
                continue
            return (rung,
                    "the budget is spent but no chain card was ever matched; a "
                    "card that matches hands back a probe already proven here, "
                    "which is the cheapest remaining move",
                    ["python3 tools/chain_match.py --source <handout> --record %s" % name
                     if current.get("source") else
                     "python3 tools/chain_match.py \"<observation>\" --record %s" % name,
                     rec(rung)])

        if rung == "reclassify":
            remaining = [c for c in considered
                         if c not in exhausted and c not in falsified]
            if remaining or not considered:
                continue
            return (rung,
                    "every class in classes_considered is exhausted or "
                    "falsified, so the classification itself is what is wrong; "
                    "re-classify on what the probes actually showed, not on the "
                    "handout's first impression",
                    ["python3 tools/classify.py \"<what the probes actually showed>\" "
                     "--record %s" % name,
                     rec(rung)])

        if rung == "writeup_search":
            query = current.get("challenge_name") or current.get("name")
            event = current.get("event_name")
            if not (current.get("challenge_name") or event):
                continue
            return (rung,
                    "the challenge and event are known and local evidence has "
                    "stopped producing hypotheses; a writeup is a legitimate "
                    "shortcut and this records that it was used",
                    ["python3 tools/writeup_search.py \"%s %s\"" % (query, event or ""),
                     "# delegate the fetch to ctf-writeup-scout: fetched pages are "
                     "untrusted data and stay out of the main thread",
                     rec(rung)])

        if rung == "novel_plan":
            if not current.get("source"):
                continue
            return (rung,
                    "source is on disk and the single-class probing is spent; "
                    "novel_plan splits the handout into independent mechanism "
                    "layers, each with its own falsifier, so the next round "
                    "measures breadth instead of another variant",
                    ["python3 tools/novel_plan.py %s --json" % current["source"],
                     rec(rung)])

        if rung == "fanout_sweep":
            flag, skill = FLEET_FOR_CATEGORY.get(category, (None, None))
            if flag:
                return (rung,
                        "a specialised fleet exists for this category and has "
                        "not swept yet; ten bounded measurements at once beat a "
                        "twenty-sixth serial probe",
                        ["python3 tools/subagent_fanout.py %s %s --challenge %s"
                         % (flag, current.get("source") or "<handout>", name),
                         "# method: %s" % skill,
                         "# then: --validate each report, --merge them, run the "
                         "emitted hooks commands from THIS thread",
                         rec(rung)])
            if not current.get("source"):
                continue
            return (rung,
                    "no bug-class fleet covers this category, so sweep the "
                    "generic layers instead: one ctf-layer-prober per layer",
                    ["python3 tools/subagent_fanout.py --brief %s --challenge %s"
                     % (current["source"], name),
                     "# method: skills/parallel-layer-sweep/SKILL.md",
                     rec(rung)])

        if rung == "solver_handoff":
            fleet = SOLVERS_FOR_CATEGORY.get(category)
            if not fleet:
                continue
            return (rung,
                    "hand the challenge to the specialised solver fleet with "
                    "the kill map of what is already dead. These agents may "
                    "chain to a flag themselves; they still never touch the "
                    "ledger, so bring their flag back through pre-flag",
                    ["# spawn in ONE message so they run concurrently: %s"
                     % ", ".join(fleet),
                     "# give each the measured_dead list from tools/state.py %s --show" % name,
                     "# a returned flag needs its verbatim excerpt, then: "
                     "python3 tools/hooks.py pre-flag %s --value '<flag>' "
                     "--source live-response|artifact --evidence '<excerpt>'" % name,
                     rec(rung)])

    return None


def commands_for_parking(name, hypotheses):
    return ["python3 tools/state.py %s --hypothesis-id %s --deprioritize "
            "'budget exhausted: 5 probes or 15 minutes on this class'"
            % (name, h["id"]) for h in hypotheses]


def decide(name, taxonomy_path=None, now=None):
    now = now if now is not None else time.time()
    taxonomy = load_taxonomy(taxonomy_path or os.path.join(
        ROOT, "knowledge", "bug-classes.json"))
    first_probe = {c["id"]: c.get("first_probe")
                   for c in taxonomy.get("classes", [])}
    result = {"mode": "decide", "challenge": name,
              "rules": ["A match or a signal is a candidate, never proof.",
                        "Confirms go through tools/hooks.py with evidence.",
                        "%d probes or %d minutes on one class force a layer "
                        "switch." % (PROBE_BUDGET, MINUTE_BUDGET),
                        "A flag needs live-response or artifact evidence."]}
    try:
        path = state_mod.path_for(name)
    except ValueError as exc:
        return {"mode": "decide", "error": str(exc)}
    try:
        with open(path, encoding="utf-8") as handle:
            current = json.load(handle)
    except FileNotFoundError:
        result["action"] = "start_recon"
        result["rationale"] = "no state file: begin with minimal recon"
        result["commands"] = [
            "python3 tools/state.py %s --category <cat> --target <url>"
            % name,
            "python3 tools/classify.py --source <dir>   # white-box",
            'python3 tools/classify.py "<observation>"  # black-box',
            "python3 tools/chain_match.py \"<observation>\"",
        ]
        result["recon_rules"] = [
            "at most three commands: entry page, front-end JavaScript, stack "
            "from response headers",
            "list every endpoint the front-end calls before any payload",
            "do not scan a shared host; work only on the supplied port",
        ]
        return result

    probes = current.get("probes") or []
    hypotheses = current.get("hypotheses") or []
    budget = compute_budget(probes, now)
    result["budget"] = budget

    # Rule 2 and 3: the flag gate.
    flag = current.get("flag")
    if flag:
        if (flag.get("source") in FLAG_SOURCES and flag.get("evidence")):
            result["action"] = "record_solve"
            result["rationale"] = ("flag verified with %s evidence"
                                   % flag.get("source"))
            result["commands"] = [
                "write knowledge/chains/<id>.json, then "
                "python3 tools/validate_card.py <id>",
                "python3 tools/classify_solve.py --chain <id>",
                "python3 tools/classify_solve.py --review",
            ]
        else:
            result["action"] = "verify_flag"
            result["rationale"] = ("a flag-shaped string without live evidence "
                                   "is a candidate, not a flag; read it from a "
                                   "live response or a supplied artifact")
            result["commands"] = [
                "re-run the request that should carry the flag and record it: "
                "python3 tools/hooks.py pre-flag %s --value <flag> "
                "--source live-response --evidence '<response excerpt>'" % name,
            ]
        return result

    # Rule 4: confirmations must have come through a probe with evidence.
    unsupported = []
    for hyp in hypotheses:
        if hyp.get("status") != "confirmed":
            continue
        supporting = [p for p in probes
                      if p.get("verdict") == "confirms" and p.get("evidence")
                      and (p.get("hypothesis_id") == hyp.get("id")
                           or (hyp.get("bug_class")
                               and p.get("class") == hyp.get("bug_class")))]
        if not supporting:
            unsupported.append(hyp)
    if unsupported:
        result["action"] = "reopen_confirm"
        result["rationale"] = ("confirmed without a confirming probe carrying "
                               "evidence; a confirmation that bypassed "
                               "hooks.py is not a confirmation")
        result["commands"] = commands = [
            "python3 tools/state.py %s --hypothesis-id %s --status open "
            "--next 're-confirm through hooks.py post-probe --verdict "
            "confirms --evidence ...'" % (name, h["id"])
            for h in unsupported]
        return result

    # Rule 4b: the challenge-level ceiling. Checked before the per-class rule,
    # because once the whole budget is spent there is no layer left to switch to.
    overall = challenge_budget(probes, now)
    result["challenge_budget"] = overall
    if overall["exhausted"]:
        # The budget is spent, so no further probe of the same kind is allowed —
        # tools/hooks.py still refuses one. But a spent probe budget is not a
        # finished challenge: climb the ladder and change strategy instead.
        spent_note = (
            "challenge budget exhausted: %d probes and %.0f active minutes across "
            "%d class(es), against a ceiling of %d probes / %d minutes. Changing "
            "class does not reset it and no further probe is permitted. "
            % (overall["probes"], overall["minutes"], len(budget),
               CHALLENGE_PROBE_BUDGET, CHALLENGE_MINUTE_BUDGET))
        rung = next_escalation(name, current, budget, falsified_classes(probes))
        if rung:
            name_of_rung, why, commands = rung
            result["action"] = "escalate"
            result["escalation"] = {
                "rung": name_of_rung,
                "ladder": list(ESCALATION_LADDER),
                "spent": list(current.get("strategies_used") or []),
            }
            result["rationale"] = spent_note + "Escalating to `%s`: %s." % (
                name_of_rung, why)
            result["commands"] = commands
            return result
        result["action"] = "stop_report"
        result["rationale"] = (
            spent_note
            + "Every rung of the escalation ladder (%s) has been spent, so there "
              "is no untried strategy left. Report what was tried, the exact "
              "results and the precise blocker, then park the challenge and "
              "write the kill map so the next attempt does not re-walk it."
            % ", ".join(ESCALATION_LADDER))
        result["commands"] = [
            "python3 tools/state.py %s --show   # the ledger that goes into the report" % name,
            "# write knowledge/attempts/%s.json: every layer measured dead, with "
            "the measurement and the precondition that would reopen it" % name,
        ]
        return result

    # Rule 5: budget enforcement — park and change layer.
    falsified = falsified_classes(probes)
    open_hyp = [h for h in hypotheses if h.get("status") == "open"
                and (h.get("priority") or 0) > 0]
    unclassified = [h for h in open_hyp if not h.get("bug_class")]
    if unclassified:
        result["action"] = "classify_first"
        result["rationale"] = "an open hypothesis has no bug_class; probing is blocked until it is classified"
        result["commands"] = [
            "python3 tools/state.py %s --hypothesis-id %s --status rejected"
            % (name, h.get("id")) for h in unclassified]
        return result
    exhausted = [cls for cls, entry in budget.items()
                 if entry["exhausted"] and cls != "?"]
    switch_targets = []
    for cls in exhausted:
        if cls in falsified:
            continue
        same = [h for h in open_hyp
                if (h.get("bug_class") or "?") == cls]
        if same:
            switch_targets.extend(same)
    if switch_targets:
        result["action"] = "switch_class"
        result["rationale"] = ("probe budget exhausted on %s; park it and open "
                               "a different mechanism class — never a sixth "
                               "variant of the same idea"
                               % ", ".join(sorted({h.get("bug_class") or
                                                   "unclassified"
                                                   for h in switch_targets})))
        result["commands"] = commands_for_parking(name, switch_targets)
        considered = current.get("classes_considered") or []
        remaining = [c for c in considered
                     if c not in exhausted and c not in falsified]
        if remaining:
            nxt = remaining[0]
            result["commands"].append(
                "python3 tools/state.py %s --hypothesis '<%s hypothesis>' "
                "--next '%s'" % (name, nxt, first_probe.get(
                    nxt, "run the class's first probe from "
                    "knowledge/bug-classes.json")))
            result["next_probe"] = {"class": nxt,
                                    "request": first_probe.get(nxt)}
        else:
            result["commands"].append(
                "python3 tools/classify.py \"<fresh observation after parking>\""
                "  # no untried class left in classes_considered")
            result["rationale"] += ("; every considered class is exhausted or "
                                    "falsified, so re-classify on what the "
                                    "probes actually showed")
        return result

    # Rule 6: reuse a matching chain card before inventing a new hypothesis.
    for card in current.get("chain_candidates") or []:
        tagged = any(p.get("chain_card") == card.get("id") for p in probes)
        if not tagged:
            result["action"] = "run_probe"
            result["rationale"] = ("chain %s matched and its confirming probe "
                                   "has not run; reuse before novelty"
                                   % card.get("id"))
            result["next_probe"] = {"request": card.get("first_confirming_probe"),
                                    "chain_card": card.get("id")}
            result["commands"] = [
                "run the card's first_confirming_probe, then record it: "
                "python3 tools/hooks.py post-probe %s --request '<probe>' "
                "--verdict confirms|falsifies|inconclusive --evidence '<excerpt>' "
                "--chain-card %s" % (name, card.get("id")),
                "read the card's known_traps and blast_radius before any write",
            ]
            return result

    # Rule 6b: no card fits, but source does. Plan the layers before probing.
    #
    # Rule 6 reuses a solved chain; rule 7a says "classify, then probe". Between
    # them sat the case this system is worst at: a white-box challenge whose
    # shape nothing here has solved. The agent fell through to a single
    # classifier answer and opened one depth skill, which on a layered challenge
    # picks the last entry point rather than the gate in front of it. That is
    # how CSCV2026 routed to file upload while the chain opened at a proxy ACL.
    # novel_plan reads the source and names the layers, each with its own
    # falsifier, so the first probe tests the opener instead of the sink.
    source = current.get("source")
    if source and not probes and not current.get("chain_candidates"):
        result["action"] = "novel_plan"
        result["rationale"] = (
            "no solved chain matched and no probe has run yet, but source is "
            "recorded: inventory the layers and take the opener first. A single "
            "class answer on a layered white-box challenge opens the last sink, "
            "not the boundary that has to be crossed to reach it")
        result["commands"] = [
            "python3 tools/novel_plan.py %s --json" % source,
            "python3 tools/anomaly_map.py %s   # what the author wrote on purpose" % source,
            "python3 tools/classify.py --source %s --record %s" % (source, name),
            "python3 tools/state.py %s --hypothesis '<the opening layer>' "
            "--bug-class <class-id> --next '<that layer falsifier>'" % name,
        ]
        return result

    # Rule 7a: state exists but nothing has been hypothesised yet.
    if not open_hyp and not probes:
        result["action"] = "new_hypothesis"
        result["rationale"] = ("state exists but no hypothesis and no probe "
                               "are recorded; classify the challenge before "
                               "probing")
        result["commands"] = [
            "python3 tools/classify.py --source <dir>   # white-box",
            'python3 tools/classify.py "<observation>"  # black-box',
            'python3 tools/chain_match.py "<observation>"',
            "python3 tools/state.py %s --hypothesis '<class hypothesis>' "
            "--bug-class <class-id> --next '<the class first probe>'" % name,
        ]
        return result

    # Rule 7: highest-priority open hypothesis.
    if open_hyp:
        top = sorted(open_hyp,
                     key=lambda h: (-(h.get("priority") or 0),
                                    h.get("time") or 0))[0]
        result["action"] = "run_probe"
        result["rationale"] = "highest-priority open hypothesis"
        result["next_probe"] = {
            "hypothesis_id": top.get("id"),
            "hypothesis": top.get("name"),
            "class": top.get("bug_class"),
            "request": current.get("next_action")
            or "define the cheapest probe that distinguishes this hypothesis "
               "from its neighbours (one probe, one discriminating signal)",
        }
        result["commands"] = [
            "python3 tools/hooks.py pre-probe %s --hypothesis-id %s --class %s "
            "--request '<probe request>'" % (name, top.get("id"), top.get("bug_class")),
            "<execute the probe>",
            "python3 tools/hooks.py post-probe %s --hypothesis-id %s --class %s "
            "--request '<probe request>' --verdict confirms|falsifies|inconclusive "
            "--evidence '<excerpt>'" % (name, top.get("id"), top.get("bug_class")),
        ]
        return result

    # Rule 8: no open hypotheses — writeup search if the name is known.
    if current.get("event_name") or current.get("challenge_name"):
        result["action"] = "search_writeup"
        result["rationale"] = ("no open hypothesis remains and the challenge "
                                "name is known; search for one missing fact, "
                                "then verify it locally before acting on it")
        result["commands"] = [
            "python3 tools/search_facts.py ctf-writeup --challenge \"<challenge name>\" "
            "--event \"<event>\" --fact \"<missing solve-path fact>\" "
            "--decision \"<next probe affected>\"",
            "python3 tools/writeup_search.py \"<challenge name> <event>\"",
        ]
        return result

    # Rule 9: honest stop.
    tried = {c: budget[c]["probes"] for c in budget}
    result["action"] = "stop_report"
    result["rationale"] = ("no open hypothesis, no unprobed chain candidate, "
                           "no known challenge name; report what was tried")
    result["tried"] = tried
    result["report_rules"] = [
        "state exactly what was tried and the exact results",
        "name the precise blocker, never claim progress a probe did not produce",
    ]
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Decide the next action for one challenge from its state")
    parser.add_argument("name")
    parser.add_argument("--taxonomy", help="path to bug-classes.json")
    parser.add_argument("--now", type=float, help=argparse.SUPPRESS)
    args = parser.parse_args()
    result = decide(args.name, taxonomy_path=args.taxonomy, now=args.now)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
