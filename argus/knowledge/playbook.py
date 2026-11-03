"""Probe ladders, loaded from data so a new class or CVE is a JSON edit."""
from __future__ import annotations

from pathlib import Path

from ..util import read_json

_PATH = Path(__file__).resolve().parent / "playbook.json"


def _load() -> dict:
    return read_json(_PATH, {"classes": {}, "recon_ladder": []})


def ladder(vuln_class: str) -> list[dict]:
    data = _load()
    entry = data["classes"].get((vuln_class or "").lower()) or {}
    return list(entry.get("steps") or [])


def skill_for(vuln_class: str) -> str | None:
    data = _load()
    entry = data["classes"].get((vuln_class or "").lower()) or {}
    return entry.get("skill")


def recon_ladder() -> list[dict]:
    return list(_load().get("recon_ladder") or [])


def known_classes() -> list[str]:
    return sorted(_load()["classes"])


def next_step(vuln_class: str, steps_done: list[str]) -> dict | None:
    """The cheapest discriminating step not yet run. The controller offers it;
    the model may argue for another and the ledger records which one ran."""
    done = {s.lower() for s in steps_done or []}
    for step in ladder(vuln_class):
        if step["step"].lower() not in done:
            return step
    return None


def proof_step(vuln_class: str) -> dict | None:
    return next((s for s in ladder(vuln_class) if s.get("proves")), None)
