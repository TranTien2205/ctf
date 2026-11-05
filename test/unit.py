#!/usr/bin/env python3
"""Offline unit checks: scope, the proof matrix, the controller, budgets, locking.

No network, no model, no fixture server. If this file fails, the toolkit is
broken; nothing above it can compensate.
"""
from __future__ import annotations

import shutil
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from argus.config import Paths                                        # noqa: E402
from argus.knowledge import playbook                                  # noqa: E402
from argus.ledger import decide, hooks                                # noqa: E402
from argus.ledger import proof as matrix                              # noqa: E402
from argus.ledger.scope import Scope, origin_of, parse_target         # noqa: E402
from argus.ledger.state import State                                  # noqa: E402
from argus.util import read_json, redact                              # noqa: E402

FAILURES: list[str] = []
COUNT = 0


def check(label: str, condition: bool, detail: str = "") -> None:
    global COUNT
    COUNT += 1
    if not condition:
        FAILURES.append(f"{label}: {detail}")
        print(f"  [FAIL] {label}" + (f" — {detail}" if detail else ""))


def section(title: str) -> None:
    print(f"\n{title}")


# --- scope -------------------------------------------------------------------

def test_scope() -> None:
    section("scope")
    check("an empty scope allows nothing", not Scope().check("http://anything/"))
    scope = Scope.from_dict({"in_scope": ["10.0.0.0/24", "*.acme.test", "http://app.test/api/"],
                             "out_of_scope": ["10.0.0.1", "admin.acme.test"],
                             "allowed_ports": [80, 443, 8080]})
    for target, expected in [("http://10.0.0.5/", True), ("10.0.0.9:8080", True),
                             ("http://10.0.0.1/", False), ("https://admin.acme.test/", False),
                             ("https://www.acme.test/x", True), ("http://acme.test/", True),
                             ("evil.test", False), ("http://10.0.0.5:9999/", False),
                             ("http://app.test/api/users", True),
                             ("notacme.test", False), ("http://xacme.test/", False)]:
        verdict = scope.check(target)
        check(f"scope: {target} -> {'allow' if expected else 'deny'}",
              bool(verdict) == expected, verdict.reason)
    check("deny wins over an in-scope match",
          not Scope.from_dict({"in_scope": ["10.0.0.0/8"],
                               "out_of_scope": ["10.1.2.3"]}).check("10.1.2.3"))
    check("a URL and a bare host resolve to one origin",
          origin_of("http://h:8080/a?b=1") == origin_of("h:8080") == "http://h:8080",
          origin_of("http://h:8080/a?b=1"))
    check("an ipv6 target parses", parse_target("[::1]:8080").host == "::1")
    check("a traversal in a hostname does not parse into a match",
          not Scope.from_dict({"in_scope": ["acme.test"]}).check("http://acme.test.evil.test/"))


# --- the proof matrix --------------------------------------------------------

def test_proof_matrix() -> None:
    section("proof matrix")
    cases = read_json(ROOT / "test" / "cases" / "proof_cases.json", {})["cases"]
    for case in cases:
        verdict = matrix.verify(case["vuln_class"], case["records"])
        expected = case["expect"]
        if expected == "proven_with_hygiene_failure":
            check(case["name"], verdict.grade == "proven"
                  and any(not c["ok"] and "minimal" in c["check"] for c in verdict.checks),
                  f"{verdict.grade}; checks={[(c['check'], c['ok']) for c in verdict.checks]}")
        else:
            check(case["name"], verdict.grade == expected,
                  f"got {verdict.grade}, missing={verdict.missing}")
    check("every class in the matrix has a requirement sentence",
          all(matrix.spec_for(name).requirement for name in matrix.classes()))
    check("every non-refused class has at least one required check",
          all(matrix.spec_for(name).required_checks for name in matrix.classes()
              if matrix.spec_for(name).verifier is not matrix.verify_refused))
    check("the marker command reads identity and echoes the nonce, and does nothing else",
          matrix.marker_command("argusX") == "id; echo argusX", matrix.marker_command("argusX"))
    check("two nonces never collide", len({matrix.nonce() for _ in range(200)}) == 200)
    # A ladder may exist for a candidate-only shape such as `version-cve`, whose
    # whole point is that it ends by telling you to prove the class it implies.
    unknown = [name for name in playbook.known_classes()
               if not matrix.spec_for(name) and name not in matrix.CANDIDATE_ONLY]
    check("every playbook class is provable or explicitly candidate-only", not unknown,
          str(unknown))
    for name in playbook.known_classes():
        proof_step = playbook.proof_step(name)
        check(f"playbook {name} has a step that can satisfy the requirement",
              proof_step is not None or name == "version-cve",
              "no step carries `proves`")


