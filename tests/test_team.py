"""Team mode: lead queue, blackboard, role gating, exploit runner, e2e."""
from __future__ import annotations

import json
import threading
import time
from pathlib import Path

import pytest

from argus.config import Config
from argus.llm import ScriptedClient
from argus.team.board import Board
from argus.team.leads import Lead, LeadQueue
from argus.team.coordinator import TeamRun
from argus.tools import team as teamtools
from argus.tools.registry import dispatch


# ------------------------------------------------------------ LeadQueue

def test_queue_dedup_and_priority():
    q = LeadQueue()
    a = Lead(kind="endpoint", url="http://t/a?x=1", params=("x",), priority=9)
    b = Lead(kind="endpoint", url="http://t/b", priority=1)
    assert q.push(a) is True
    assert q.push(a) is False                    # duplicate dropped
    assert q.push(b) is True
    leads, closed = q.pull(max_n=5, wait_s=0)
    assert closed is False
    assert [l.url for l in leads] == ["http://t/b", "http://t/a?x=1"]  # prio first


def test_queue_close_drains():
    q = LeadQueue()
    q.push(Lead(kind="endpoint", url="http://t/a"))
    q.close()
    assert q.push(Lead(kind="endpoint", url="http://t/b")) is False  # closed: reject
    leads, closed = q.pull(wait_s=0)
    assert len(leads) == 1 and closed is False   # still has items
    leads, closed = q.pull(wait_s=0)
    assert leads == [] and closed is True        # drained + closed


def test_pull_blocks_then_wakes():
    q = LeadQueue()
    got = []

    def consumer():
        leads, closed = q.pull(wait_s=5)
        got.append((len(leads), closed))

    t = threading.Thread(target=consumer)
    t.start()
    time.sleep(0.3)
    q.push(Lead(kind="endpoint", url="http://t/x"))
    t.join(timeout=3)
    assert got == [(1, False)]


# ------------------------------------------------------------ Board

def test_board_requests_consumed_only_by_lead(ctx):
    board = Board(ctx.session)
    board.request_worker("recon-1", "exploit", "attack /api", "too much surface")
    snap = board.snapshot(consume_requests=False)
    assert len(snap["requests"]) == 1
    snap = board.snapshot(consume_requests=False)   # still there for the lead
    assert len(snap["requests"]) == 1
    snap = board.snapshot(consume_requests=True)    # lead drains
    assert len(snap["requests"]) == 1
    assert board.snapshot()["requests"] == []


def test_board_text_fields_bounded(ctx):
    """Huge worker-written strings must not bloat the lead snapshot."""
    board = Board(ctx.session)
    board.request_worker("recon-1", "exploit", "T" * 9999, "R" * 9999)
    req = board.snapshot(consume_requests=True)["requests"][0]
    assert len(req["task"]) == 2000 and len(req["reason"]) == 1000
    board.post_note("recon-1", "N" * 9999)
    assert len(board.snapshot()["notes"][-1]["text"]) == 2000


def test_emit_lead_fields_bounded(ctx):
    ctx.board = Board(ctx.session)
    ctx.agent_name = "recon-1"
    r = teamtools.emit_lead(ctx, kind="endpoint",
                            url=ctx.cfg.target + "/" + "u" * 5000,
                            params=[f"p{i}" for i in range(100)],
                            tech="t" * 2000, note="n" * 9999)
    assert r["queued"] is True
    leads, _ = ctx.board.leads.pull(max_n=1, wait_s=0)
    assert len(leads[0].url) <= 2000 and len(leads[0].note) <= 2000
    assert len(leads[0].tech) <= 500 and len(leads[0].params) <= 50


def test_board_counts_bounded(ctx):
    """A runaway worker cannot grow board state without limit."""
    board = Board(ctx.session)
    for i in range(600):
        board.post_note("w", f"n{i}")
    assert len(board.notes()) == 500
    for i in range(300):
        board.request_worker("w", "exploit", f"t{i}", "r")
    assert len(board.pending_requests()) == 200
    for i in range(210):
        board.register(f"w{i}", "recon", "t")
        board.update_agent(f"w{i}", status="done")
    board.register("fresh", "recon", "t")
    assert len(board.agents()) < 210          # finished entries pruned


