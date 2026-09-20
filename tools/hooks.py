#!/usr/bin/env python3
"""Verification hooks between the agent and the challenge state.

The agent executes probes; these hooks decide whether a claim is allowed to
enter the state. They are the ONLY write path for probe verdicts, hypothesis
confirmations and flags. An agent that bypasses them produces a confirmation
decide.py will reopen.

Subcommands:

  pre-probe    guard before execution: duplicate-request churn, write-shaped
               probes, blast-radius acknowledgement
  post-probe   validate and record a probe result; verdict=confirms must
               quote the response substring that proves it, and a timeout is
               never a confirmation
  pre-confirm  a hypothesis may go to 'confirmed' only with a recorded
               confirming probe carrying evidence
  pre-flag     a flag enters the state only with a source and an evidence
               excerpt
  budget       per-class probe counts and elapsed minutes (same math as
               decide.py)

Exit codes: 0 hook passed (state written where applicable), 2 hook refused
the claim. Output is always JSON.
"""
import argparse
import json
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import state as state_mod  # noqa: E402
from decide import compute_budget, PROBE_BUDGET, MINUTE_BUDGET  # noqa: E402

VERDICTS = ("confirms", "falsifies", "inconclusive")
FLAG_SOURCES = ("live-response", "artifact")
NEVER_CONFIRMATIONS = re.compile(
    r"time.?out|timed?\s*out|connection\s*(reset|refused)|no\s+response|"
    r"empty\s+response|http[_ ]?000", re.I)
WRITE_SHAPED = re.compile(
    r"^\s*(post|put|patch|delete)\b|\b(drop|truncate|mass\s+(update|delete)|"
    r"update\s+all|delete\s+all)\b", re.I)


class Refused(Exception):
    """A hook refused the claim; the message is the reason."""


def load_state(path):
    try:
        with open(path, encoding="utf-8") as handle:
            current = json.load(handle)
    except FileNotFoundError:
        raise Refused("no state file: create it with tools/state.py first")
    except (OSError, ValueError) as exc:
        raise Refused("state unreadable: %s" % exc)
    if not isinstance(current, dict) \
            or not isinstance(current.get("probes"), list) \
            or not isinstance(current.get("hypotheses"), list):
        raise Refused("invalid state structure; hook not applied")
    return current


def emit(payload, code=0):
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return code


def hook_pre_probe(args, current, path):
    if not args.request.strip():
        raise Refused("a probe needs a request string")
    if not args.allow_repeat and any(
            p.get("request") == args.request for p in current["probes"]):
        raise Refused(
            "duplicate probe request: a new probe must change the mechanism, "
            "not the syntax; --allow-repeat exists only for a legitimate "
            "repeat such as a timing baseline")
    if WRITE_SHAPED.search(args.request) and not args.write_ack:
        raise Refused(
            "write-shaped probe: read blast_radius on the matching chain card "
            "and test on an object you created, then pass --write-ack")
    return emit({"ok": True, "hook": "pre-probe",
                 "note": "prefer a read-only oracle; omit fields that cause a "
                         "write and read what the endpoint returns"})


def hook_post_probe(args, current, path):
    if not args.request.strip():
        raise Refused("a probe needs a request string")
    if args.verdict not in VERDICTS:
        raise Refused("verdict must be one of %s" % ", ".join(VERDICTS))
    if args.verdict == "confirms":
        if not (args.evidence or "").strip():
            raise Refused(
                "verdict=confirms must quote the response substring that "
                "proves it; record inconclusive if the response showed "
                "nothing decisive")
        if NEVER_CONFIRMATIONS.search(args.evidence):
            raise Refused(
                "a timeout or a dead connection is never a confirmation; it "
                "is evidence about availability, not about the bug")
    probe = {"request": args.request,
             "result": args.result or args.verdict,
             "time": time.time(),
             "verdict": args.verdict}
    for key in ("class", "evidence", "chain_card"):
        value = getattr(args, key)
        if value:
            probe[key] = value
    if args.hypothesis_id:
        matches = [h for h in current["hypotheses"]
                   if h.get("id") == args.hypothesis_id]
        if len(matches) != 1:
            raise Refused("--hypothesis-id must identify exactly one "
                          "existing hypothesis")
        probe["hypothesis_id"] = args.hypothesis_id
    current["probes"].append(probe)
    current["updated_at"] = time.time()
    state_mod.atomic_json(path, current)
    budget = compute_budget(current["probes"])
    entry = budget.get(getattr(args, "class") or "?", {})
    payload = {"ok": True, "hook": "post-probe", "probe": probe,
               "class_budget": entry}
    if entry.get("exhausted"):
        payload["budget_exhausted"] = True
        payload["next"] = ("class hit %d probes or %d minutes; run "
                           "tools/decide.py %s and expect switch_class"
                           % (PROBE_BUDGET, MINUTE_BUDGET,
                              current.get("name") or path))
    return emit(payload)


