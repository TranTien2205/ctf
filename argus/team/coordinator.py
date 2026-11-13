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

import sys
import threading
import time
from pathlib import Path

from ..config import Config
from ..httpclient import GuardedClient
from dataclasses import replace

from ..llm import make_client
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
        self.max_workers = max_workers
        self.scope = ScopeGuard(
            cfg.target, extra_hosts=cfg.scope_hosts,
            exclude_paths=cfg.exclude_paths, allow_private=cfg.allow_private)
        self.session = Session(cfg.session_dir, cfg.target, meta={
            "model": cfg.model, "goal": cfg.goal, "operator": cfg.operator,
            "mode": "team", "scope": cfg.scope_hosts,
            "max_turns": cfg.max_turns, "max_requests": cfg.max_requests,
            "rate_rps": cfg.rate_rps, "exclude_paths": cfg.exclude_paths,
            "proxy": bool(cfg.proxy), "tls_verify": cfg.tls_verify,
            "require_proof": cfg.require_proof,
            "chain_keyed": bool(cfg.seal_key)},
            resume=Path(cfg.resume) if cfg.resume else None,
            secrets=cfg.secret_values, require_proof=cfg.require_proof,
            seal_key=cfg.seal_key)
        self.rate = RateLimiter(cfg.rate_rps)
        from ..mcp import MCPManager, discover_config_path
        self.mcp = MCPManager(discover_config_path(cfg.mcp_config))
        for name, err in self.mcp.errors().items():
            print(f"[argus] mcp config error {name}: {err}",
                  file=sys.stderr)
        self.board = Board(self.session)
        self.board.set_spawner(self._spawn_guarded)
        self._llm_factory = llm_factory or self._default_llm
        self._threads: dict[str, threading.Thread] = {}
        self._results: dict[str, dict] = {}
        self._lock = threading.Lock()
        self._counts = {"recon": 0, "exploit": 0, "report": 0}
        self._initial = {"recon": max(0, n_recon), "exploit": max(0, n_exploit),
                         "report": max(0, n_report)}

    def _resume_note(self) -> str:
        """When resuming, workers must know prior findings exist - the
        dedup gate would reject re-verified ones anyway."""
        if not (getattr(self.session, "resumed", False)
                and self.session.findings):
            return ""
        from ..session import sanitized_findings
        prior = "\n".join(
            f"- {f['id']} [{f['severity']}] {f['title']} ({f['url']})"
            for f in sanitized_findings(self.session.findings)[:15])
        return (f"\n\nThis run RESUMES session {self.session.id}. "
                f"Prior findings are already recorded - build on them, "
                f"do not re-verify:\n{prior}")

    # ------------------------------------------------------------- llm
    # A team role maps onto a job in the model table. The four cards want
    # different things: the lead holds the plan, recon makes many cheap calls
    # over a wide surface, exploit holds one long chain of reasoning about one
    # target, and the writer turns recorded findings into prose.
    TABLE_ROLE = {"lead": "planner", "recon": "breadth",
                  "exploit": "depth", "report": "writer"}

    def model_for(self, role: str) -> str:
        """The model this role runs on, and why it is that one.

        Off by default. Silently running four agents on four models would
        make a run harder to explain than it is worth, and an operator with
        one credential would watch three of them fail. With `--role-models`
        the table picks, and a pick whose credential is not set falls back to
        the run's own model rather than failing the agent.
        """
        if not getattr(self.cfg, "role_models", False):
            return self.cfg.model
        from .. import models as models_mod
        table_role = self.TABLE_ROLE.get(role, "")
        if not table_role:
            return self.cfg.model
        pick = models_mod.for_role(
            table_role, str(getattr(self.cfg, "policy", "") or "cheap"))
        if pick is None:
            return self.cfg.model
        if pick.provider != "anthropic" and not pick.credential():
            # naming the variable beats a role that dies on its first call
            print(f"[argus] {role}: the table picks {pick.key} for "
                  f"{table_role}, but none of "
                  f"{', '.join(pick.api_key_env) or '(no variable named)'} "
                  f"is set - falling back to {self.cfg.model}",
                  file=sys.stderr)
            return self.cfg.model
        return pick.key

    def _cost_breakdown(self) -> dict:
        """USD per agent and in total, each line naming the model it used.

        A team run can span providers, so one rate cannot describe it. An
        agent whose model is not in the table contributes no number and says
        so, rather than contributing a zero that reads as free.
        """
        from .. import models as models_mod
        per_agent, total, unpriced = {}, 0.0, []
        for name, res in self._results.items():
            if not isinstance(res, dict):
                continue
            tok = res.get("llm_tokens") if isinstance(
                res.get("llm_tokens"), dict) else {}
            # a crashed worker has no result dict to name its model, so fall
            # back to what the role WOULD have used rather than to the team's
            model = str(res.get("model") or "")
            if not model:
                role = name.rsplit("-", 1)[0] if "-" in name else name
                model = self.model_for(role)
            spec = models_mod.get(model)
            if spec is None:
                unpriced.append(f"{name} ({model})")
                per_agent[name] = {"model": model, "usd": None}
                continue
            usd = spec.cost(tok.get("in", 0), tok.get("out", 0),
                            cache_read=tok.get("cache_read", 0),
                            cache_write=tok.get("cache_write", 0))
            total += usd
            per_agent[name] = {"model": model, "usd": usd}
        out = {"usd": round(total, 6), "per_agent": per_agent,
               "table_version": models_mod.table_version(),
               "basis": "cache reads at 10% and cache writes at 125% of "
                        "input, per models.json"}
        if unpriced:
            out["unpriced"] = unpriced
            out["basis"] += (f"; {len(unpriced)} agent(s) ran a model with no "
                             "line in models.json and contribute no number")
        return out

    def _default_llm(self, role: str, name: str):
        model = self.model_for(role)
        if model == self.cfg.model:
            return make_client(self.cfg)
        # one field differs; everything else about the run is unchanged
        return make_client(replace(self.cfg, model=model))

    # ------------------------------------------------------------- spawn
    def _spawn_guarded(self, role: str, task: str) -> dict:
        """board.spawn callback - the only path to a new agent."""
        card = CARDS.get(role)
        if card is None or not card.worker:
            return {"error": f"role must be one of "
                             f"{[n for n, c in CARDS.items() if c.worker]}"}
        with self._lock:
            # the cap counts workers only - the lead is the coordinator and
            # must not starve the pool it manages
            if len([n for n, a in self.board.agents().items()
                    if a.get("status") == "running"
                    and a.get("role") != "lead"]) >= self.max_workers:
                return {"error": f"max_workers ({self.max_workers}) reached"}
            self._counts[role] += 1
            name = f"{role}-{self._counts[role]}"
            # a huge lead-written task lands verbatim in the worker seed -
            # bound it like board notes
            self._start_worker(name, card,
                               str(task or _DEFAULT_TASKS[role])[:4000])
            return {"spawned": name, "role": role}

    def _mk_client(self, name: str, max_requests: int = 0) -> GuardedClient:
        return GuardedClient(
            self.scope, self.session, self.rate,
            default_headers=self.cfg.resolved_headers(),
            tls_verify=self.cfg.tls_verify,
            max_requests=max_requests or self.cfg.max_requests, agent=name,
            proxy=self.cfg.proxy,
            secret_values=self.cfg.secret_values)

    def _start_worker(self, name: str, card, task: str) -> None:
        self.board.register(name, card.name, task)
        import dataclasses
        # `model` goes in too, or the loop reports the TEAM's model while its
        # client talks to the role's one - which priced every worker at the
        # wrong rate in `summary.json`, defeating the whole point of
        # --role-models. The cfg a loop holds must name the model it uses.
        wcfg = dataclasses.replace(
            self.cfg,
            model=self.model_for(card.name),
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
            replace(self.cfg, model=self.model_for("lead")),
            llm=self._llm_factory("lead", name),
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
        for role in ("recon", "exploit", "report"):
            for _ in range(self._initial.get(role, 0)):
                res = self._spawn_guarded(role, _DEFAULT_TASKS[role])
                if "error" in res:
                    # a dropped initial spawn ran silently before - the
                    # operator sized --max-workers and deserves to know the
                    # team came up short
                    print(f"[argus] initial {role} worker not started: "
                          f"{res['error']}", file=sys.stderr)

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
                    # lead finished: wait for workers to drain + exit.
                    # _threads is mutated by _start_worker on the lead's
                    # thread - snapshot under the same lock the spawner
                    # holds or the iteration can RuntimeError mid-run
                    with self._lock:
                        threads = list(self._threads.values())
                    if all(not t.is_alive() for t in threads):
                        break
                if self.board.stop.is_set():
                    break
        except KeyboardInterrupt:
            self.board.stop.set()
            self.board.leads.close()

        # bounded join; workers are daemon threads so a straggler can't hang
        join_deadline = time.monotonic() + 30
        with self._lock:
            join_set = list(self._threads.values())
        for t in join_set:
            remaining = join_deadline - time.monotonic()
            if remaining <= 0:
                break
            t.join(timeout=max(0.1, remaining))
        self.board.stop.set()

        with self._lock:
            threads = list(self._threads.items())
        for name, t in threads:
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
            return sum((r.get("llm_tokens") if isinstance(
                r.get("llm_tokens"), dict) else {}).get(key, 0)
                for r in self._results.values())
        tokens = {"in": _sum_tokens("in"), "out": _sum_tokens("out"),
                  "cache_read": _sum_tokens("cache_read"),
                  "cache_write": _sum_tokens("cache_write")}
        cost = self._cost_breakdown()
        calls = sum(r.get("llm_calls", 0)
                    if isinstance(r.get("llm_calls"), int) else 0
                    for r in self._results.values())
        report_path = ""
        try:
            report_path = str(render_report(
                self.session, cfg, summary, extra={
                    "mode": "team", "agents": self.board.agents(),
                    "llm_calls": calls, "llm_tokens": tokens,
                    "llm_cost": cost,
                }))
        except Exception as exc:
            # render failure must not swallow the run result or the seal
            print(f"[argus] report render failed: {exc}", file=sys.stderr)
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