def test_lead_queue_saturates(ctx):
    from argus.team.leads import Lead, LeadQueue
    q = LeadQueue()
    for i in range(10_000):
        assert q.push(Lead(kind="endpoint", url=ctx.cfg.target + f"/{i}"))
    assert not q.push(Lead(kind="endpoint", url=ctx.cfg.target + "/overflow"))
    assert q.pending == 10_000


# ------------------------------------------------------------ role gating

def test_role_tool_gate(ctx):
    ctx.allowed = frozenset({"note"})
    out = dispatch(ctx, "http_request", {"method": "GET", "url": ctx.cfg.target})
    assert "error" in out and "not available" in out["error"]
    out = dispatch(ctx, "note", {"text": "hello"})
    assert out.get("result", {}).get("ok") is True


# ------------------------------------------------------------ team tools

def test_emit_and_pull_lead(ctx):
    ctx.board = Board(ctx.session)
    ctx.agent_name = "recon-1"
    r = teamtools.emit_lead(ctx, kind="endpoint",
                            url=ctx.cfg.target + "/item?id=1",
                            params=["id"], note="sqli-shaped", priority=3)
    assert r["queued"] is True
    r2 = teamtools.emit_lead(ctx, kind="endpoint",
                             url=ctx.cfg.target + "/item?id=1", params=["id"])
    assert r2["queued"] is False                   # dedup
    ctx.agent_name = "exploit-1"
    out = teamtools.pull_leads(ctx, max_n=5, wait_s=0)
    assert out["leads"][0]["url"].endswith("/item?id=1")
    assert out["leads"][0]["params"] == ["id"]


def test_emit_lead_scope_checked(ctx):
    ctx.board = Board(ctx.session)
    out = teamtools.emit_lead(ctx, kind="endpoint", url="http://evil.example/")
    assert "error" in out


def test_team_tool_requires_board(ctx):
    ctx.board = None
    out = dispatch(ctx, "emit_lead", {"kind": "endpoint", "url": "http://x/"})
    assert "error" in out


def test_wordlist_fuzz(ctx, lab_url):
    ctx.board = Board(ctx.session)
    out = teamtools.wordlist_fuzz(ctx, base_url=lab_url,
                                  wordlist="api-paths", max_words=20)
    assert out["tested"] == 20
    paths = {h["word"] for h in out["interesting"]}
    assert "api/me" in paths or "api/data" in paths


def test_wordlist_fuzz_post_body(ctx, lab_url):
    ctx.board = Board(ctx.session)
    out = teamtools.wordlist_fuzz(
        ctx, base_url=lab_url + "/login", wordlist="usernames",
        mode="param", param="username", method="POST",
        data="username={{param}}&password=x", max_words=10)
    assert out["tested"] == 10
    sizes = {h["word"]: h["bytes"] for h in out["interesting"]}
    # lab /login answers 'Wrong password for admin' for real users and
    # 'Unknown user' otherwise - differing body sizes prove the word
    # really reached the POST body
    assert sizes["admin"] != sizes["root"], sizes


def test_run_exploit_lab(ctx, lab_url):
    ctx.board = Board(ctx.session)
    ctx.agent_name = "exploit-1"
    out = teamtools.run_exploit(ctx, "lab-auth-bypass", lab_url)
    assert out.get("proof") is True, out
    assert "role=admin" in out["output"]
    # run_id is citable evidence
    finding = ctx.session.add_finding(
        title="Auth bypass", severity="high", category="sqli",
        url=lab_url + "/login", evidence_ids=[out["run_id"]],
        evidence_excerpt="role=admin",
        description="d", remediation="r")
    assert finding["id"] == "F01"


def test_run_exploit_scope(ctx):
    ctx.board = Board(ctx.session)
    out = teamtools.run_exploit(ctx, "lab-auth-bypass", "http://evil.example")
    assert "error" in out


