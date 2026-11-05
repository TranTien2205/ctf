"""Which model, on which runner, for this task.

The routing decision is cheap to make and expensive to get wrong in one
direction only: using the strongest model for everything costs money, and using
the cheapest for a judgement call costs the engagement. So the table below is
ordered by what the task *needs*, not by what is available, and the cost policy
only chooses between candidates that can do the job.

Two rules are not negotiable:

* **Review is cross-family.** Two models that agree because they share a prior
  are not a check. A review task excludes the family that produced the finding.
* **A task that touches a target runs on our own harness when it can**, because
  that is the path where every call goes through the ledger gate. Delegating to
  a CLI agent is fine — its tools are still ours, over MCP — but it is a second
  choice for probing and a first choice for research and writing.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from ..broker import exec as ex
from ..runtime import credentials, profile as profile_mod

# What each kind of task needs from a model, in role terms.
ROLE_FOR_KIND = {
    "plan": "planner",
    "recon": "breadth",
    "classify": "executor",
    "probe": "executor",
    "exploit": "executor",
    "prove": "executor",
    "research": "long_context",
    "review": "reviewer",
    "report": "report",
    "tooling": "executor",
    "triage": "breadth",
}

# Tasks where the ledger gate matters most, so our own loop is preferred.
HARNESS_FIRST = {"recon", "probe", "exploit", "prove", "classify", "triage"}

POLICIES = ("quality", "balanced", "cheap")

# Roles where the cheapest capable model is the right answer, because the work is
# volume rather than judgement. Everything else keeps the declared order under
# the balanced policy: a plan or a review made by the cheapest available model is
# a false economy — it is the one decision the whole engagement is shaped by.
COST_SENSITIVE_ROLES = {"breadth", "triage", "long_context"}
ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")


@dataclass
class Route:
    task_id: str
    runner: str                  # harness | claude | opencode
    model: str
    role: str
    family: str
    reason: str
    profile: object = None
    estimated_cost_usd: float = 0.0
    alternatives: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"task_id": self.task_id, "runner": self.runner, "model": self.model,
                "role": self.role, "family": self.family, "reason": self.reason,
                "estimated_cost_usd": round(self.estimated_cost_usd, 4),
                "alternatives": self.alternatives}


class Availability:
    """What can actually run on this machine right now, measured once."""

    def __init__(self, probe_opencode: bool = True, probe_openbot: bool = True):
        self.keys = credentials.available()
        self.claude_cli = ex.which("claude") is not None
        self.opencode_cli = ex.which("opencode") is not None
        self.opencode_providers: set[str] = set()
        if probe_opencode and self.opencode_cli:
            self.opencode_providers = self._probe_opencode()
        # OpenBot is a coordination plane rather than a provider: it reaches a
        # model through an agent that already holds a subscription, so what makes
        # a model reachable is an agent configured for it, not a key here.
        self.openbot_agents: dict[str, str] = {}
        self.openbot_reason = "not probed"
        if probe_openbot:
            self.openbot_agents, self.openbot_reason = self._probe_openbot()

    @staticmethod
    def _probe_openbot() -> tuple[dict[str, str], str]:
        """Which argus models a dispatchable OpenBot agent exists for."""
        try:
            from .openbot import Fleet
            fleet = Fleet()
            ok, reason = fleet.available()
            if not ok:
                return {}, reason
            found = {agent.argus_model: (agent.id or agent.name)
                     for agent in fleet.list_agents() if agent.argus_model}
            return found, reason
        except Exception as error:                                     # noqa: BLE001
            return {}, f"{type(error).__name__}: {error}"

    @staticmethod
    def _probe_opencode() -> set[str]:
        """Read which providers opencode holds credentials for.

        `opencode auth list` is a TUI listing: box-drawing characters, ANSI
        colour, and a trailing `api`/`oauth` word per row. Stripping all three is
        the whole job, and skipping it silently cost this router every non-Claude
        model — the names came out as `deepseek-\x1b[90mapi` and matched nothing.
        """
        try:
            result = ex.run(["opencode", "auth", "list"], timeout=30)
        except Exception:                                              # noqa: BLE001
            return set()
        found = set()
        for line in ANSI_RE.sub("", result.stdout).splitlines():
            text = line.strip().lstrip("●│┌└├─ ").strip()
            if not text or "redential" in text:
                continue
            tokens = [token for token in text.split() if token]
            while tokens and tokens[-1].lower() in ("api", "oauth", "wellknown", "key"):
                tokens.pop()
            if tokens:
                found.add("-".join(tokens).lower())
        return found

    def runners_for(self, model_profile) -> list[tuple[str, str]]:
        """(runner, why) pairs that can reach this model, best first."""
        out = []
        provider = model_profile.provider
        agent = self.openbot_agents.get(model_profile.model)
        if agent:
            out.append(("openbot", f"openbot agent {agent} runs its own loop "
                                   f"against our MCP server"))
        if provider in ("anthropic", "openai", "deepseek", "google", "openrouter"):
            if self.keys.get(provider, {}).get("present"):
                out.append(("harness", f"{provider} key present, our loop keeps the ledger gate"))
        if provider == "opencode" and self.opencode_cli:
            prefix = (model_profile.opencode_name or "").split("/")[0]
            if not prefix or prefix in self.opencode_providers or not self.opencode_providers:
                out.append(("harness", "opencode cli as a stateless model, our loop"))
                out.append(("opencode", "opencode runs its own loop against our MCP server"))
        if model_profile.family == "claude" and self.claude_cli:
            out.append(("claude", "claude code subscription, its own loop against our MCP server"))
            out.append(("harness", "claude cli as a stateless model, our loop"))
        if provider == "mock":
            out.append(("harness", "scripted provider"))
        return out

    def to_dict(self) -> dict:
        return {"api_keys": {k: v["present"] for k, v in self.keys.items()},
                "claude_cli": self.claude_cli, "opencode_cli": self.opencode_cli,
                "opencode_credentials": sorted(self.opencode_providers),
                "openbot_agents": dict(sorted(self.openbot_agents.items())),
                "openbot": self.openbot_reason}


class Router:
    def __init__(self, policy: str = "balanced", availability: Availability | None = None):
        if policy not in POLICIES:
            raise ValueError(f"policy must be one of {POLICIES}")
        self.policy = policy
        self.availability = availability or Availability()

    # --- candidate ordering --------------------------------------------------

    def candidates(self, role: str, exclude_families: tuple[str, ...] = ()) -> list:
        models = profile_mod.for_role(role) or profile_mod.for_role("executor")
        profiles = [profile_mod.load(model) for model in models]
        profiles = [p for p in profiles if p.family not in exclude_families]
        reachable = [p for p in profiles if self.availability.runners_for(p)]
        if self.policy == "cheap" or (self.policy == "balanced"
                                      and role in COST_SENSITIVE_ROLES):
            reachable.sort(key=_cost_key)
        return reachable

    # --- the decision --------------------------------------------------------

    def route(self, task: dict, exclude_families: tuple[str, ...] = ()) -> Route:
        kind = (task.get("kind") or "probe").lower()
        role = task.get("role") or ROLE_FOR_KIND.get(kind, "executor")
        pinned = task.get("model")
        if pinned:
            model_profile = profile_mod.load(pinned)
            runners = self.availability.runners_for(model_profile)
            if runners:
                runner = task.get("runner") or self._pick_runner(kind, runners)
                return Route(task.get("id", "?"), runner, pinned, role, model_profile.family,
                             f"pinned by the plan; {dict(runners).get(runner, 'available')}",
                             model_profile, _estimate(model_profile, task))
            # A pinned model that cannot run is a routing fact, not a failure:
            # fall through and say so in the reason.
        options = self.candidates(role, exclude_families)
        if not options:
            return Route(task.get("id", "?"), "none", "", role, "",
                         f"no model for role {role!r} is reachable: "
                         f"{json.dumps(self.availability.to_dict())}"
                         + (f"; excluded families {list(exclude_families)}" if exclude_families else ""))
        chosen = options[0]
        runners = self.availability.runners_for(chosen)
        runner = task.get("runner") or self._pick_runner(kind, runners)
        why = dict(runners).get(runner, "available")
        reason = (f"role {role} -> {chosen.model} ({chosen.family}); policy {self.policy}; {why}"
                  + (f"; pinned {pinned} was unreachable" if pinned else ""))
        return Route(task.get("id", "?"), runner, chosen.model, role, chosen.family, reason,
                     chosen, _estimate(chosen, task),
                     [{"model": option.model, "family": option.family,
                       "cost_per_mtok": option.cost_per_mtok} for option in options[1:4]])

    @staticmethod
    def _pick_runner(kind: str, runners: list[tuple[str, str]]) -> str:
        names = [name for name, _why in runners]
        if kind in HARNESS_FIRST and "harness" in names:
            return "harness"
        for preferred in ("claude", "opencode", "harness"):
            if preferred in names:
                return preferred
        return names[0] if names else "none"


def _cost_key(model_profile) -> float:
    rates = model_profile.cost_per_mtok or {}
    return rates.get("input", 0.0) + rates.get("output", 0.0) * 0.25


def _estimate(model_profile, task: dict) -> float:
    """A rough per-task estimate: steps x a typical turn. Good enough to compare
    two candidates, not good enough to bill anyone."""
    steps = int(task.get("max_steps") or model_profile.max_steps)
    per_step_input = min(model_profile.history_chars, 40_000) // 4
    per_step_output = 600
    return model_profile.cost(steps * per_step_input, steps * per_step_output)


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(prog="argus-route")
    parser.add_argument("--policy", default="balanced", choices=POLICIES)
    parser.add_argument("--kind", default=None, help="route one task kind and exit")
    args = parser.parse_args(argv)
    router = Router(policy=args.policy)
    print("availability:", json.dumps(router.availability.to_dict(), indent=1))
    kinds = [args.kind] if args.kind else list(ROLE_FOR_KIND)
    print(f"\n{'kind':10} {'runner':9} {'model':24} {'family':9} est.$  reason")
    for kind in kinds:
        route = router.route({"id": f"t-{kind}", "kind": kind})
        print(f"{kind:10} {route.runner:9} {route.model or '-':24} {route.family or '-':9} "
              f"{route.estimated_cost_usd:6.3f} {route.reason[:70]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
