"""OpenBot as the coordination plane, with this repository still the gate.

OpenBot drives coding-agent CLIs over ACP and keeps one workspace per agent, so
it does the part `argus/orchestrator/` does: hold several subscriptions, hand a
task to one of them, and report what came back. It does not do the part
`argus/ledger/` does. Nothing in OpenBot decides whether a claim is `proven`,
because that decision is the proof matrix and the proof matrix lives here. So
the arrangement is OpenBot above and argus below: OpenBot picks who works, the
broker decides what they may run, and the ledger decides what counts.

The control surface is `openbot-cli`, which talks to the running app over a
loopback HTTP server the app opens only when at least one agent has "Local
scripts" turned on. That server writes its address and bearer token to three
files, and their absence is the single reason the CLI cannot be reached:

    ~/.config/OpenBot/automation/url      http://127.0.0.1:<port>
    ~/.config/OpenBot/automation/token    the bearer token
    ~/.config/OpenBot/automation/headers  the same token as a header line

Both of the settings this needs are per-agent switches in the app's own UI and
neither can be set from here. `openbot.db` is an event-sourced store belonging
to a running process; writing a flag into its projection behind its back would
leave the projection disagreeing with its own event log, so this module reads
that database and never writes it. `preflight()` reports exactly what is missing
instead.
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
from dataclasses import dataclass, field
from pathlib import Path

from ..broker import exec as ex
from ..runtime import profile as profile_mod

AUTOMATION_DIR = Path.home() / ".config" / "OpenBot" / "automation"
OPENBOT_DB = Path.home() / ".config" / "OpenBot" / "openbot.db"
CLI = "openbot-cli"

# `openbot-cli` documents these, and they are the whole control vocabulary. A
# number that is not here is a CLI this code has not been read against.
EXIT_DONE = 0
EXIT_FAILED = 1          # the turn failed, or OpenBot refused
EXIT_USAGE = 2           # wrong command line: ours to fix, never the agent's
EXIT_NEEDS_PERSON = 3    # the agent is waiting for a human
EXIT_TIMEOUT = 4         # timed out, and the work continues inside OpenBot
EXIT_UNREACHABLE = 5     # no running app, or no agent with Local scripts on

# What an exhausted subscription looks like in the text that comes back. Each one
# is a substring match on a lowercased message, because the wording belongs to
# the provider rather than to OpenBot and a provider rewords its errors.
EXHAUSTED = ("usage limit", "rate limit", "quota", "insufficient balance",
             "insufficient_quota", "credit balance", "too many requests",
             "429", "resets at", "upgrade to continue", "out of credit")


def _looks_exhausted(text: str) -> bool:
    lowered = (text or "").lower()
    return any(marker in lowered for marker in EXHAUSTED)


@dataclass
class OpenBotAgent:
    """One agent as OpenBot reports it, plus the argus profile it maps to."""
    id: str
    name: str
    model: str = ""
    provider: str = ""
    effort: str = ""
    raw: dict = field(default_factory=dict)

    @property
    def argus_model(self) -> str:
        """The argus profile whose route this agent's model is.

        An OpenBot agent names a model the way its provider does
        (`opencode-go/deepseek-v4.1-flash`), and argus names the same model its
        own way (`deepseek-flash`). The profile carries both, so the match is on
        either spelling rather than on a table that would have to be maintained
        twice.
        """
        for name in profile_mod.known():
            loaded = profile_mod.load(name)
            if self.model and self.model in (loaded.model, loaded.opencode_name):
                return name
        return ""

    def roles(self) -> list[str]:
        """Which argus roles this agent can take, from the profile it maps to."""
        model = self.argus_model
        if not model:
            return []
        return [role for role, members in profile_mod.roles().items() if model in members]


@dataclass
class Delivery:
    """The outcome of handing one task to one agent."""
    agent: str
    exit_code: int = -1
    delivery_id: str = ""
    text: str = ""
    error: str = ""
    raw: dict = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.exit_code == EXIT_DONE

    @property
    def exhausted(self) -> bool:
        """Did this fail because the account behind the agent has nothing left?

        Only a failed turn can be an exhausted one. A timeout is work still
        running and a refusal is a decision, so neither is quota.
        """
        return self.exit_code == EXIT_FAILED and _looks_exhausted(f"{self.error} {self.text}")

    @property
    def reason(self) -> str:
        return {EXIT_DONE: "done", EXIT_FAILED: "turn-failed", EXIT_USAGE: "bad-command-line",
                EXIT_NEEDS_PERSON: "waiting-for-a-person", EXIT_TIMEOUT: "timed-out",
                EXIT_UNREACHABLE: "openbot-unreachable"}.get(self.exit_code,
                                                             f"exit-{self.exit_code}")


def automation_ready() -> tuple[bool, str]:
    """Is the app's loopback control server up, and how do we know?"""
    if ex.which(CLI) is None:
        return False, f"{CLI} is not on PATH"
    missing = [name for name in ("url", "token") if not (AUTOMATION_DIR / name).is_file()]
    if missing:
        return False, (f"{AUTOMATION_DIR} has no {', '.join(missing)}: the app writes these only "
                       f"while at least one agent has Local scripts on")
    return True, (AUTOMATION_DIR / "url").read_text().strip()


