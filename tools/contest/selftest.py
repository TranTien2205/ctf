#!/usr/bin/env python3
"""Offline proof for the contest plane. No network, no subprocess, no sockets.

Built the way tools/ad/selftest.py is: it drives the pure functions directly, so
a failure here is a logic failure rather than an environment one. Every case
below exists because getting it wrong would cost places on a scoreboard, and
the docstring of each says which mistake it guards.

Run: python3 tools/contest/selftest.py
"""
import json
import os
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import board as board_mod      # noqa: E402
import triage as triage_mod    # noqa: E402
import dispatch as dispatch_mod  # noqa: E402

RESULTS = []


def check(name, condition, detail=""):
    RESULTS.append({"case": name, "ok": bool(condition), "detail": detail})
    return bool(condition)


def t_normalise_keeps_unknown_solves_unknown():
    """HTB publishes no solve count. Reading absent as zero would rank every
    HTB challenge as maximally hard, which is backwards."""
    row = board_mod.normalise({"name": "Brutus", "category": "dfir"})
    check("solves absent stays None", row["solves"] is None, repr(row["solves"]))
    row2 = board_mod.normalise({"name": "x", "solves": 0})
    check("solves zero stays zero", row2["solves"] == 0, repr(row2["solves"]))


def t_normalise_slugs_and_defaults():
    row = board_mod.normalise({"name": "The Galactic Times!"})
    check("id slugged from name", row["id"] == "the-galactic-times", row["id"])
    check("unknown category normalised", row["category"] == "unknown", row["category"])
    row2 = board_mod.normalise({"name": "y", "category": "WEB"})
    check("category lowercased", row2["category"] == "web", row2["category"])
    try:
        board_mod.normalise({"name": "z", "status": "nonsense"})
        check("bad status rejected", False, "no error raised")
    except ValueError:
        check("bad status rejected", True)
    try:
        board_mod.normalise({})
        check("nameless row rejected", False, "no error raised")
    except ValueError:
        check("nameless row rejected", True)


def t_board_path_guards():
    """Lifted from state.py:path_for, which is already correct. A board name is
    operator input at a contest and must not escape its directory."""
    for bad in ("../escape", "has space", "/abs", "", "-leading"):
        try:
            board_mod.board_path(bad)
            check("rejects %r" % bad, False, "no error raised")
        except ValueError:
            check("rejects %r" % bad, True)
    check("accepts a sane slug",
          board_mod.board_path("somectf-2026").name == "board.json")


def t_ingest_preserves_progress():
    """The case that would actually lose a contest: re-ingesting the scoreboard
    mid-event must not wipe the fact that a challenge is already solved."""
    with tempfile.TemporaryDirectory() as tmp:
        original = board_mod.ROOT
        board_mod.ROOT = Path(tmp)
        try:
            rows = [{"id": "web-01", "name": "A", "category": "web",
                     "points": 100, "solves": 5}]
            b, added, _ = board_mod.ingest("ev", rows)
            board_mod.save("ev", b)
            check("first ingest adds", added == 1, str(added))

            b = board_mod.load("ev")
            board_mod.set_fields(b, "web-01", status="solved", flag="flag{x}")
            board_mod.save("ev", b)

            # the platform now reports more solves and more points
            b2, added2, updated2 = board_mod.ingest(
                "ev", [{"id": "web-01", "name": "A", "category": "web",
                        "points": 120, "solves": 40}])
            row = b2["challenges"][0]
            check("re-ingest updates not duplicates",
                  added2 == 0 and updated2 == 1 and len(b2["challenges"]) == 1,
                  "added=%s updated=%s n=%s" % (added2, updated2,
                                                len(b2["challenges"])))
            check("solved status survives a re-ingest",
                  row["status"] == "solved", row["status"])
            check("flag survives a re-ingest", row["flag"] == "flag{x}",
                  str(row["flag"]))
            check("fresh points are taken", row["points"] == 120,
                  str(row["points"]))
            check("fresh solves are taken", row["solves"] == 40,
                  str(row["solves"]))

            b3, _, _ = board_mod.ingest(
                "ev", [{"id": "web-01", "name": "A", "category": "web"}],
                replace=True)
            check("--replace really replaces",
                  b3["challenges"][0]["status"] == "untouched",
                  b3["challenges"][0]["status"])
        finally:
            board_mod.ROOT = original