# --- redaction ---------------------------------------------------------------

def test_redaction() -> None:
    section("redaction")
    samples = {"sk-ant-" + "a" * 30: "sk-ant-REDACTED",
               "AKIAIOSFODNN7EXAMPLE": "AKIA-REDACTED",
               "ghp_" + "b" * 36: "ghp-REDACTED",
               "AIza" + "c" * 35: "AIza-REDACTED"}
    for raw, expected in samples.items():
        check(f"redaction hides {expected}", expected in redact(f"token={raw}"), redact(raw))


# --- the controller ----------------------------------------------------------

def test_controller() -> None:
    section("controller")
    name = "t-unit-controller"
    shutil.rmtree(Paths(name).dir, ignore_errors=True)
    check("the controller asks for an engagement before anything",
          decide.decide(name).action == "open_engagement")
    hooks.open_engagement(name, "unit", {"in_scope": ["127.0.0.1"], "allowed_ports": [9]},
                          tiers=["passive", "active", "intrusive"], authorisation="unit test")
    check("then a target", decide.decide(name).action == "add_target")
    hooks.add_target(name, "http://127.0.0.1:9/")
    action = decide.decide(name)
    check("then recon, at the first unrun ladder step",
          action.action == "recon" and action.step == "host-liveness",
          f"{action.action}/{action.step}")
    for step in [s["step"] for s in playbook.recon_ladder()]:
        hooks.post_probe(name, "recon", "recon", "http://127.0.0.1:9/", "unit", ["x"], "signal",
                         step=step, evidence={"stdout_span": "."})
    state = State.load(name)
    state.add_surface("http://127.0.0.1:9/", "param", "id")
    state.save()
    check("then classify, because surface exists with no hypothesis",
          decide.decide(name).action == "classify", decide.decide(name).action)
    state = State.load(name)
    hypothesis = state.add_hypothesis("http://127.0.0.1:9/", "sqli", "id is concatenated",
                                      {"param": "id"}, falsifier="a quote changes nothing")
    state.save()
    action = decide.decide(name)
    check("then probe, at the cheapest unrun rung",
          action.action == "probe" and action.step == "quote-differential",
          f"{action.action}/{action.step}")
    hooks.post_probe(name, hypothesis["id"], "sqli", "http://127.0.0.1:9/", "sqlmap", ["x"],
                     "signal", step="sqlmap-confirm", evidence={"extracted": {"dbms": "SQLite"}})
    action = decide.decide(name)
    check("partial evidence becomes a named proof gap",
          action.action == "close_proof_gap" and "named table read" in str(action.detail),
          f"{action.action}")
    hooks.post_probe(name, hypothesis["id"], "sqli", "http://127.0.0.1:9/", "sqlmap", ["x"],
                     "signal", step="minimal-extraction",
                     evidence={"extracted": {"dbms": "SQLite", "table": "users",
                                             "rows": [["1"]], "row_count": 1}})
    action = decide.decide(name)
    check("a met requirement becomes record_finding", action.action == "record_finding",
          action.action)
    evidence_ids = [e["id"] for e in State.load(name).data["evidence_index"]
                    if e.get("hypothesis_id") == hypothesis["id"]]
    outcome = hooks.record_finding(name, hypothesis["id"], "sqli in id", evidence_ids)
    check("the finding is recorded as confirmed", outcome.ok and "confirmed" in outcome.message,
          outcome.message)
    check("then cross_verify", decide.decide(name).action == "cross_verify",
          decide.decide(name).action)
    finding_id = State.load(name).data["findings"][0]["id"]
    hooks.cross_verify(name, finding_id, "unit", True, "re-read")
    check("then the escalation ladder", decide.decide(name).action == "escalate",
          decide.decide(name).action)
    for rung in State.load(name).data["strategies_used"] or []:
        pass
    from argus.ledger.state import LADDER
    for rung in LADDER:
        hooks.strategy(name, rung)
    check("a spent ladder ends at report", decide.decide(name).action == "report",
          decide.decide(name).action)


