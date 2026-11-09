"""argus served over MCP: the same guards, a different driver.

Driven by argus's own MCP client (argus/mcp.py), so both halves of the
protocol are exercised against each other rather than against a mock.
"""
import json
import sys
import threading
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from argus.config import Config
from argus.mcpserver import ArgusMCPServer, WITHHELD, tool_manifest


class _Pipe:
    """A line-oriented stand-in for stdio: the test writes frames in, reads
    frames out, without a subprocess."""

    def __init__(self):
        self.inbox: list[str] = []
        self.outbox: list[str] = []

    # server side
    def __iter__(self):
        while self.inbox:
            yield self.inbox.pop(0)

    def write(self, text):
        self.outbox.append(text)

    def flush(self):
        pass

    # test side
    def send(self, msg):
        self.inbox.append(json.dumps(msg) + "\n")

    def frames(self):
        out = [json.loads(line) for line in self.outbox if line.strip()]
        self.outbox.clear()
        return out


@pytest.fixture()
def served(tmp_path, lab_url):
    pipe = _Pipe()
    cfg = Config(target=lab_url, allow_private=True, session_dir=tmp_path,
                 rate_rps=0)
    server = ArgusMCPServer(cfg, stdin=pipe, stdout=pipe)
    yield server, pipe
    server.close()


def _one(server, pipe, msg):
    pipe.send(msg)
    server.serve()
    frames = pipe.frames()
    return frames[-1] if frames else None


def test_manifest_is_mcp_shaped():
    for tool in tool_manifest():
        assert set(tool) == {"name", "description", "inputSchema"}
        assert tool["inputSchema"]["type"] == "object"
        assert tool["name"] not in WITHHELD


def test_initialize_announces_tools_and_the_contract(served):
    server, pipe = served
    reply = _one(server, pipe, {"jsonrpc": "2.0", "id": 1,
                                "method": "initialize", "params": {}})
    assert reply["result"]["serverInfo"]["name"] == "argus"
    assert reply["result"]["capabilities"]["tools"]
    # the operating contract travels with the connection: a host LLM that
    # never read argus's system prompt still gets the scope and the rules
    assert "AUTHORIZED" in reply["result"]["instructions"]
    assert "proof requirement" in reply["result"]["instructions"] or \
        "What each class has to produce" in reply["result"]["instructions"]


def test_tools_list_withholds_orchestration_and_outbound_mcp(served):
    server, pipe = served
    reply = _one(server, pipe, {"jsonrpc": "2.0", "id": 2,
                                "method": "tools/list"})
    names = {t["name"] for t in reply["result"]["tools"]}
    assert "http_request" in names and "record_finding" in names
    assert not (names & WITHHELD)


def test_a_tool_call_reaches_the_target_and_is_recorded(served, lab_url):
    server, pipe = served
    reply = _one(server, pipe, {
        "jsonrpc": "2.0", "id": 3, "method": "tools/call",
        "params": {"name": "http_request",
                   "arguments": {"method": "GET", "url": lab_url + "/"}}})
    assert reply["result"]["isError"] is False
    body = json.loads(reply["result"]["content"][0]["text"])
    assert body["status"] == 200
    # the transcript is argus's, not the host's: the exchange is on record
    assert server.session._seq == 1


def test_scope_still_refuses_an_outside_host(served):
    server, pipe = served
    reply = _one(server, pipe, {
        "jsonrpc": "2.0", "id": 4, "method": "tools/call",
        "params": {"name": "http_request",
                   "arguments": {"method": "GET", "url": "http://evil.test/"}}})
    assert reply["result"]["isError"] is True
    assert "scope" in reply["result"]["content"][0]["text"].lower()


def test_a_withheld_tool_is_refused_with_a_reason(served):
    server, pipe = served
    reply = _one(server, pipe, {
        "jsonrpc": "2.0", "id": 5, "method": "tools/call",
        "params": {"name": "spawn_worker", "arguments": {}}})
    assert reply["result"]["isError"] is True
    assert "orchestrator" in reply["result"]["content"][0]["text"]


def test_findings_are_graded_over_mcp_too(served, lab_url):
    """The point of serving instead of exporting: the host LLM gets argus's
    hands and argus's rules, including the proof matrix."""
    server, pipe = served
    pipe.send({"jsonrpc": "2.0", "id": 6, "method": "tools/call",
               "params": {"name": "probe_cmdi",
                          "arguments": {"url": lab_url + "/ping?host=127.0.0.1",
                                        "param": "host"}}})
    server.serve()
    probe = json.loads(pipe.frames()[-1]["result"]["content"][0]["text"])
    rid = probe["proof_request_id"]
    import re
    body = server.session.get_exchange(rid)["response"]["body"]
    ident = re.search(r"uid=\d+\([^)]*\)|[A-Za-z0-9_.-]+\\[A-Za-z0-9_.-]+",
                      body).group(0)
    reply = _one(server, pipe, {
        "jsonrpc": "2.0", "id": 7, "method": "tools/call",
        "params": {"name": "record_finding", "arguments": {
            "title": "OS command injection in /ping", "severity": "critical",
            "category": "rce", "url": lab_url + "/ping?host=127.0.0.1",
            "evidence_excerpt": ident, "evidence_ids": [rid],
            "description": "host reaches a shell", "remediation": "use argv"}}})
    out = json.loads(reply["result"]["content"][0]["text"])
    assert out["grade"] == "proven", out