def t_category_strength_reads_disk():
    """The signal must track the tree. When the crypto fleet grew from one agent
    to five, the estimate had to improve without anyone editing a constant."""
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "knowledge").mkdir()
        (root / "knowledge" / "bug-classes.json").write_text(json.dumps({
            "classes": [
                {"id": "web-sqli", "category": "web", "evidence_level": "verified",
                 "verified_by": ["a", "b"]},
                {"id": "web-cors", "category": "web", "evidence_level": "catalogue",
                 "verified_by": []},
                {"id": "file-read-primitives", "category": "web",
                 "evidence_level": "verified", "verified_by": ["c"]},
            ]}), encoding="utf-8")
        agents = root / ".claude" / "agents"
        agents.mkdir(parents=True)
        for n in ("ctf-crypto-rsa", "ctf-crypto-prng", "ctf-web-injection",
                  "ctf-recon", "ctf-killmap-scout"):
            (agents / (n + ".md")).write_text("x", encoding="utf-8")

        s = triage_mod.category_strength(root)
        check("verified counted by the class's own category field",
              s["web"]["verified_classes"] == 2,
              str(s["web"]["verified_classes"]))
        check("a web class with no web- prefix still counts",
              s["web"]["chain_cards"] == 3, str(s["web"]["chain_cards"]))
        check("catalogue classes are not counted as verified",
              s["web"]["verified_classes"] != 3)
        check("fleet counted per category",
              s["crypto"]["specialised_agents"] == 2,
              str(s["crypto"]["specialised_agents"]))
        check("generic scouts are not a category fleet",
              s["unknown"]["specialised_agents"] == 0,
              str(s["unknown"]["specialised_agents"]))


# Mirrors what category_strength() actually measures off this tree today, so a
# case written against the fixture means the same thing in production. `unknown`
# is the genuinely uncovered category and is what the no-fleet cases use.
STRENGTH = {
    "web": {"verified_classes": 20, "chain_cards": 34, "specialised_agents": 10},
    "dfir": {"verified_classes": 1, "chain_cards": 1, "specialised_agents": 8},
    "crypto": {"verified_classes": 0, "chain_cards": 0, "specialised_agents": 6},
    "pwn": {"verified_classes": 0, "chain_cards": 0, "specialised_agents": 5},
    "rev": {"verified_classes": 0, "chain_cards": 0, "specialised_agents": 4},
    "osint": {"verified_classes": 0, "chain_cards": 0, "specialised_agents": 3},
    "misc": {"verified_classes": 0, "chain_cards": 0, "specialised_agents": 2},
    "unknown": {"verified_classes": 0, "chain_cards": 0, "specialised_agents": 0},
    "__field__": {"max_solves": 50},
}