# --- the gate itself ---------------------------------------------------------

def test_refusals() -> None:
    section("refusals")
    name = "t-unit-refusals"
    shutil.rmtree(Paths(name).dir, ignore_errors=True)
    check("the intrusive tier needs an authorisation note",
          not hooks.open_engagement(name, "x", {"in_scope": ["127.0.0.1"]},
                                    tiers=["passive", "active", "intrusive"]))
    check("an empty scope is refused at open",
          not hooks.open_engagement(name, "x", {"in_scope": []}))
    hooks.open_engagement(name, "x", {"in_scope": ["127.0.0.1"], "allowed_ports": [9]},
                          tiers=["passive", "active"], authorisation="unit")
    hooks.add_target(name, "http://127.0.0.1:9/")
    state = State.load(name)
    hypothesis = state.add_hypothesis("http://127.0.0.1:9/", "sqli", "x")
    state.save()
    check("out of scope is refused",
          hooks.pre_probe(name, hypothesis["id"], "sqli", "http://10.9.9.9/").refusal
          == "out-of-scope")
    check("a class mismatch is refused",
          hooks.pre_probe(name, hypothesis["id"], "xss", "http://127.0.0.1:9/").refusal
          == "class-mismatch")
    check("a disabled tier is refused",
          hooks.pre_probe(name, hypothesis["id"], "sqli", "http://127.0.0.1:9/",
                          tier="intrusive").refusal == "tier-not-enabled")
    for index in range(10):
        gate = hooks.pre_probe(name, hypothesis["id"], "sqli", f"http://127.0.0.1:9/?v={index}")
        if not gate:
            break
        hooks.post_probe(name, hypothesis["id"], "sqli", f"http://127.0.0.1:9/?v={index}",
                         "unit", ["x"], "no-signal", evidence={"stdout_span": "."})
    check("the per-class budget stops repetition", gate.refusal == "budget-spent",
          f"{gate.refusal} after {index} probes")
    check("a budget refusal names the next strategy",
          bool(gate.data.get("next_strategy")), str(gate.data))
    outcome = hooks.record_finding(name, hypothesis["id"], "unproven sqli",
                                   [e["id"] for e in State.load(name).data["evidence_index"]][:1])
    check("a finding with no proof is refused", outcome.refusal == "unproven", str(outcome.refusal))
    check("falsifying without an evidence id is refused",
          hooks.falsify(name, hypothesis["id"], "ev-nonexistent", "because").refusal == "unproven")


# --- concurrency -------------------------------------------------------------

