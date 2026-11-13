"""End-to-end: ScriptedClient drives the loop on the live lab."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from argus.config import Config
from argus.llm import ScriptedClient
from argus.loop import AgentLoop


def _call(name, inp, n=0):
    return {"id": f"call_{name}_{n}", "name": name, "input": inp,
            "type": "tool_use"}


def test_truncate_result_survives_nonjson():
    """A tool impl returning bytes/a set/NaN must produce a string for
    tool_result, not raise out of the loop mid-run (fcf7d78)."""
    from argus.loop import _truncate_result
    for weird in ({"b": b"\xff"}, {"s": {1, 2}}, {"f": float("nan")},
                  "plain", 5, None):
        out = _truncate_result(weird)
        assert isinstance(out, str)


def test_compact_history_bounds_context():
    """Old tool_results compact to stubs naming their request_ids, so a long
    run stays under the context window; recent results stay verbatim."""
    from argus.loop import _compact_history, _KEEP_FULL_RESULTS
    big = json.dumps({"result": {"request_id": "r7", "data": "x" * 600}})
    msgs = [{"role": "user", "content": "seed"}]
    n = _KEEP_FULL_RESULTS + 3
    for i in range(n):
        msgs.append({"role": "assistant", "content": [
            {"type": "tool_use", "id": f"c{i}", "name": "crawl",
             "input": {}}]})
        msgs.append({"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": f"c{i}",
             "content": big.replace("r7", f"r{i}")}]})
    _compact_history(msgs)
    result_msgs = [m for m in msgs if isinstance(m["content"], list)
                   and any(b.get("type") == "tool_result"
                           for b in m["content"])]
    compacted = result_msgs[:-_KEEP_FULL_RESULTS]
    kept = result_msgs[-_KEEP_FULL_RESULTS:]
    assert len(compacted) == 3
    for m in compacted:
        stub = m["content"][0]["content"]
        assert "cleared" in stub and "rids:" in stub
    for m in kept:
        assert "xxxx" in m["content"][0]["content"]  # still verbatim
    assert "r0" in compacted[0]["content"][0]["content"]


def test_loop_records_finding_and_reports(lab_url, tmp_path):
    # probe_sqli sends: r1 baseline, r2 quote (error body), r3 true, r4 false.
    script = [
        {"tool_calls": [_call("probe_sqli", {"url": lab_url + "/item?id=1",
                                            "param": "id"})]},
        {"tool_calls": [_call("fingerprint", {"url": lab_url})]},
        {"tool_calls": [_call("crawl", {"url": lab_url, "depth": 1})]},
        {"tool_calls": [_call("record_finding", {
            "title": "SQL injection in /item id",
            "severity": "high", "category": "sqli",
            "url": lab_url + "/item",
            "evidence_ids": ["r2"],
            "evidence_excerpt": "sqlite3.OperationalError",
            "description": "quote param reaches sqlite query; error channel",
            "remediation": "parameterize queries",
        })]},
        {"tool_calls": [_call("finish", {"summary": "found error-based sqli"})]},
    ]
    cfg = Config(target=lab_url, allow_private=True, session_dir=tmp_path,
                 max_turns=20, rate_rps=0)
    llm = ScriptedClient(script)
    loop = AgentLoop(cfg, llm=llm, quiet=True)
    result = loop.run()

    assert result["findings"] == 1
    assert Path(result["report"]).exists()
    report = Path(result["report"]).read_text()
    assert "SQL injection" in report
    assert "sqlite3.OperationalError" in report
    assert "GET http://127.0.0.1" in report  # transcript embedded


def test_loop_rejects_bad_evidence(lab_url, tmp_path):
    script = [
        {"tool_calls": [_call("record_finding", {
            "title": "invented", "severity": "high", "category": "x",
            "url": lab_url, "evidence_ids": ["r42"],
            "evidence_excerpt": "nothing", "description": "d",
            "remediation": "r"})]},
        {"tool_calls": [_call("finish", {"summary": "done"})]},
    ]
    cfg = Config(target=lab_url, allow_private=True, session_dir=tmp_path,
                 max_turns=10, rate_rps=0)
    result = AgentLoop(cfg, llm=ScriptedClient(script), quiet=True).run()
    assert result["findings"] == 0


def test_scope_enforced_through_loop(lab_url, tmp_path):
    script = [
        {"tool_calls": [_call("http_request",
                              {"method": "GET", "url": "https://example.org/"})]},
        {"tool_calls": [_call("finish", {"summary": "done"})]},
    ]
    cfg = Config(target=lab_url, allow_private=True, session_dir=tmp_path,
                 max_turns=10, rate_rps=0)
    loop = AgentLoop(cfg, llm=ScriptedClient(script), quiet=True)
    result = loop.run()
    # the out-of-scope call must have been refused, not sent
    assert result["requests"] == 0


def test_loop_resume_seed_carries_findings(lab_url, tmp_path):
    """--resume: the new run's seed names prior findings so the model
    builds on them instead of re-verifying."""
    from argus.session import Session
    s = Session(tmp_path, lab_url, meta={})
    rid = s.record_exchange("t", {}, {"status": 200, "body": "proof-bytes"})
    s.add_finding("Old bug", "high", "sqli", lab_url + "/item",
                  [rid], "proof-bytes", "d", "r")

    script = [{"tool_calls": [_call("finish", {"summary": "resumed"})]}]
    cfg = Config(target=lab_url, allow_private=True, session_dir=tmp_path,
                 resume=str(s.dir), max_turns=10, rate_rps=0)
    llm = ScriptedClient(script)
    result = AgentLoop(cfg, llm=llm, quiet=True).run()
    seed = llm.seen_messages[0][0]["content"]
    assert "RESUMES" in seed and "Old bug" in seed
    assert result["findings"] == 1  # prior finding still counted


def test_loop_warns_before_budget_exhaustion(lab_url, tmp_path):
    """~80% into the turn budget the loop injects an early warning so the
    model can record findings before the forced finish - measured real-LLM
    behavior was deferring record_finding until the hard stop lost them."""
    script = [{"tool_calls": [_call("note", {"text": f"turn {i}"})]}
              for i in range(8)]
    cfg = Config(target=lab_url, allow_private=True, session_dir=tmp_path,
                 max_turns=8, rate_rps=0)
    llm = ScriptedClient(script)
    result = AgentLoop(cfg, llm=llm, quiet=True).run()
    # 8 script turns + 1 extra turn granted by the exhaustion nudge
    assert llm.calls == 9
    # seen_messages shares the one growing list - scan the final state:
    # user-role strings in order are seed, then injected nudges
    user_strings = [m["content"] for m in llm.seen_messages[-1]
                    if m["role"] == "user" and isinstance(m["content"], str)]
    early = [i for i, c in enumerate(user_strings) if "Budget warning" in c]
    final = [i for i, c in enumerate(user_strings)
             if "Budget nearly exhausted" in c]
    assert early, "early budget warning never injected"
    assert final, "exhaustion nudge never injected"
    assert early[0] < final[0], "early warning must precede the forced nudge"


def test_loop_survives_keyboard_interrupt(lab_url, tmp_path):
    # Ctrl-C mid-run must still render report + return cleanly.
    class InterruptingClient(ScriptedClient):
        def chat(self, messages, tools, system):
            if self.calls == 1:
                raise KeyboardInterrupt
            return super().chat(messages, tools, system)

    script = [{"tool_calls": [_call("fingerprint", {"url": lab_url})]}]
    cfg = Config(target=lab_url, allow_private=True, session_dir=tmp_path,
                 max_turns=10, rate_rps=0)
    result = AgentLoop(cfg, llm=InterruptingClient(script),
                       quiet=True).run()
    assert result["error"] == "interrupted"
    assert Path(result["report"]).exists()


def test_loop_interrupt_during_dispatch_stops(lab_url, tmp_path):
    # Ctrl-C while a tool runs must end the loop - not fall through to
    # another llm.chat call (which would need a second Ctrl-C).
    import argus.loop as aloop
    script = [
        {"tool_calls": [_call("fingerprint", {"url": lab_url}),
                        _call("fingerprint", {"url": lab_url})]},
        {"tool_calls": [_call("finish", {"summary": "x"})]},
    ]
    llm = ScriptedClient(script)
    cfg = Config(target=lab_url, allow_private=True, session_dir=tmp_path,
                 max_turns=10, rate_rps=0)
    orig = aloop.dispatch
    calls = []

    def boom(ctx, name, args):
        calls.append(name)
        if len(calls) == 2:
            raise KeyboardInterrupt
        return orig(ctx, name, args)

    aloop.dispatch = boom
    try:
        result = AgentLoop(cfg, llm=llm, quiet=True).run()
    finally:
        aloop.dispatch = orig
    assert result["error"] == "interrupted"
    assert llm.calls == 1  # never reached a second chat turn