def t_estimate_orders_by_real_signals():
    card = {"id": "a", "category": "web", "points": 100,
            "chain_match": {"status": "candidate"}, "solves": None}
    nocard = {"id": "b", "category": "web", "points": 100,
              "chain_match": {"status": "none"}, "solves": None}
    weak = {"id": "c", "category": "web", "points": 100,
            "chain_match": {"status": "weak"}, "solves": None}
    nofleet = {"id": "d", "category": "rev", "points": 100,
               "chain_match": {"status": "none"}, "solves": None}

    m_card, why = triage_mod.expected_minutes(card, STRENGTH)
    m_nocard, _ = triage_mod.expected_minutes(nocard, STRENGTH)
    m_weak, _ = triage_mod.expected_minutes(weak, STRENGTH)
    m_nofleet, _ = triage_mod.expected_minutes(nofleet, STRENGTH)

    check("a strong card is the cheapest thing on the board",
          m_card < m_nocard, "%s vs %s" % (m_card, m_nocard))
    check("a weak card earns little credit",
          m_nocard * 0.6 < m_weak <= m_nocard, "%s vs %s" % (m_weak, m_nocard))
    check("no fleet costs more than a fleet",
          m_nofleet > m_nocard, "%s vs %s" % (m_nofleet, m_nocard))
    check("every estimate states its basis", why and all(isinstance(w, str) for w in why))

    many = dict(nocard, solves=50)
    few = dict(nocard, solves=1)
    m_many, _ = triage_mod.expected_minutes(many, STRENGTH)
    m_few, _ = triage_mod.expected_minutes(few, STRENGTH)
    check("many solvers means bank it sooner",
          m_many < m_few, "%s vs %s" % (m_many, m_few))
    check("estimates never go to zero or below", m_card >= 2.0, str(m_card))


def t_probability_separates_the_cheap_certainty_from_the_expensive_maybe():
    """The measured failure this function was added to fix.

    On a real demo board a 100-point challenge with 61 solves ranked EIGHTH
    while a 500-point crypto with 2 solves ranked second, because 500/26 beats
    100/11. Ranking on points-per-minute optimises the wrong thing: in a timed
    event with a few parallel slots, that ordering banks the hard maybe and
    skips the near-certain point.
    """
    easy = {"id": "e", "category": "misc", "points": 100, "solves": 50,
            "chain_match": {"status": "none"}}
    hard = {"id": "h", "category": "crypto", "points": 500, "solves": 2,
            "chain_match": {"status": "none"}}
    carded = {"id": "c", "category": "web", "points": 200, "solves": 30,
              "chain_match": {"status": "candidate"}}
    unknown = {"id": "u", "category": "web", "points": 200, "solves": None,
               "chain_match": {"status": "none"}}

    p_easy, why = triage_mod.probability_of_solving(easy, STRENGTH)
    p_hard, _ = triage_mod.probability_of_solving(hard, STRENGTH)
    p_card, _ = triage_mod.probability_of_solving(carded, STRENGTH)
    p_unknown, _ = triage_mod.probability_of_solving(unknown, STRENGTH)

    check("many solvers means a high chance", p_easy > 0.6, str(p_easy))
    check("two solvers means a low chance", p_hard < 0.35, str(p_hard))
    check("a strong card is the most certain thing on a board",
          p_card >= p_easy, "%s vs %s" % (p_card, p_easy))
    check("an unpublished solve count is neutral, not pessimistic",
          0.3 < p_unknown < 0.75, str(p_unknown))
    check("probability stays a probability",
          all(0.0 < p <= 1.0 for p in (p_easy, p_hard, p_card, p_unknown)))
    check("every probability states its basis", why and isinstance(why[0], str))

    # Same solve count, same points: the ONLY difference is that no specialised
    # agent covers the category at all. Measured today that is true of nothing
    # the taxonomy names, which is why the fixture uses `unknown`.
    no_fleet = {"id": "n", "category": "unknown", "points": 100, "solves": 50,
                "chain_match": {"status": "none"}}
    p_nofleet, _ = triage_mod.probability_of_solving(no_fleet, STRENGTH)
    check("a category with no fleet at all is discounted",
          p_nofleet < p_easy, "%s vs %s" % (p_nofleet, p_easy))

    b = {"challenges": [board_mod.normalise(easy), board_mod.normalise(hard)]}
    ordered = triage_mod.rank(b, STRENGTH, parallel_slots=1)
    check("the cheap certainty now outranks the expensive maybe",
          ordered[0]["id"] == "e", ordered[0]["id"])