def test_locking() -> None:
    section("locking")
    name = "t-unit-lock"
    shutil.rmtree(Paths(name).dir, ignore_errors=True)
    hooks.open_engagement(name, "x", {"in_scope": ["127.0.0.1"]}, tiers=["passive", "active"])
    state = State.load(name)
    hypothesis = state.add_hypothesis("http://127.0.0.1/", "sqli", "x")
    state.save()

    def worker(index: int) -> None:
        for attempt in range(5):
            hooks.post_probe(name, hypothesis["id"], "sqli", "http://127.0.0.1/", f"t{index}",
                             ["x"], "no-signal", evidence={"stdout_span": f"{index}-{attempt}"})

    threads = [threading.Thread(target=worker, args=(index,)) for index in range(6)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    final = State.load(name)
    check("30 concurrent writes all survive", len(final.data["probes"]) == 30,
          str(len(final.data["probes"])))
    check("every write produced its evidence record", len(final.data["evidence_index"]) == 30,
          str(len(final.data["evidence_index"])))


# --- the harness plane -------------------------------------------------------

def test_runtime() -> None:
    section("runtime")
    from argus.runtime import profile as profile_mod
    from argus.runtime.context import compact
    from argus.runtime.loop import _terminal_provider_error
    from argus.runtime.providers.base import Message, parse_text_call

    for message, expected in [("opencode: Insufficient Balance (request_id: x)", True),
                              ("HTTP 402: payment required", True),
                              ("no deepseek key configured", True),
                              ("opencode is not on PATH", True),
                              ("HTTP 429: rate limited", False),
                              ("transport: timed out", False),
                              ("HTTP 503: upstream unavailable", False)]:
        check(f"terminal-error classifier: {message[:34]!r} -> {expected}",
              _terminal_provider_error(message) is expected)

    calls, done = parse_text_call('prose\n```json\n{"tool":"http.probe",'
                                  '"arguments":{"url":"http://x/"},"why":"baseline"}\n```')
    check("the text dialect recovers a fenced tool call",
          len(calls) == 1 and calls[0].name == "http.probe" and not done)
    calls, done = parse_text_call('{"done": true, "summary": "nothing left"}')
    check("the text dialect recovers an unfenced done block", not calls and bool(done))
    calls, done = parse_text_call("I would probe the id parameter next.")
    check("prose with no block is neither a call nor a done", not calls and not done)
    calls, _done = parse_text_call('```json\n{"tool":"a","arguments":{}}\n```\n'
                                   '```json\n{"tool":"b","arguments":{}}\n```')
    check("two blocks resolve to the last one", len(calls) == 1 and calls[0].name == "b",
          str([c.name for c in calls]))

    profile = profile_mod.load("claude-haiku-5-5")
    history = [Message("assistant", "step"),
               *[Message("tool", "x" * 9000, tool_call_id=str(i), name="http.probe")
                 for i in range(40)]]
    compacted, collapsed = compact(history, profile)
    total = sum(message.chars() for message in compacted)
    check("compaction brings a long transcript under the profile's budget",
          total <= profile.history_chars, f"{total} chars, {collapsed} collapsed")
    check("compaction keeps the most recent results verbatim",
          not compacted[-1].content.startswith("[collapsed]"))
    check("compaction leaves a short transcript alone",
          compact([Message("tool", "short", name="t")], profile)[1] == 0)

    for model in profile_mod.known():
        loaded = profile_mod.load(model)
        if loaded.provider == "opencode":
            check(f"profile {model} names the opencode billing route",
                  "/" in (loaded.opencode_name or ""), loaded.opencode_name or "(none)")


# --- the tool plane's scratch ------------------------------------------------

def test_tool_scratch() -> None:
    section("tool scratch")
    import os
    from argus.broker import exec as ex

    scratch = str(Path(__file__).resolve().parent.parent / "engagements" / ".scratch-check")
    previous = os.environ.get("ARGUS_TMPDIR")
    try:
        os.environ["ARGUS_TMPDIR"] = scratch
        result = ex.run(["env"])
        lines = dict(line.split("=", 1) for line in result.stdout.splitlines() if "=" in line)
        for name in ("TMPDIR", "TMP", "TEMP"):
            check(f"a tool's {name} points at ARGUS_TMPDIR", lines.get(name) == scratch,
                  str(lines.get(name)))
        check("the scratch directory is created rather than assumed",
              Path(scratch).is_dir())
        for leaked in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "DEEPSEEK_API_KEY",
                       "GEMINI_API_KEY"):
            check(f"a tool never sees {leaked}", leaked not in lines)
    finally:
        if previous is None:
            os.environ.pop("ARGUS_TMPDIR", None)
        else:
            os.environ["ARGUS_TMPDIR"] = previous
        shutil.rmtree(scratch, ignore_errors=True)
    # The override has to be cleared for this one rather than assumed absent.
    # The gate is run with ARGUS_TMPDIR set whenever /tmp is a tmpfs small enough
    # for sqlmap to fill, which is the case this feature exists for, and reading
    # the live environment made the gate fail on the very machine that needs it.
    override = os.environ.pop("ARGUS_TMPDIR", None)
    try:
        inherited = os.environ.get("TMPDIR", "")
        result = ex.run(["env"])
        lines = dict(line.split("=", 1) for line in result.stdout.splitlines() if "=" in line)
        check("without the override a tool keeps the inherited temp directory",
              lines.get("TMPDIR", inherited) == inherited,
              f"{lines.get('TMPDIR')} vs {inherited or '(unset)'}")
    finally:
        if override is not None:
            os.environ["ARGUS_TMPDIR"] = override


