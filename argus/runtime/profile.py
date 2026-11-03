"""Harness profiles, loaded from data so tuning a model is not a code change."""
from __future__ import annotations

from dataclasses import dataclass, field

from .. import config
from ..util import read_json

_PATH = config.PROFILES / "models.json"


def _raw() -> dict:
    return read_json(_PATH, {"defaults": {}, "models": {}, "roles": {}})


@dataclass
class Profile:
    model: str
    provider: str = "mock"
    display: str = ""
    tool_dialect: str = "openai"
    context_window: int = 128000
    max_output_tokens: int = 4096
    max_steps: int = 24
    observation_cap: int = 9000
    history_chars: int = 90000
    restate_contract_every: int = 6
    plan_first: bool = True
    one_tool_per_step: bool = True
    temperature: float = 0.2
    reasoning: str = ""
    retry: int = 2
    compaction: str = "digest"
    family: str = "unknown"
    opencode_name: str = ""
    cost_per_mtok: dict = field(default_factory=lambda: {"input": 0.0, "output": 0.0})
    strengths: list = field(default_factory=list)
    notes: str = ""

    def cost(self, input_tokens: int, output_tokens: int) -> float:
        rates = self.cost_per_mtok or {}
        return (input_tokens * (rates.get("input", 0.0)) +
                output_tokens * (rates.get("output", 0.0))) / 1_000_000

    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items()}


def load(model: str) -> Profile:
    data = _raw()
    defaults = dict(data.get("defaults") or {})
    entry = (data.get("models") or {}).get(model)
    if entry is None:
        # An unknown model is not an error: it runs on the defaults, with its
        # name recorded, so trying a new model needs no edit at all.
        entry = {"display": model, "notes": "not in models.json; running on defaults"}
    merged = {**defaults, **entry, "model": model}
    allowed = set(Profile.__dataclass_fields__)
    return Profile(**{k: v for k, v in merged.items() if k in allowed})


def known() -> list[str]:
    return sorted((_raw().get("models") or {}))


def roles() -> dict:
    return dict(_raw().get("roles") or {})


def for_role(role: str) -> list[str]:
    return list(roles().get(role) or [])