def t_rank_prefers_a_known_card_over_raw_points():
    """The plan's own acceptance test: a web challenge with a strong chain card
    must outrank a higher-scoring crypto challenge with nothing behind it. If it
    does not, the weighting is wrong."""
    b = {"challenges": [
        board_mod.normalise({"id": "crypto-hard", "name": "Hard", "category": "crypto",
                             "points": 500, "solves": 2}),
        board_mod.normalise({"id": "web-known", "name": "Known", "category": "web",
                             "points": 200, "solves": 30,
                             "chain_match": {"status": "candidate", "card": "c1",
                                             "confidence": 0.8}}),
    ]}
    ordered = triage_mod.rank(b, STRENGTH, parallel_slots=1)
    check("the known card ranks first", ordered[0]["id"] == "web-known",
          ordered[0]["id"])
    check("and it is the one marked attack_now",
          ordered[0]["action"] == "attack_now", ordered[0]["action"])


def t_rank_handles_the_clock_and_terminal_states():
    b = {"challenges": [
        board_mod.normalise({"id": "done", "name": "D", "category": "web",
                             "points": 100, "status": "solved"}),
        board_mod.normalise({"id": "gone", "name": "G", "category": "web",
                             "points": 100, "status": "dead"}),
        board_mod.normalise({"id": "slow", "name": "S", "category": "rev",
                             "points": 100, "solves": 1}),
    ]}
    ordered = {e["id"]: e for e in triage_mod.rank(b, STRENGTH, minutes_left=3.0)}
    check("a solved challenge is done", ordered["done"]["action"] == "done",
          ordered["done"]["action"])
    check("a dead challenge is dropped", ordered["gone"]["action"] == "drop",
          ordered["gone"]["action"])
    check("what cannot finish before the clock is dropped, not started",
          ordered["slow"]["action"] == "drop", ordered["slow"]["action"])
    check("the drop says why",
          any("clock" in w for w in ordered["slow"]["why"]),
          str(ordered["slow"]["why"]))

    parked = {"challenges": [board_mod.normalise(
        {"id": "p", "name": "P", "category": "web", "points": 100,
         "status": "parked"})]}
    got = triage_mod.rank(parked, STRENGTH)[0]
    check("a parked challenge is offered for revival",
          got["action"] == "revive", got["action"])


def t_width_does_not_sweep_a_known_answer():
    """Ten agents rediscovering a card we already hold is the exact waste the
    7-10 minute spawn floor makes expensive."""
    w, why = dispatch_mod.width_for({"category": "web",
                                     "chain_match": "candidate"}, STRENGTH)
    check("a strong card gets width 1", w == 1, str(w))
    check("and it says why", "probe" in why.lower(), why)

    w2, _ = dispatch_mod.width_for({"category": "web", "chain_match": "none"},
                                   STRENGTH)
    check("a covered category gets a real wave",
          dispatch_mod.MIN_USEFUL_WIDTH <= w2 <= dispatch_mod.MAX_USEFUL_WIDTH,
          str(w2))
    check("width never exceeds six, because ten is a sweep not a wave",
          w2 <= 6, str(w2))

    # `unknown` is the only genuinely uncovered category now that crypto, pwn,
    # rev, osint and misc all have fleets on disk.
    w3, _ = dispatch_mod.width_for({"category": "unknown", "chain_match": "none"},
                                   STRENGTH)
    check("an uncovered category still gets the minimum useful width",
          w3 == dispatch_mod.MIN_USEFUL_WIDTH, str(w3))

    w4, _ = dispatch_mod.width_for({"category": "rev", "chain_match": "none"},
                                   STRENGTH)
    check("a four-agent fleet gets four, not the floor and not the ceiling",
          w4 == 4, str(w4))