def test_run_exploit_args_scope(ctx, lab_url):
    """{args} is free text on the command line - a foreign URL/host in it
    must not slip past the scope guard."""
    ctx.board = Board(ctx.session)
    out = teamtools.run_exploit(ctx, "lab-auth-bypass", lab_url,
                                args="--next http://evil.example/x")
    assert "scope" in out["error"]
    out = teamtools.run_exploit(ctx, "lab-auth-bypass", lab_url,
                                args="evil.example")
    assert "scope" in out["error"]
    out = teamtools.run_exploit(ctx, "lab-auth-bypass", lab_url,
                                args="--verbose")
    assert "scope" not in out.get("error", "")


def test_run_exploit_env_scrubbed(ctx, lab_url, tmp_path, monkeypatch):
    """Exploit PoCs may come from the internet - they must not inherit
    credentials from the process environment."""
    import argus.tools.team as tt
    d = tmp_path / "envcheck"
    d.mkdir()
    (d / "manifest.json").write_text(
        '{"id":"envcheck","command":["probe.py","{target}"],'
        '"proof_marker":"ok"}')
    (d / "probe.py").write_text(
        "import os\n"
        "print('SEEN=' + os.environ.get('MY_API_KEY','<absent>'))\n"
        "print('SEEN2=' + os.environ.get('HARMLESS_NAME','<absent>'))\n"
        "print('ok')\n")
    monkeypatch.setenv("MY_API_KEY", "topsecret")
    # a declared --secret VALUE under an innocuous name must scrub too -
    # run_external already drops both name-matches and value-matches
    monkeypatch.setenv("HARMLESS_NAME", "op-login-passw0rd")
    ctx.session.secret_values.add("op-login-passw0rd")
    monkeypatch.setattr(tt, "EXPLOITS", tmp_path)
    out = tt.run_exploit(ctx, "envcheck", lab_url)
    assert out.get("proof") is True, out
    assert "SEEN=<absent>" in out["output"]
    assert "SEEN2=<absent>" in out["output"]
    assert "topsecret" not in out["output"]
    assert "op-login-passw0rd" not in out["output"]


def test_run_exploit_command_escape(ctx, lab_url, tmp_path, monkeypatch):
    """A manifest whose relative command leaves its own dir is refused."""
    import argus.tools.team as tt
    d = tmp_path / "esc"
    d.mkdir()
    (d / "manifest.json").write_text(
        '{"id":"esc","command":["../outside.py","{target}"]}')
    monkeypatch.setattr(tt, "EXPLOITS", tmp_path)
    out = tt.run_exploit(ctx, "esc", lab_url)
    assert "escapes" in out["error"]


def test_run_exploit_malformed_manifest(ctx, lab_url, tmp_path, monkeypatch):
    """A manifest with a string (not list) 'command' used to iterate the
    string char-by-char into a garbage argv (48f32a5), and an invalid
    proof_marker regex crashed run_capped AFTER the subprocess had run.
    Both must fail before anything executes."""
    import argus.tools.team as tt
    for name, manifest in (
            ("strcmd", '{"id":"strcmd","command":"echo x {target}"}'),
            ("emptycmd", '{"id":"emptycmd","command":[]}'),
            ("badmarker",
             '{"id":"badmarker","command":["p.py"],'
             '"proof_marker":"("}')):
        d = tmp_path / name
        d.mkdir()
        (d / "manifest.json").write_text(manifest)
        (d / "p.py").write_text("print('SHOULD-NOT-RUN')\n")
    monkeypatch.setattr(tt, "EXPLOITS", tmp_path)
    out = tt.run_exploit(ctx, "strcmd", lab_url)
    assert "not a non-empty list" in out["error"]
    out = tt.run_exploit(ctx, "emptycmd", lab_url)
    assert "not a non-empty list" in out["error"]
    # invalid regex is treated as absent: script runs but never 'proves'
    out = tt.run_exploit(ctx, "badmarker", lab_url)
    assert "SHOULD-NOT-RUN" in out.get("output", "")
    assert out.get("proof") is not True


# ------------------------------------------------------------ e2e team

def _tool(name, **inp):
    return {"type": "tool_use", "id": f"t{name}{time.time_ns() % 99999}",
            "name": name, "input": inp}


