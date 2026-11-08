"""Team coordinator: shared infra, worker threads, budget watchdog.

Topology (two LLM levels, deliberately):
    lead (strategist) -> workers (recon/exploit/report)
Workers subdivide work via tool fan-out or by *requesting* a worker on the
board - the lead decides whether to actually spawn. The queue never lets
anyone but the lead widen the org chart.

Shared between every member (code-enforced, not prompt-level):
    one ScopeGuard, one RateLimiter, one Session/transcript, one Board.
"""
from __future__ import annotations

import threading
import time
from pathlib import Path

from ..config import Config
from ..httpclient import GuardedClient
from ..llm import ClaudeClient
from ..loop import AgentLoop
from ..ratelimit import RateLimiter
from ..scope import ScopeGuard
from ..session import Session
from ..system import build_system
from .board import Board
from .cards import CARDS, LEAD

_DEFAULT_TASKS = {
    "recon": "Map the target's attack surface and emit a lead for every "
             "endpoint+parameter worth testing. Prioritize params, forms, "
             "object ids, redirects, auth flows.",
    "exploit": "Pull leads and verify them into recorded findings. "
               "Confirm each with a minimal proving request before recording.",
    "report": "Read all findings and board notes, then write the executive "
              "summary of the engagement.",
}

_LEAD_SEED = """\
You are the LEAD of an authorized team assessment of {target}.

{authz}
{goal_line}
A crew is already running (see read_board). Your job: steer, not scan.
Seed priorities, spawn workers when coverage lags, handle worker requests,
and call finish_engagement when the surface is covered or budget is nearly
spent. Start with read_board() to see the current state."""