def test_an_ungraded_claim_comes_back_with_its_missing_checks(served, lab_url):
    server, pipe = served
    pipe.send({"jsonrpc": "2.0", "id": 8, "method": "tools/call",
               "params": {"name": "http_request",
                          "arguments": {"method": "GET",
                                        "url": lab_url + "/item?id=1%27"}}})
    server.serve()
    rid = json.loads(pipe.frames()[-1]["result"]["content"][0]["text"])["request_id"]
    reply = _one(server, pipe, {
        "jsonrpc": "2.0", "id": 9, "method": "tools/call",
        "params": {"name": "record_finding", "arguments": {
            "title": "SQLi in /item", "severity": "high", "category": "sqli",
            "url": lab_url + "/item?id=1", "evidence_ids": [rid],
            "evidence_excerpt": "sqlite3.OperationalError",
            "description": "d", "remediation": "r"}}})
    out = json.loads(reply["result"]["content"][0]["text"])
    assert out["grade"] == "candidate"
    assert "the query named its target" in out["missing"]


def test_unknown_method_and_bad_frames_do_not_kill_the_server(served):
    server, pipe = served
    pipe.send({"jsonrpc": "2.0", "id": 10, "method": "does/not/exist"})
    pipe.inbox.append("{not json\n")
    pipe.send({"jsonrpc": "2.0", "id": 11, "method": "ping"})
    server.serve()
    frames = pipe.frames()
    assert frames[0]["error"]["code"] == -32601
    assert frames[1]["error"]["code"] == -32700
    assert frames[2]["result"] == {}


def test_a_notification_gets_no_reply(served):
    server, pipe = served
    pipe.send({"jsonrpc": "2.0", "method": "notifications/initialized"})
    server.serve()
    assert pipe.frames() == []
    assert server._initialized is True


def test_host_probes_for_resources_and_prompts_answer_empty(served):
    server, pipe = served
    for rid, method, key in ((12, "resources/list", "resources"),
                             (13, "prompts/list", "prompts")):
        reply = _one(server, pipe, {"jsonrpc": "2.0", "id": rid,
                                    "method": method})
        assert reply["result"][key] == []


# --- over a real subprocess, driven by argus's own MCP client ---------------

def test_round_trip_over_stdio(tmp_path, lab_url):
    """The handler tests drive the server in-process. This one spawns it the
    way a host does and speaks the wire protocol to it, so the framing itself
    is under test and not assumed."""
    from argus.mcp import MCPClient
    client = MCPClient(
        "argus-under-test",
        [sys.executable, "-m", "argus", "mcp-serve", lab_url,
         "--allow-private", "--session-dir", str(tmp_path), "--rate", "0"],
        env={"PYTHONPATH": str(Path(__file__).resolve().parent.parent)},
        timeout_s=30.0)
    try:
        names = {t["name"] for t in client.tools()}
        assert "probe_cmdi" in names and "record_finding" in names
        assert not (names & WITHHELD)
        out = client.call("http_request",
                          {"method": "GET", "url": lab_url + "/"}, timeout_s=30.0)
        payload = json.loads(out["content"][0]["text"])
        assert payload["status"] == 200
        assert payload["request_id"] == "r1"
    finally:
        client.close()


def test_a_notification_of_any_method_gets_no_reply(served):
    """A JSON-RPC notification is any message with no id, whatever its method.
    This replied to every method outside the notifications/ namespace."""
    server, pipe = served
    pipe.send({"jsonrpc": "2.0", "method": "some/other/method"})
    pipe.send({"jsonrpc": "2.0", "method": "notifications/cancelled"})
    server.serve()
    assert pipe.frames() == []


def test_board_tools_are_not_advertised(served):
    """read_board, post_board_note, emit_lead and pull_leads were in the
    manifest and can only raise outside team mode - there is no Board."""
    server, pipe = served
    reply = _one(server, pipe, {"jsonrpc": "2.0", "id": 90,
                                "method": "tools/list"})
    names = {t["name"] for t in reply["result"]["tools"]}
    for board in ("read_board", "post_board_note", "emit_lead", "pull_leads",
                  "spawn_worker", "request_worker", "list_workers",
                  "finish_engagement"):
        assert board not in names, board


def test_a_tool_level_refusal_is_reported_as_an_error(served):
    """dispatch wraps a tool's own refusal as {"result": {"error": ...}}, so
    isError read False and the host saw a success."""
    server, pipe = served
    reply = _one(server, pipe, {
        "jsonrpc": "2.0", "id": 91, "method": "tools/call",
        "params": {"name": "http_request",
                   "arguments": {"method": "GET", "url": "http://evil.test/"}}})
    assert reply["result"]["isError"] is True
    assert "scope" in reply["result"]["content"][0]["text"].lower()


def test_finish_renders_and_seals_a_served_session(served):
    """A served engagement never sealed, so `argus verify` passed a
    transcript with its tail deleted."""
    from argus.cli import main
    server, pipe = served
    _one(server, pipe, {
        "jsonrpc": "2.0", "id": 92, "method": "tools/call",
        "params": {"name": "finish", "arguments": {"summary": "served run"}}})
    names = {p.name for p in server.session.dir.iterdir()}
    assert {"report.md", "report.html", "report.sarif",
            "summary.json"} <= names
    assert main(["verify", str(server.session.dir)]) == 0
