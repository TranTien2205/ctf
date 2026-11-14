"""Team mode: lead queue, blackboard, role gating, exploit runner, e2e."""
from __future__ import annotations

import re
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
    assert q.offer(a) == ""
    assert q.offer(a) == "duplicate"             # and it says WHICH refusal
    assert q.offer(b) == ""
    leads, closed = q.pull(max_n=5, wait_s=0)
    assert closed is False
    assert [l.url for l in leads] == ["http://t/b", "http://t/a?x=1"]  # prio first


def test_queue_close_drains():
    q = LeadQueue()
    q.offer(Lead(kind="endpoint", url="http://t/a"))
    q.close()
    # a closed pipeline is NOT a duplicate: the producer must stop, not
    # go looking for different surface
    assert q.offer(Lead(kind="endpoint", url="http://t/b")) == "closed"
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
    q.offer(Lead(kind="endpoint", url="http://t/x"))
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
        assert q.offer(Lead(kind="endpoint", url=ctx.cfg.target + f"/{i}")) == ""
    # the bound being spent says nothing about this lead, and the surface
    # is not covered - reporting "duplicate" here claimed both
    assert q.offer(
        Lead(kind="endpoint", url=ctx.cfg.target + "/overflow")) == "capacity"
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
    assert r2["refusal"] == "duplicate"            # and this one really is
    ctx.agent_name = "exploit-1"
    out = teamtools.pull_leads(ctx, max_n=5, wait_s=0)
    assert out["leads"][0]["url"].endswith("/item?id=1")
    assert out["leads"][0]["params"] == ["id"]


def test_a_closed_pipeline_is_not_reported_as_a_duplicate(ctx):
    """The refusal a worker is shown decides what it does next.

    `LeadQueue` refuses a lead for three unrelated reasons - the pipeline is
    closed, the lead is a duplicate, the unique-lead bound is spent - and all
    three used to arrive at the model as "duplicate of an existing lead".

    Told "duplicate", a recon worker correctly goes looking for DIFFERENT
    surface. That is the right move for one of the three and wrong for the
    other two: against a closed pipeline it burns the worker's remaining
    turns producing leads nobody will pull, and against a spent bound it
    reports the surface as already covered when nothing about that lead was
    wrong. An operator reading the transcript saw "duplicate" either way and
    concluded recon had been thorough.
    """
    ctx.board = Board(ctx.session)
    ctx.agent_name = "recon-1"
    ctx.board.leads.close()
    out = teamtools.emit_lead(ctx, kind="endpoint",
                              url=ctx.cfg.target + "/never-pulled")
    assert out["queued"] is False
    assert out["refusal"] == "closed"
    # the prose the model actually reads must name the action, not the wrong
    # cause - "duplicate" would send it hunting for more surface instead
    assert "duplicate" not in out["reason"]
    assert "stop emitting leads" in out["reason"]


def test_a_spent_lead_bound_does_not_claim_the_surface_is_covered(ctx):
    from argus.team.leads import Lead
    ctx.board = Board(ctx.session)
    ctx.agent_name = "recon-1"
    for i in range(10_000):
        ctx.board.leads.offer(
            Lead(kind="endpoint", url=ctx.cfg.target + f"/seen/{i}"))
    out = teamtools.emit_lead(ctx, kind="endpoint",
                              url=ctx.cfg.target + "/brand-new")
    assert out["queued"] is False and out["refusal"] == "capacity"
    assert "duplicate" not in out["reason"]
    assert "NOT covered" in out["reason"]


def test_every_registered_tool_is_granted_to_some_role():
    """The direction that rots, for the tool registry this time.

    Every card's tools are checked against the registry - a card naming a
    tool that does not exist fails loudly. Nothing checked the reverse: a
    tool that exists and is in NO card is unreachable for every agent in
    team mode, and nothing says so. `next_action` was exactly that, found by
    hand: the registry had it, four cards did not, and `decide.py`'s own
    docstring named the agent as one of the ledger's two readers.

    Measured now: 56 registered tools, 56 reachable. The partition is
    satisfied, which is the cheapest moment to hold it - a new probe added
    to the registry and forgotten in `cards.py` reaches no worker, and the
    probe's absence looks exactly like a probe that found nothing.
    """
    from argus.team.cards import CARDS, LEAD
    from argus.tools import registry

    known = {t["name"] for t in registry.TOOL_SCHEMAS}
    granted = set(LEAD.tools)
    for card in CARDS.values():
        granted |= set(card.tools)

    assert known, "the registry is empty, so this test measures nothing"
    unreachable = sorted(known - granted)
    assert not unreachable, (
        f"{unreachable} exist in the registry and are in no role card, so no "
        "agent can call them in team mode. Grant each to the role that "
        "should have it, or take it out of the registry.")

    # and every granted name is a real tool, or a card is filtering on a
    # typo and silently narrowing that role
    assert granted <= known, sorted(granted - known)