class TeamRun:
    def __init__(self, cfg: Config, llm_factory=None, quiet: bool = False,
                 n_recon: int = 1, n_exploit: int = 1, n_report: int = 0,
                 max_workers: int = 6):
        self.cfg = cfg
        self.quiet = quiet
        self.n_report = n_report
        self.max_workers = max_workers
        self.scope = ScopeGuard(
            cfg.target, extra_hosts=cfg.scope_hosts,
            exclude_paths=cfg.exclude_paths, allow_private=cfg.allow_private)
        self.session = Session(cfg.session_dir, cfg.target, meta={
            "model": cfg.model, "goal": cfg.goal, "operator": cfg.operator,
            "mode": "team", "scope": cfg.scope_hosts,
            "max_turns": cfg.max_turns, "max_requests": cfg.max_requests,
            "rate_rps": cfg.rate_rps, "exclude_paths": cfg.exclude_paths,
            "proxy": bool(cfg.proxy), "tls_verify": cfg.tls_verify},
            resume=Path(cfg.resume) if cfg.resume else None)
        self.rate = RateLimiter(cfg.rate_rps)
        from ..mcp import MCPManager, discover_config_path
        self.mcp = MCPManager(discover_config_path(cfg.mcp_config))
        self.board = Board(self.session)
        self.board.set_spawner(self._spawn_guarded)
        self._llm_factory = llm_factory or self._default_llm
        self._threads: dict[str, threading.Thread] = {}
        self._results: dict[str, dict] = {}
        self._lock = threading.Lock()
        self._counts = {"recon": 0, "exploit": 0, "report": 0}
        self._initial = {"recon": max(0, n_recon), "exploit": max(0, n_exploit)}

    def _resume_note(self) -> str:
        """When resuming, workers must know prior findings exist - the
        dedup gate would reject re-verified ones anyway."""
        if not (getattr(self.session, "resumed", False)
                and self.session.findings):
            return ""
        prior = "\n".join(
            f"- {f['id']} [{f['severity']}] {f['title']} ({f['url']})"
            for f in self.session.findings[:15])
        return (f"\n\nThis run RESUMES session {self.session.id}. "
                f"Prior findings are already recorded - build on them, "
                f"do not re-verify:\n{prior}")

    # ------------------------------------------------------------- llm
    def _default_llm(self, role: str, name: str):
        return ClaudeClient(self.cfg.api_key, self.cfg.api_base, self.cfg.model,
                            max_tokens=self.cfg.llm_max_tokens,
                            auth_token=self.cfg.auth_token)

    # ------------------------------------------------------------- spawn
    def _spawn_guarded(self, role: str, task: str) -> dict:
        """board.spawn callback - the only path to a new agent."""
        card = CARDS.get(role)
        if card is None or not card.worker:
            return {"error": f"role must be one of "
                             f"{[n for n, c in CARDS.items() if c.worker]}"}
        with self._lock:
            if len([n for n, a in self.board.agents().items()
                    if a.get("status") == "running"]) >= self.max_workers:
                return {"error": f"max_workers ({self.max_workers}) reached"}
            self._counts[role] += 1
            name = f"{role}-{self._counts[role]}"
            self._start_worker(name, card, task or _DEFAULT_TASKS[role])
            return {"spawned": name, "role": role}

    def _mk_client(self, name: str, max_requests: int = 0) -> GuardedClient:
        return GuardedClient(
            self.scope, self.session, self.rate,
            default_headers=self.cfg.resolved_headers(),
            tls_verify=self.cfg.tls_verify,
            max_requests=max_requests or self.cfg.max_requests, agent=name,
            proxy=self.cfg.proxy)

    def _start_worker(self, name: str, card, task: str) -> None:
        self.board.register(name, card.name, task)
        import dataclasses
        wcfg = dataclasses.replace(
            self.cfg,
            max_turns=card.turns or self.cfg.max_turns,
            max_requests=card.requests or self.cfg.max_requests)
        system = build_system(wcfg, self.scope) + "\n\n" + card.prompt()
        seed = (f"You are {name}, a {card.name} worker on an authorized "
                f"team assessment of {self.cfg.target}.\n"
                f"Task from the lead: {task}\n"
                f"{'Pull work with pull_leads().' if card.name == 'exploit' else 'Begin your task now.'}")
        seed += self._resume_note()
        loop = AgentLoop(
            wcfg, llm=self._llm_factory(card.name, name),
            quiet=self.quiet, scope=self.scope, session=self.session,
            client=self._mk_client(name, card.requests), board=self.board,
            mcp=self.mcp,
            agent_name=name, role=card.name, allowed=card.tools,
            system=system, seed=seed,
            stop_event=self.board.stop, report=False)

        def _run():
            try:
                res = loop.run()
            except Exception as exc:  # a worker crash must not kill the team
                res = {"error": f"{type(exc).__name__}: {exc}", "turns": 0}
            with self._lock:
                self._results[name] = res
            self.board.update_agent(
                name, status="done", turns=res.get("turns", 0),
                requests=loop.ctx.client.sent,
                tokens=res.get("llm_tokens"),
                llm_calls=res.get("llm_calls", 0),
                error=res.get("error"))

        t = threading.Thread(target=_run, name=name, daemon=True)
        self._threads[name] = t
        t.start()

    def _start_lead(self) -> None:
        name = "lead"
        self.board.register(name, "lead", "coordinate the engagement")
        system = build_system(self.cfg, self.scope) + "\n\n" + LEAD.prompt()
        goal_line = (f"Operator goal: {self.cfg.goal}" if self.cfg.goal else
                     "Operator goal: full authorized web assessment.")
        seed = _LEAD_SEED.format(
            target=self.cfg.target, goal_line=goal_line,
            authz="Authorization: operator-declared; the scope guard enforces "
                  "it technically for every worker's requests too.")
        seed += self._resume_note()
        loop = AgentLoop(
            self.cfg, llm=self._llm_factory("lead", name),
            quiet=self.quiet, scope=self.scope, session=self.session,
            client=self._mk_client(name), board=self.board, mcp=self.mcp,
            agent_name=name, role="lead", allowed=LEAD.tools, system=system,
            seed=seed, stop_event=self.board.stop, report=False)

        def _run():
            try:
                res = loop.run()
            except Exception as exc:
                res = {"error": f"{type(exc).__name__}: {exc}", "turns": 0}
            with self._lock:
                self._results[name] = res
            self.board.update_agent(
                name, status="done", turns=res.get("turns", 0),
                requests=loop.ctx.client.sent,
                tokens=res.get("llm_tokens"),
                llm_calls=res.get("llm_calls", 0),
                error=res.get("error"))
            # if the lead dies without finishing, close the pipeline anyway
            self.board.leads.close()
            self.board.engagement_done.set()

        t = threading.Thread(target=_run, name=name, daemon=True)
        self._threads[name] = t
        t.start()

    # ------------------------------------------------------------- run
    def run(self) -> dict:
        cfg = self.cfg
        started = time.monotonic()
        self._start_lead()
        for _ in range(self._initial["recon"]):
            self._spawn_guarded("recon", _DEFAULT_TASKS["recon"])
        for _ in range(self._initial["exploit"]):
            self._spawn_guarded("exploit", _DEFAULT_TASKS["exploit"])
        for _ in range(max(0, self.n_report)):
            self._spawn_guarded("report", _DEFAULT_TASKS["report"])

        deadline = started + cfg.max_time_s
        total_req_cap = cfg.max_requests * max(2, self.max_workers)
        try:
            while True:
                time.sleep(0.5)
                if self.session._seq >= total_req_cap or \
                        time.monotonic() >= deadline:
                    self.board.stop.set()
                    self.board.leads.close()
                    break
                if self.board.engagement_done.is_set():
                    # lead finished: wait for workers to drain + exit
                    if all(not t.is_alive() for t in self._threads.values()):
                        break
                if self.board.stop.is_set():
                    break
        except KeyboardInterrupt:
            self.board.stop.set()
            self.board.leads.close()

        # bounded join; workers are daemon threads so a straggler can't hang
        join_deadline = time.monotonic() + 30
        for t in self._threads.values():
            remaining = join_deadline - time.monotonic()
            if remaining <= 0:
                break
            t.join(timeout=max(0.1, remaining))
        self.board.stop.set()

        for name, t in self._threads.items():
            if t.is_alive():
                self.board.update_agent(name, status="killed")
        self.mcp.close()

        # final per-agent metrics pass: findings credited by agent name
        for name in self.board.agents():
            n = sum(1 for f in self.session.findings if f.get("agent") == name)
            self.board.update_agent(name, findings=n)

        from ..report.markdown import render_report
        lead_res = self._results.get("lead", {})
        summary = lead_res.get("summary") or ""
        def _sum_tokens(key: str) -> int:
            return sum((r.get("llm_tokens") or {}).get(key, 0)
                       for r in self._results.values())
        tokens = {"in": _sum_tokens("in"), "out": _sum_tokens("out"),
                  "cache_read": _sum_tokens("cache_read"),
                  "cache_write": _sum_tokens("cache_write")}
        calls = sum(r.get("llm_calls", 0) or 0 for r in self._results.values())
        report_path = render_report(self.session, cfg, summary, extra={
            "mode": "team", "agents": self.board.agents(),
            "llm_calls": calls, "llm_tokens": tokens,
        })
        # anchor every un-chained artifact (meta/findings/summary/report.*)
        # into the transcript so post-run edits are detectable by verify -
        # best-effort: a seal failure must not kill a completed run
        try:
            self.session.seal_artifacts()
        except OSError:
            pass
        return {
            "mode": "team",
            "session_dir": str(self.session.dir),
            "agents": self.board.agents(),
            "requests": self.session._seq,
            "findings": len(self.session.findings),
            "report": str(report_path),
            "llm_calls": calls,
            "llm_tokens": tokens,
            "lead_summary": summary,
            "lead_error": lead_res.get("error"),
            "elapsed_s": round(time.monotonic() - started, 1),
        }