def t_agent_cap_and_hold():
    check("cap follows min(16, cpus-2)", dispatch_mod.agent_cap(8) == 6,
          str(dispatch_mod.agent_cap(8)))
    check("cap is bounded at sixteen", dispatch_mod.agent_cap(64) == 16,
          str(dispatch_mod.agent_cap(64)))
    check("cap is never zero", dispatch_mod.agent_cap(1) == 1,
          str(dispatch_mod.agent_cap(1)))

    ranked = [{"id": "a", "name": "A", "category": "web", "action": "attack_now",
               "chain_match": "none", "expected_minutes": 18},
              {"id": "b", "name": "B", "category": "web", "action": "attack_now",
               "chain_match": "none", "expected_minutes": 18},
              {"id": "c", "name": "C", "category": "web", "action": "attack_now",
               "chain_match": "none", "expected_minutes": 18}]
    got = dispatch_mod.plan(ranked, STRENGTH, cpus=8)
    check("never commits more agents than the cap",
          got["agents_committed"] <= got["agent_cap"],
          "%s of %s" % (got["agents_committed"], got["agent_cap"]))
    check("a challenge that would only queue is held, not started",
          any(p["action"] == "hold" for p in got["plan"])
          or got["challenges_started"] == len(ranked),
          json.dumps([(p["id"], p["action"], p["width"]) for p in got["plan"]]))
    for entry in got["plan"]:
        if entry["action"] == "start":
            check("a started challenge carries real commands (%s)" % entry["id"],
                  bool(entry["commands"]), str(entry["commands"]))


def t_solver_fleets_name_agents_that_exist():
    """A plan that names a subagent which is not on disk cannot be executed, and
    naming a tool that does not exist is the one thing this repo forbids most."""
    agents = HERE.parents[1] / ".claude" / "agents"
    missing = []
    for category, fleet in dispatch_mod.SOLVER_FLEET.items():
        for name in fleet:
            if not (agents / (name + ".md")).is_file():
                missing.append("%s -> %s" % (category, name))
    check("every solver fleet member exists on disk", not missing,
          ", ".join(missing))


def t_flag_gate_is_never_delegated():
    """The one rule the speed rebuild must not break."""
    text = (HERE / "dispatch.py").read_text(encoding="utf-8")
    check("dispatch tells the main thread to run pre-flag",
          "hooks.py pre-flag" in text)
    check("dispatch forbids a subagent touching the gate",
          "do not let a subagent run tools/hooks.py" in text)
    for mod in ("board.py", "triage.py", "dispatch.py"):
        src = (HERE / mod).read_text(encoding="utf-8")
        check("%s never writes a challenge ledger" % mod,
              "challenges/" not in src.replace("challenges/<name>/state.json", "")
              or "state_mod" not in src)


def main():
    for fn in (t_normalise_keeps_unknown_solves_unknown,
               t_normalise_slugs_and_defaults,
               t_board_path_guards,
               t_ingest_preserves_progress,
               t_category_strength_reads_disk,
               t_estimate_orders_by_real_signals,
               t_probability_separates_the_cheap_certainty_from_the_expensive_maybe,
               t_rank_prefers_a_known_card_over_raw_points,
               t_rank_handles_the_clock_and_terminal_states,
               t_width_does_not_sweep_a_known_answer,
               t_agent_cap_and_hold,
               t_solver_fleets_name_agents_that_exist,
               t_flag_gate_is_never_delegated):
        try:
            fn()
        except Exception as exc:  # a crash is a failure, reported as one
            RESULTS.append({"case": fn.__name__, "ok": False,
                            "detail": "raised %s: %s" % (type(exc).__name__, exc)})

    failed = [r for r in RESULTS if not r["ok"]]
    print(json.dumps({
        "mode": "contest-selftest",
        "offline": "no network, no subprocess, no sockets; pure functions only",
        "total": len(RESULTS),
        "passed": len(RESULTS) - len(failed),
        "failed": len(failed),
        "failures": failed,
    }, ensure_ascii=False, indent=2))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