# --- openbot as the coordination plane ---------------------------------------

def test_openbot_fleet() -> None:
    """OpenBot coordinates; this repository still decides what counts.

    Nothing here needs the app running: what is checked is the mapping between an
    OpenBot agent and an argus role, the exit-code vocabulary the dispatcher
    branches on, and that an unreachable control server is reported as a reason
    rather than as an empty fleet.
    """
    section("openbot fleet")
    from argus.orchestrator import openbot

    ready, why = openbot.automation_ready()
    check("an unreachable control server explains itself", bool(why.strip()), why[:90])
    if not ready:
        check("and names the files it looked for",
              "automation" in why or "PATH" in why, why[:90])

    # An agent is matched to an argus profile by either spelling of its model,
    # because the profile is the only place that holds both.
    agent = openbot.OpenBotAgent(id="a1", name="Flash",
                                 model="opencode-go/deepseek-v4.1-flash")
    check("an agent maps to the argus model by its opencode route",
          agent.argus_model == "deepseek-flash", agent.argus_model or "(none)")
    check("and inherits that model's roles",
          "executor" in agent.roles(), str(agent.roles()))
    pinned = openbot.OpenBotAgent(id="a2", name="Leader", model="claude-opus-5-5")
    check("an agent maps by the argus id as well",
          pinned.argus_model == "claude-opus-5-5", pinned.argus_model or "(none)")
    check("the planner agent is offered the planner role",
          "planner" in pinned.roles(), str(pinned.roles()))
    unknown = openbot.OpenBotAgent(id="a3", name="Mystery", model="some/model-nobody-profiled")
    check("an agent with no profile claims no role",
          unknown.argus_model == "" and unknown.roles() == [])

    # The exit codes are the whole control vocabulary, and each one means a
    # different next move, so a wrong mapping sends work to the wrong place.
    spent = openbot.Delivery(agent="Flash", exit_code=openbot.EXIT_FAILED,
                             error="You have hit your usage limit. Resets at 14:00.")
    check("a failed turn that names a usage limit is exhaustion", spent.exhausted)
    check("and is not reported as done", not spent.ok)
    refused = openbot.Delivery(agent="Flash", exit_code=openbot.EXIT_FAILED,
                               error="the agent refused: out of scope")
    check("a failed turn that is a decision is not exhaustion", not refused.exhausted,
          refused.reason)
    waiting = openbot.Delivery(agent="Leader", exit_code=openbot.EXIT_NEEDS_PERSON)
    check("waiting for a person is neither done nor exhausted",
          not waiting.ok and not waiting.exhausted, waiting.reason)
    late = openbot.Delivery(agent="Leader", exit_code=openbot.EXIT_TIMEOUT)
    check("a timeout is work still running, not quota",
          not late.exhausted and late.reason == "timed-out", late.reason)
    gone = openbot.Delivery(agent="Leader", exit_code=openbot.EXIT_UNREACHABLE)
    check("an unreachable app is named as such", gone.reason == "openbot-unreachable",
          gone.reason)

    # This module reads the app's store and must never write it.
    source = (Path(__file__).resolve().parent.parent
              / "argus" / "orchestrator" / "openbot.py").read_text()
    check("the app's database is only ever opened read-only",
          source.count("sqlite3.connect") == source.count("mode=ro"),
          f"{source.count('sqlite3.connect')} connect vs {source.count('mode=ro')} read-only")
    for forbidden in ("insert into", "update ", "delete from", "drop table"):
        check(f"and never issues {forbidden.strip()}", forbidden not in source.lower())


# --- a dry run is a question, not a step -------------------------------------

