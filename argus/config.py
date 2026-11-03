"""Paths, budgets and the one place an environment override is read."""
from __future__ import annotations

import os
from pathlib import Path

from .util import check_slug

ROOT = Path(__file__).resolve().parent.parent
ENGAGEMENTS = Path(os.environ.get("ARGUS_ENGAGEMENTS", ROOT / "engagements")).resolve()
SKILLS = ROOT / "skills"
WORKFLOWS = ROOT / "workflows"
EXPLOITS = ROOT / "scripts" / "exploits"
PROFILES = ROOT / "argus" / "runtime" / "profiles"

# An optional read-only bridge to the CTF toolkit this system was rebuilt from.
# Absent is normal: every module that uses it degrades to "no prior knowledge".
CTF_V2 = Path(os.environ.get("ARGUS_CTF_V2", "/home/kali/ctf-v2"))

# --- budgets -----------------------------------------------------------------
# These are brakes, not targets. They exist because the failure mode of an
# LLM-driven tester is not stopping too early; it is spending an afternoon on
# payload variants of a hypothesis that was already dead.
PROBE_BUDGET_PER_CLASS = 6        # probes against one vuln class before a forced switch
MINUTE_BUDGET_PER_CLASS = 20      # active minutes against one class before the same
PROBE_BUDGET_RECON = 15           # recon commands per target before the surface counts as mapped
PROBE_BUDGET_PER_TARGET = 40      # probes across all classes on one target
MINUTE_BUDGET_PER_TARGET = 90
IDLE_GAP_MINUTES = 25             # a longer gap between probes is parking, not work

# --- tool plane --------------------------------------------------------------
TOOL_TIMEOUT_DEFAULT = 180        # seconds
TOOL_TIMEOUT_MAX = 1800
TOOL_OUTPUT_CAP = 200_000         # bytes kept from one command's stdout
OBSERVATION_CAP = 12_000          # chars of one tool result handed to a model

# Risk tiers. The broker refuses a tier the engagement has not enabled.
TIER_PASSIVE = "passive"          # reads public/indirect sources only
TIER_ACTIVE = "active"            # touches the target, read-only, no state change
TIER_INTRUSIVE = "intrusive"      # writes, uploads, executes, changes state
TIERS = (TIER_PASSIVE, TIER_ACTIVE, TIER_INTRUSIVE)


def engagement_dir(name: str) -> Path:
    """Resolve, and refuse anything that leaves the engagements root."""
    safe = check_slug(name, "engagement name")
    path = (ENGAGEMENTS / safe).resolve()
    if ENGAGEMENTS.is_symlink() or not str(path).startswith(str(ENGAGEMENTS) + os.sep):
        raise ValueError(f"engagement path escapes {ENGAGEMENTS}")
    return path


class Paths:
    """Every file one engagement owns. One object, so no module invents a path."""

    def __init__(self, name: str):
        self.name = check_slug(name, "engagement name")
        self.dir = engagement_dir(name)
        self.engagement = self.dir / "engagement.json"
        self.scope = self.dir / "scope.json"
        self.state = self.dir / "state.json"
        self.plan = self.dir / "plan.json"
        self.tasks = self.dir / "tasks"
        self.reports = self.dir / "reports"
        self.evidence = self.dir / "evidence"
        self.artifacts = self.dir / "artifacts"
        self.events = self.dir / "log" / "events.jsonl"
        self.commands = self.dir / "log" / "commands.jsonl"
        self.refusals = self.dir / "log" / "refusals.jsonl"
        self.cost = self.dir / "log" / "cost.jsonl"
        self.decisions = self.dir / "decisions.json"
        # The one file in the system that holds a credential in the clear. It is
        # mode 0600, it is never read into a digest, and engagements/ is
        # gitignored. `Paths` exists so that no module invents a path, and the
        # identity store is not an exception.
        self.identities = self.dir / "identities.json"
        self.report = self.dir / "report.md"
        self.transcripts = self.dir / "transcripts"

    def ensure(self) -> "Paths":
        for directory in (
            self.dir, self.tasks, self.reports, self.evidence,
            self.artifacts, self.transcripts, self.events.parent,
        ):
            directory.mkdir(parents=True, exist_ok=True)
        return self

    def __repr__(self) -> str:
        return f"Paths({self.name} -> {self.dir})"