def agents_in_db() -> list[OpenBotAgent]:
    """Every agent the app has, read from its store rather than from the CLI.

    The CLI lists only agents with Local scripts on, which is the right answer
    for dispatch and the wrong one for diagnosis: an agent that exists but cannot
    be reached is exactly what the operator needs told. This read is the only
    reason this module opens the database, and it opens it read-only.
    """
    if not OPENBOT_DB.is_file():
        return []
    out: list[OpenBotAgent] = []
    connection = sqlite3.connect(f"file:{OPENBOT_DB}?mode=ro", uri=True)
    try:
        rows = connection.execute("select agent_id, agent_json from projection_agents "
                                  "order by sort_order").fetchall()
    except sqlite3.DatabaseError:
        return []
    finally:
        connection.close()
    for agent_id, agent_json in rows:
        try:
            data = json.loads(agent_json)
        except json.JSONDecodeError:
            data = {}
        out.append(OpenBotAgent(id=agent_id, name=str(data.get("name") or agent_id),
                                model=str(data.get("model") or ""),
                                provider=str(data.get("provider") or ""),
                                effort=str(data.get("reasoningEffort") or ""), raw=data))
    return out


def mcp_servers_in_db() -> list[dict]:
    """The MCP servers registered in the app, so we can say whether argus is one."""
    if not OPENBOT_DB.is_file():
        return []
    connection = sqlite3.connect(f"file:{OPENBOT_DB}?mode=ro", uri=True)
    try:
        rows = connection.execute("select name, transport, enabled, command, args_json "
                                  "from projection_mcp_servers order by position").fetchall()
    except sqlite3.DatabaseError:
        return []
    finally:
        connection.close()
    return [{"name": name, "transport": transport, "enabled": bool(enabled),
             "command": command, "args": json.loads(args or "[]")}
            for name, transport, enabled, command, args in rows]


