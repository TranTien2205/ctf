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
MINUTE_BUDGET = 15    # wall minutes per mechanism class before the same
FLAG_SOURCES = ("live-response", "artifact")


def load_taxonomy(path):
    try:
        with open(path, encoding="utf-8") as handle:
            return json.load(handle)
    except (OSError, ValueError):
        return {"classes": []}


def compute_budget(probes, now=None):
    """Per-class probe counts and elapsed minutes since the class was opened.

    Shared by decide.py and hooks.py so the two never disagree.
    """
    now = now if now is not None else time.time()
    table = {}
    for probe in probes:
        cls = probe.get("class") or "?"
        when = probe.get("time") or now
        entry = table.setdefault(cls, {"probes": 0, "first": when, "last": when})
        entry["probes"] += 1
        entry["first"] = min(entry["first"], when)
        entry["last"] = max(entry.get("last", when), when)
    for cls, entry in table.items():
        # Wall minutes BETWEEN the first and the last probe of the class — idle
        # time between a probe and the next decision must not accumulate.
        minutes = (entry["last"] - entry["first"]) / 60.0
        entry["minutes"] = round(minutes, 1)
        entry["exhausted"] = (entry["probes"] >= PROBE_BUDGET
                              or minutes >= MINUTE_BUDGET)
    return table


def falsified_classes(probes):
    return {p.get("class") for p in probes
            if p.get("verdict") == "falsifies" and p.get("class")}


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

    # Rule 5: budget enforcement — park and change layer.
    falsified = falsified_classes(probes)
    open_hyp = [h for h in hypotheses if h.get("status") == "open"
                and (h.get("priority") or 0) > 0]
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
            "--next '<the class first probe>'" % name,
        ]
        return result

    # Rule 6a: a confirmed hypothesis without a verified flag means the
    # exploit is proven but the flag is not yet in hand — keep exploiting
    # toward the flag instead of stopping.
    confirmed = [h for h in hypotheses
                 if h.get("status") == "confirmed"]
    if confirmed and not current.get("flag"):
        top = sorted(confirmed,
                     key=lambda h: (-(h.get("priority") or 0),
                                    h.get("time") or 0))[0]
        result["action"] = "exploit_confirmed"
        result["rationale"] = ("%s is confirmed: run the confirmed chain toward "
                               "the flag, then verify it through "
                               "hooks.py pre-flag" % (top.get("bug_class")
                                                      or top.get("name")))
        result["next_probe"] = {
            "hypothesis_id": top.get("id"),
            "class": top.get("bug_class"),
            "request": current.get("next_action")
            or "carry the confirmed primitive to the flag path the source "
               "or pipeline showed, then record the flag",
        }
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
            "python3 tools/hooks.py pre-probe %s --request '<probe request>'"
            % name,
            "<execute the probe>",
            "python3 tools/hooks.py post-probe %s --request '<probe request>' "
            "--verdict confirms|falsifies|inconclusive --evidence '<excerpt>'"
            % name,
        ]
        return result

    # Rule 8: no open hypotheses — writeup search if the name is known.
    if current.get("event_name") or current.get("challenge_name"):
        result["action"] = "search_writeup"
        result["rationale"] = ("no open hypothesis remains and the challenge "
                               "name is known; a writeup shortcut is allowed, "
                               "record that it was used")
        result["commands"] = [
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