def test_no_role_is_told_to_call_a_tool_its_grant_denies(ctx):
    """The shared prompt was a single-agent playbook given to four roles.

    `SYSTEM`'s numbered method is imperative - "fingerprint() the target,
    crawl() the surface", "record_finding() IMMEDIATELY", "finish() with",
    "call next_action()" - and it was rendered identically for every role
    while `dispatch` enforces the role's card. Measured before the fix:

        recon    record_finding, next_action
        exploit  crawl, fingerprint, js_recon, next_action
        report   crawl, fingerprint, js_recon, record_finding, next_action
        lead     finish, record_finding, next_action

    The grants are deliberate - recon maps, exploit proves, so only exploit
    records - and every role CARD's own prompt is consistent with its own
    grant. So the shared prompt was the wrong half, and widening the grants
    to match it would have dissolved the role separation that is the point
    of team mode.

    This test does not demand that the two sets match. It demands that the
    prompt never silently instructs what the gate denies: either the role
    can call the tool, or the prompt says out loud that it cannot and who
    does. That is derived in `_grant_block`, so it cannot drift from a card.
    """
    from argus.scope import ScopeGuard
    from argus.system import build_system
    from argus.team.cards import CARDS, LEAD
    from argus.tools import registry

    known = {t["name"] for t in registry.TOOL_SCHEMAS}
    scope = ScopeGuard(ctx.cfg.target)
    roles = [(name, card.tools) for name, card in CARDS.items()]
    roles.append(("LEAD", LEAD.tools))

    for name, grant in roles:
        rendered = build_system(ctx.cfg, scope, allowed=grant)
        named = {m for m in re.findall(r"\b([a-z_][a-z0-9_]*)\s*\(", rendered)
                 if m in known}
        assert named, (f"{name}: the rendered prompt names no tools at "
                       "all, so this test is measuring nothing")
        for tool in sorted(named - set(grant)):
            # not granted, so the prompt must say so by name
            assert "YOUR TOOLS." in rendered, (
                f"{name} is instructed to call {tool} and cannot, with no "
                "statement in the prompt that it cannot")
            disclaimer = rendered.split("YOUR TOOLS.", 1)[1]
            assert tool in disclaimer, (
                f"{name} is instructed to call {tool}, its grant denies it, "
                "and the disclaimer does not name it - so the agent spends a "
                f"turn on 'tool {tool} is not available to role'")


def test_single_agent_mode_gets_no_disclaimer_because_it_needs_none(ctx):
    """The other direction: with every tool granted, nothing is withheld.

    If this fails while the test above passes, the disclaimer has started
    appearing where it is false - telling a single agent that holds all 56
    tools that some of them belong to another worker, on a run that has no
    other worker.
    """
    from argus.scope import ScopeGuard
    from argus.system import build_system

    rendered = build_system(ctx.cfg, ScopeGuard(ctx.cfg.target))
    assert "YOUR TOOLS." not in rendered
    assert "next_action()" in rendered          # single mode really holds it
    assert "belongs to the lead" not in rendered


def test_the_lead_can_actually_reach_the_ledger(ctx):
    """`decide.py` names two readers: the operator, and the agent itself.

    For every team agent the second was false - `next_action` was in the
    registry and in no card, so `dispatch` refused it by role name. The lead
    is the role it belongs to, because deciding what happens next from
    recorded evidence is what a coordinator does.
    """
    from argus.team.cards import LEAD
    from argus.tools import registry

    assert "next_action" in LEAD.tools
    assert "next_action" in {t["name"] for t in registry.TOOL_SCHEMAS}
    ctx.board = Board(ctx.session)
    ctx.allowed = frozenset(LEAD.tools)
    out = registry.dispatch(ctx, "next_action", {})
    assert "not available to role" not in str(out.get("error", ""))


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


def test_max_workers_counts_workers_not_lead(tmp_path, lab_url):
    """--max-workers caps *worker* concurrency; the lead is the
    coordinator and must not consume a worker slot. With cap=1 a worker
    still spawns alongside the lead; the second worker is refused."""
    cfg = Config(target=lab_url, allow_private=True,
                 session_dir=tmp_path, max_turns=5, max_requests=50,
                 max_time_s=60, rate_rps=0)
    team = TeamRun(cfg, llm_factory=lambda role, name: ScriptedClient([]),
                   quiet=True, n_recon=0, n_exploit=0, max_workers=1)
    # register-only start: keeps agents "running" so the tally is exact
    team._start_worker = (
        lambda name, card, task: team.board.register(name, card.name, task))
    team.board.register("lead", "lead", "coordinate")
    first = team._spawn_guarded("recon", "t")
    assert "spawned" in first                       # lead not counted
    second = team._spawn_guarded("exploit", "t")
    assert "max_workers" in second.get("error", "")