def test_dry_run_leaves_the_plan_alone() -> None:
    """`--dry-run` once marked every task done and made the plan unrunnable.

    It wrote `status: done` plus a "would execute" result to disk, so the real
    run that followed reported "nothing left that is ready" against a plan whose
    twelve tasks had never touched a target. Routing is a question about a plan;
    a question must not consume it.
    """
    section("dry run")
    import json
    from argus.orchestrator import planner as planner_mod
    from argus.orchestrator.scheduler import Scheduler

    name = "t-unit-dry-run"
    shutil.rmtree(Paths(name).dir, ignore_errors=True)
    try:
        hooks.open_engagement(name, "dry run is side-effect free",
                              {"in_scope": ["127.0.0.1"], "allowed_ports": [9]},
                              tiers=["passive", "active"], authorisation="unit test")
        hooks.add_target(name, "http://127.0.0.1:9/")
        plan = planner_mod.deterministic_plan(name)
        before = json.dumps(plan, sort_keys=True)
        check("the plan starts with every task pending",
              all(task["status"] == "pending" for task in plan["tasks"]),
              str(sorted({task["status"] for task in plan["tasks"]})))

        summary = Scheduler(name, policy="cheap", dry_run=True, parallelism=2).run(expand=False)
        after = planner_mod.load(name)
        statuses = sorted({task["status"] for task in after["tasks"]})
        check("a dry run routes every task", summary.tasks_run == len(plan["tasks"]),
              f"{summary.tasks_run} of {len(plan['tasks'])}")
        check("a dry run calls no model and spends nothing", summary.cost_usd == 0.0,
              str(summary.cost_usd))
        check("a dry run leaves every task pending", statuses == ["pending"], str(statuses))
        check("a dry run writes no fake result",
              all(task.get("result") is None for task in after["tasks"]))
        check("a dry run leaves the plan on disk byte-identical",
              json.dumps(after, sort_keys=True) == before)
    finally:
        shutil.rmtree(Paths(name).dir, ignore_errors=True)


# --- the delegation path's tool surface --------------------------------------

def test_delegated_tool_surface() -> None:
    section("delegated tool surface")
    from argus.orchestrator.runner import (ARGUS_AGENT, OPENCODE_BUILTIN_DENY, Runner,
                                           _inherited_opencode_servers)

    name = "t-unit-delegate"
    shutil.rmtree(Paths(name).dir, ignore_errors=True)
    hooks.open_engagement(name, "delegation surface", {"in_scope": ["127.0.0.1"]},
                          tiers=["passive", "active"], authorisation="unit test")
    runner = Runner(name)

    claude_config = read_json(runner.mcp_config_claude(), {})
    servers = (claude_config.get("mcpServers") or {})
    check("the claude config registers argus and nothing else", list(servers) == ["argus"],
          str(list(servers)))

    opencode_config = read_json(runner.mcp_config_opencode(), {})
    mcp = opencode_config.get("mcp") or {}
    check("the opencode config enables argus", (mcp.get("argus") or {}).get("enabled") is True)
    # `OPENCODE_CONFIG` MERGES with the user's configuration rather than replacing
    # it: measured 2026-11-04 on opencode 1.19.5, `opencode mcp list` answered
    # with argus plus the five servers already in ~/.config/opencode. A delegated
    # agent therefore reached tools that never pass the ledger gate, which is the
    # one thing this runner exists to prevent. Each inherited server is now
    # written back disabled, and this is the check that keeps it that way.
    inherited = {server for server in _inherited_opencode_servers() if server != "argus"}
    missing = [server for server in inherited
               if (mcp.get(server) or {}).get("enabled") is not False]
    check("every inherited opencode MCP server is explicitly disabled", not missing,
          f"left enabled: {missing}" if missing else f"disabled {len(inherited)}: "
          f"{sorted(inherited)}")
    agent = (opencode_config.get("agent") or {}).get(ARGUS_AGENT) or {}
    denied = agent.get("tools") or {}
    check("the delegated opencode agent is asked to give up its own shell",
          all(denied.get(tool) is False for tool in OPENCODE_BUILTIN_DENY),
          str(denied))
    check("and the same denial is expressed as a permission",
          (agent.get("permission") or {}).get("bash") == "deny",
          str(agent.get("permission")))


def main() -> int:
    test_scope()
    test_proof_matrix()
    test_redaction()
    test_controller()
    test_refusals()
    test_locking()
    test_runtime()
    test_tool_scratch()
    test_dry_run_leaves_the_plan_alone()
    test_openbot_fleet()
    test_delegated_tool_surface()
    print(f"\n{COUNT - len(FAILURES)}/{COUNT} unit checks passed")
    if FAILURES:
        print("\nFAILURES:")
        for failure in FAILURES:
            print(f"  - {failure}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
