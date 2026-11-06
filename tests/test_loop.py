"""End-to-end: ScriptedClient drives the loop on the live lab."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from argus.config import Config
from argus.llm import ScriptedClient
from argus.loop import AgentLoop


def _call(name, inp, n=0):
    return {"id": f"call_{name}_{n}", "name": name, "input": inp,
            "type": "tool_use"}


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