def test_team_e2e(tmp_path, lab_url):
    """Scripted lead+recon+exploit run a full pipeline against the lab."""
    scripts = {
        ("lead", "lead"): ScriptedClient([
            {"tool_calls": [_tool("read_board")]},
            {"tool_calls": [_tool("finish_engagement",
                                  summary="lead done")]},
        ]),
        ("recon", "recon-1"): ScriptedClient([
            {"tool_calls": [_tool("crawl", url=lab_url, depth=1)]},
            {"tool_calls": [_tool("emit_lead", kind="param",
                                  url=lab_url + "/search?q=x",
                                  params=["q"], note="reflected"),
                            _tool("emit_lead", kind="param",
                                  url=lab_url + "/item?id=1",
                                  params=["id"], note="sqli-shaped")]},
            {"tool_calls": [_tool("finish", summary="mapped")]},
        ]),
        ("exploit", "exploit-1"): ScriptedClient([
            {"tool_calls": [_tool("pull_leads", max_n=5, wait_s=10)]},
            {"tool_calls": [_tool("probe_reflection",
                                  url=lab_url + "/search?q=x", param="q")]},
            {"tool_calls": [_tool("probe_sqli",
                                  url=lab_url + "/item?id=1", param="id")]},
            {"tool_calls": [_tool("pull_leads", max_n=5, wait_s=2)]},
            {"tool_calls": [_tool("finish", summary="verified")]},
        ]),
    }

    cfg = Config(target=lab_url, allow_private=True,
                 session_dir=tmp_path, max_turns=15, max_requests=300,
                 max_time_s=120, rate_rps=0)
    team = TeamRun(cfg, llm_factory=lambda role, name: scripts[(role, name)],
                   quiet=True, n_recon=1, n_exploit=1)
    result = team.run()

    assert result["lead_error"] is None
    assert "exploit-1" in result["agents"]
    assert "recon-1" in result["agents"]
    assert result["agents"]["recon-1"]["status"] == "done"
    # exploit worker actually sent probes through the shared transcript
    assert result["requests"] > 5
    assert Path(result["report"]).exists()
    # per-agent metrics landed on the board and in summary.json
    assert result["agents"]["exploit-1"]["requests"] > 0
    assert "llm_calls" in result["agents"]["recon-1"]
    assert result["llm_calls"] >= 3
    sj = json.loads((Path(result["session_dir"]) / "summary.json")
                    .read_text(encoding="utf-8"))
    assert sj["mode"] == "team"
    assert "time_to_first_finding_s" in sj
    assert sj["llm_tokens"]["in"] >= 0
    assert "agents" in sj


def test_role_cards_reference_real_tools():
    from argus.team.cards import RECON, EXPLOIT, REPORT, LEAD
    from argus.tools.registry import TOOL_SCHEMAS
    names = {s["name"] for s in TOOL_SCHEMAS}
    for card in (RECON, EXPLOIT, REPORT, LEAD):
        assert card.tools <= names, \
            f"{card.name} card references tools without schemas"


def test_worker_crash_does_not_kill_team(tmp_path, lab_url):
    """A worker whose LLM raises inside chat() must land as a status
    entry, not propagate - the lead still drains and the run still seals
    (coordinator._run wraps loop.run)."""
    from argus.llm import ScriptedClient

    class CrashClient(ScriptedClient):
        def chat(self, messages, tools, system):
            raise RuntimeError("model endpoint exploded")

    scripts = {
        ("lead", "lead"): ScriptedClient([
            {"tool_calls": [_tool("read_board")]},
            {"tool_calls": [_tool("finish_engagement", summary="done")]},
        ]),
        ("recon", "recon-1"): CrashClient([]),
    }
    cfg = Config(target=lab_url, allow_private=True,
                 session_dir=tmp_path, max_turns=10, max_requests=100,
                 max_time_s=60, rate_rps=0)
    team = TeamRun(cfg, llm_factory=lambda role, name: scripts[(role, name)],
                   quiet=True, n_recon=1, n_exploit=0)
    result = team.run()
    assert result["lead_error"] is None
    agent = result["agents"]["recon-1"]
    assert agent["status"] == "done"
    assert "exploded" in (agent.get("error") or "")
