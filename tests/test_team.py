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