def hook_pre_confirm(args, current, path):
    if not args.hypothesis_id:
        raise Refused("pre-confirm needs --hypothesis-id")
    matches = [h for h in current["hypotheses"]
               if h.get("id") == args.hypothesis_id]
    if len(matches) != 1:
        raise Refused("--hypothesis-id must identify exactly one hypothesis")
    hyp = matches[0]
    if hyp.get("status") != "open":
        raise Refused("only an open hypothesis can be confirmed "
                      "(current status: %s)" % hyp.get("status"))
    supporting = [p for p in current["probes"]
                  if p.get("verdict") == "confirms" and p.get("evidence")
                  and (p.get("hypothesis_id") == hyp.get("id")
                       or (hyp.get("bug_class") and
                           p.get("class") == hyp.get("bug_class")))]
    if not supporting:
        raise Refused(
            "cannot confirm without a recorded confirming probe carrying "
            "evidence: hooks.py post-probe --verdict confirms --evidence "
            "'<excerpt>' [--hypothesis-id %s]" % hyp.get("id"))
    return emit({"ok": True, "hook": "pre-confirm",
                 "supporting_probes": len(supporting),
                 "then": "python3 tools/state.py %s --hypothesis-id %s "
                         "--status confirmed"
                         % (current.get("name"), hyp.get("id"))})


def hook_pre_flag(args, current, path):
    if not (args.value or "").strip():
        raise Refused("pre-flag needs --value")
    if args.source not in FLAG_SOURCES:
        raise Refused("--source must be one of %s; a flag-shaped string "
                      "without a live source is a candidate"
                      % ", ".join(FLAG_SOURCES))
    if not (args.evidence or "").strip():
        raise Refused("pre-flag needs --evidence: the response excerpt or "
                      "artifact content the flag was read from")
    current["flag"] = {"value": args.value, "source": args.source,
                       "evidence": args.evidence, "time": time.time()}
    current["updated_at"] = time.time()
    state_mod.atomic_json(path, current)
    return emit({"ok": True, "hook": "pre-flag",
                 "next": "python3 tools/decide.py %s — expect record_solve"
                         % current.get("name")})


def hook_budget(args, current, path):
    table = compute_budget(current["probes"])
    return emit({"ok": True, "hook": "budget", "budget": table,
                 "rules": {"probes_per_class": PROBE_BUDGET,
                           "minutes_per_class": MINUTE_BUDGET}})


HOOKS = {"pre-probe": hook_pre_probe, "post-probe": hook_post_probe,
         "pre-confirm": hook_pre_confirm, "pre-flag": hook_pre_flag,
         "budget": hook_budget}


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="hook", required=True)

    pre = sub.add_parser("pre-probe")
    pre.add_argument("name")
    pre.add_argument("--request", default="")
    pre.add_argument("--allow-repeat", action="store_true")
    pre.add_argument("--write-ack", action="store_true")

    post = sub.add_parser("post-probe")
    post.add_argument("name")
    post.add_argument("--request", default="")
    post.add_argument("--verdict", required=True)
    post.add_argument("--evidence")
    post.add_argument("--result")
    post.add_argument("--class", dest="class")
    post.add_argument("--chain-card", dest="chain_card")
    post.add_argument("--hypothesis-id", dest="hypothesis_id")

    confirm = sub.add_parser("pre-confirm")
    confirm.add_argument("name")
    confirm.add_argument("--hypothesis-id", dest="hypothesis_id")

    flag = sub.add_parser("pre-flag")
    flag.add_argument("name")
    flag.add_argument("--value")
    flag.add_argument("--source")
    flag.add_argument("--evidence")

    budget = sub.add_parser("budget")
    budget.add_argument("name")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        path = state_mod.path_for(args.name)
    except ValueError as exc:
        return emit({"ok": False, "hook": args.hook, "reason": str(exc)}, 2)
    try:
        current = load_state(path)
    except Refused as exc:
        return emit({"ok": False, "hook": args.hook, "reason": str(exc)}, 2)
    try:
        return HOOKS[args.hook](args, current, path)
    except Refused as exc:
        return emit({"ok": False, "hook": args.hook, "reason": str(exc)}, 2)


if __name__ == "__main__":
    sys.exit(main())