class Fleet:
    """The agents OpenBot can run, and the one way a task reaches one of them."""

    def __init__(self, timeout: int = 1800, cli: str = CLI):
        self.timeout = timeout
        self.cli = cli
        self._listed: list[OpenBotAgent] | None = None

    # --- what can be reached -------------------------------------------------

    def available(self) -> tuple[bool, str]:
        ready, detail = automation_ready()
        if not ready:
            return False, detail
        if not self.list_agents():
            return False, "no agent has Local scripts on, so the CLI finds none"
        return True, detail

    def list_agents(self, refresh: bool = False) -> list[OpenBotAgent]:
        """The agents the CLI can dispatch to, which is not every agent that exists."""
        if self._listed is not None and not refresh:
            return self._listed
        result = ex.run([self.cli, "list", "--json"], timeout=60)
        self._listed = []
        if result.exit_code != EXIT_DONE:
            return self._listed
        try:
            data = json.loads(result.stdout or "{}")
        except json.JSONDecodeError:
            return self._listed
        rows = data.get("agents") if isinstance(data, dict) else data
        for row in rows or []:
            if not isinstance(row, dict):
                continue
            self._listed.append(OpenBotAgent(
                id=str(row.get("id") or row.get("agentId") or ""),
                name=str(row.get("name") or ""), model=str(row.get("model") or ""),
                provider=str(row.get("provider") or ""),
                effort=str(row.get("reasoningEffort") or row.get("effort") or ""), raw=row))
        return self._listed

    def for_role(self, role: str) -> list[OpenBotAgent]:
        """Agents that can take this role, strongest-to-cheapest as the role lists them."""
        order = {model: index for index, model in enumerate(profile_mod.for_role(role))}
        ranked = [(order.get(agent.argus_model, 10_000), agent)
                  for agent in self.list_agents() if role in agent.roles()]
        return [agent for _rank, agent in sorted(ranked, key=lambda pair: pair[0])]

    # --- handing over one task -----------------------------------------------

    def dispatch(self, agent: OpenBotAgent | str, brief: str, key: str = "",
                 timeout: int | None = None) -> Delivery:
        """Run one task on one agent and wait for the turn to end.

        The brief goes in on stdin rather than in argv: a brief is thousands of
        characters of contract and evidence, and an argv has a limit. `--id` makes
        the call idempotent, so a retry after a dropped connection resumes the
        same delivery instead of starting a second one.
        """
        name = agent if isinstance(agent, str) else (agent.id or agent.name)
        seconds = timeout or self.timeout
        argv = [self.cli, "run", name, "-", "--wait", "--json", "--timeout", f"{seconds}s"]
        if key:
            argv += ["--id", key]
        result = ex.run(argv, timeout=seconds + 120, stdin=brief)
        delivery = Delivery(agent=name, exit_code=result.exit_code)
        try:
            data = json.loads(result.stdout or "{}")
        except json.JSONDecodeError:
            data = {}
        if isinstance(data, dict):
            delivery.raw = data
            delivery.delivery_id = str(data.get("deliveryId") or data.get("id") or "")
            delivery.text = str(data.get("text") or data.get("result") or data.get("message") or "")
            delivery.error = str(data.get("error") or "")
        if not delivery.text and not delivery.error:
            delivery.text = (result.stdout or "").strip()
            delivery.error = (result.stderr or "").strip() if result.exit_code else ""
        return delivery

    def status(self, agent: OpenBotAgent | str, delivery_id: str) -> dict:
        """Where a delivery got to, for the one that timed out while still working."""
        name = agent if isinstance(agent, str) else (agent.id or agent.name)
        result = ex.run([self.cli, "status", name, delivery_id, "--json"], timeout=60)
        try:
            return json.loads(result.stdout or "{}")
        except json.JSONDecodeError:
            return {"exitCode": result.exit_code, "stdout": (result.stdout or "")[:2000]}

    # --- when an agent runs out ----------------------------------------------

    def set_account(self, agent: OpenBotAgent | str, account: str = "default") -> bool:
        name = agent if isinstance(agent, str) else (agent.id or agent.name)
        return ex.run([self.cli, "agent", "set-account", name, account, "--json"],
                      timeout=120).exit_code == EXIT_DONE

    def set_model(self, agent: OpenBotAgent | str, model: str,
                  effort: str = "", provider: str = "") -> bool:
        name = agent if isinstance(agent, str) else (agent.id or agent.name)
        argv = [self.cli, "agent", "set-model", name, model]
        if effort:
            argv += ["--effort", effort]
        if provider:
            argv += ["--provider", provider]
        return ex.run(argv + ["--json"], timeout=120).exit_code == EXIT_DONE

    def new_chat(self, agent: OpenBotAgent | str) -> bool:
        """Start a fresh chat, which is the answer to a context window that is full."""
        name = agent if isinstance(agent, str) else (agent.id or agent.name)
        return ex.run([self.cli, "agent", "new-chat", name, "--json"],
                      timeout=120).exit_code == EXIT_DONE
