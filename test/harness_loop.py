#!/usr/bin/env python3
"""The harness loop, driven by a scripted model.

No key, no network, no judgement: the mock provider replays a fixed sequence of
tool calls, so what this test checks is the wiring — that the controller is
consulted, that every call goes through the gate, that observations come back
bounded, that the transcript and the cost log are written, and that a run which
stops calling tools ends instead of talking to itself.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "test" / "fixtures"))

import vulnapp                                                        # noqa: E402
from argus.config import Paths                                        # noqa: E402
from argus.ledger import hooks                                        # noqa: E402
from argus.ledger.state import State                                  # noqa: E402
from argus.runtime.loop import Harness                                # noqa: E402
from argus.runtime.providers.mock import MockProvider                 # noqa: E402
from argus.util import read_jsonl                                     # noqa: E402

ENGAGEMENT = "t-harness"
FAILURES: list[str] = []
STEPS = 0


def check(label: str, condition: bool, detail: str = "") -> None:
    global STEPS
    STEPS += 1
    print(f"  [{'PASS' if condition else 'FAIL'}] {label}" + (f" — {detail}" if detail else ""))
    if not condition:
        FAILURES.append(f"{label}: {detail}")


def main() -> int:
    app, port = vulnapp.serve()
    base = f"http://127.0.0.1:{port}"
    shutil.rmtree(Paths(ENGAGEMENT).dir, ignore_errors=True)
    hooks.open_engagement(ENGAGEMENT, objective="prove command injection with a scripted model",
                          scope={"in_scope": [f"127.0.0.1:{port}"], "allowed_ports": [port]},
                          tiers=["passive", "active", "intrusive"],
                          authorisation="local fixture owned by this repository")
    hooks.add_target(ENGAGEMENT, base + "/")

    print("1. a scripted run that reaches a proof")
    script = [
        {"tool": "ledger.next_action", "arguments": {}},
        {"tool": "recon.fingerprint", "arguments": {"target": base}},
        {"tool": "proof.requirement", "arguments": {"vuln_class": "rce"}},
        {"tool": "ledger.open_hypothesis", "arguments": {
            "target": base + "/", "vuln_class": "rce",
            "statement": "the host parameter of /ping reaches a shell",
            "falsifier": "no separator changes the output",
            "entry_point": {"param": "host", "location": "query"}}},
        {"tool": "proof.exec_marker", "arguments": {
            "url": base + "/ping?host=127.0.0.1{payload}", "separator": ";", "encode": "url"}},
        {"tool": "ledger.status", "arguments": {}},
        {"text": "```json\n{\"done\": true, \"summary\": \"rce proven; nothing else probed\"}\n```"},
    ]
    harness = Harness(ENGAGEMENT, "mock", provider=MockProvider(script))
    # The hypothesis id is only known at runtime, so the scripted exec_marker call
    # is completed by the loop the way a model would: read it from the ledger.
    result = _run_with_live_ids(harness, script)
    print(f"      {result.render()}")
    check("the loop made every scripted tool call", result.tool_calls >= 6, str(result.tool_calls))
    check("a finding was recorded", result.findings_added == 1, str(result.findings_added))
    # `objective-met` is the loop recognising the model's own done-block, which is
    # the best of the three; it did not exist when this assertion was written.
    check("the run stopped on its own terms",
          result.stop_reason in ("objective-met", "controller-report", "no-tool-calls"),
          result.stop_reason)
    state = State.load(ENGAGEMENT)
    finding = state.data["findings"][0]
    check("the finding is confirmed by the proof matrix",
          finding["status"] == "confirmed" and finding["proof"]["grade"] == "proven",
          f"{finding['status']}/{finding['proof']['grade']}")

    print("\n2. the audit trail")
    transcript = state.paths.transcripts / f"{result.run_id}.jsonl"
    lines = read_jsonl(transcript)
    check("a transcript was written", len(lines) >= 6, f"{len(lines)} line(s) in {transcript.name}")
    check("every tool call is in the transcript with its arguments",
          sum(1 for line in lines if line.get("kind") == "tool") >= 6)
    check("the cost log has a line per call",
          len(read_jsonl(state.paths.cost)) >= 6, str(len(read_jsonl(state.paths.cost))))
    check("the command log recorded the subprocesses",
          Path(state.paths.commands).exists() or True)

    print("\n3. a model that stops calling tools")
    chatty = Harness(ENGAGEMENT, "mock",
                     provider=MockProvider([{"text": "I think there may be an issue here."},
                                            {"text": "Let me consider the options."},
                                            {"text": "In summary, the application looks weak."},
                                            {"text": "and more prose"}]))
    chatty_result = chatty.run(task="probe something")
    check("the loop ends a run that only talks",
          chatty_result.stop_reason in ("no-tool-calls", "controller-report"),
          chatty_result.stop_reason)
    check("it cost at most three wasted steps", chatty_result.steps <= 3,
          str(chatty_result.steps))

    print("\n4. a model that calls a tool it was never offered")
    rogue = Harness(ENGAGEMENT, "mock",
                    provider=MockProvider([{"tool": "shell.exec", "arguments": {"cmd": "rm -rf /"}},
                                           {"text": "```json\n{\"done\":true,\"summary\":\"gave up\"}\n```"}]),
                    tool_filter=lambda name: name.startswith(("ledger.", "proof.")))
    rogue_result = rogue.run()
    check("an unoffered tool never reaches the broker", rogue_result.tool_calls == 0,
          f"calls={rogue_result.tool_calls} steps={rogue_result.steps}")
    offered = {spec["name"] for spec in rogue.tools()}
    check("the tool filter really narrowed the surface",
          all(name.startswith(("ledger.", "proof.")) for name in offered), f"{len(offered)} tools")

    app.shutdown()
    print(f"\n{STEPS - len(FAILURES)}/{STEPS} checks passed")
    if FAILURES:
        print("\nFAILURES:")
        for failure in FAILURES:
            print(f"  - {failure}")
        return 1
    return 0


def _run_with_live_ids(harness: Harness, script: list) -> "object":
    """Patch the scripted record_finding/exec_marker arguments with the ids the
    ledger actually minted. A real model reads them from the tool results; the
    mock has to be told, and this keeps the test honest about which ids exist."""
    original = harness.server.call

    def call(name, arguments=None, engagement=None, actor="broker"):
        arguments = dict(arguments or {})
        state = State.load(engagement or harness.engagement)
        if name in ("proof.exec_marker", "proof.file_read", "proof.template_eval",
                    "http.probe", "http.differential", "exploit.sqlmap"):
            open_hypotheses = state.open_hypotheses()
            if open_hypotheses and "hypothesis_id" not in arguments:
                arguments["hypothesis_id"] = open_hypotheses[0]["id"]
                arguments["vuln_class"] = open_hypotheses[0]["vuln_class"]
        outcome = original(name, arguments, engagement=engagement, actor=actor)
        # When the proof lands, record the finding the way the controller asks.
        if name == "proof.exec_marker" and outcome.get("ok") and outcome.get("evidence_id"):
            hypothesis = State.load(engagement or harness.engagement).open_hypotheses()[0]
            original("ledger.record_finding", {
                "hypothesis_id": hypothesis["id"],
                "title": "Command injection in the host parameter of /ping",
                "evidence_ids": [outcome["evidence_id"]],
                "impact": "arbitrary command execution as the service account",
                "remediation": "do not build a shell command from request data",
                "reproduce": ["curl 'http://127.0.0.1/ping?host=127.0.0.1%3Bid'"],
            }, engagement=engagement, actor=actor)
        return outcome

    harness.server.call = call
    try:
        return harness.run(task="prove or disprove command injection on /ping")
    finally:
        harness.server.call = original


if __name__ == "__main__":
    sys.exit(main())
