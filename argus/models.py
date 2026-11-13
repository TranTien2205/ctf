"""The model table: which models exist, what they cost, what they are for.

Ported from the orchestrator in the four-plane tree, reduced to what this
loop actually needs. Two things it buys:

* **A price.** The loop already counts tokens; without a table it cannot turn
  them into money, and "cost-optimised by model strength" is a claim you
  cannot check without a number. `summary.json` carries USD now, and the
  number traces to a line in `models.json`.
* **A role.** `--role depth` picks the cheapest model the table says can do
  that job, rather than making the operator remember which name is strong.

Prices move. A stale price is a wrong cost report, so `argus models` prints
what the file says and the report names the table version it used - the number
is always traceable to a line someone can check.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path

_PATH = Path(__file__).resolve().parent / "models.json"


def _raw() -> dict:
    try:
        data = json.loads(_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {"version": 0, "defaults": {}, "models": {}, "roles": {}}
    return data if isinstance(data, dict) else {
        "version": 0, "defaults": {}, "models": {}, "roles": {}}


@dataclass
class Model:
    key: str
    provider: str = "anthropic"
    display: str = ""
    api_base: str = ""
    api_key_env: list[str] = field(default_factory=list)
    context_window: int = 200000
    max_output_tokens: int = 4096
    usd_per_mtok_in: float = 0.0
    usd_per_mtok_out: float = 0.0
    roles: list[str] = field(default_factory=list)
    allow_insecure_base: bool = False
    note: str = ""
    #: The published successor, when this model has one. A successor
    #: relation, not a capability ranking: role selection drops a model whose
    #: successor this machine can call, so a cost policy cannot reach past
    #: the current generation.
    superseded_by: str = ""

    #: Cache reads bill at about a tenth of base input, cache writes at about
    #: 1.25x, on the published 5-minute-TTL rates the loop's ephemeral
    #: breakpoints use. Reads are the whole reason the loop marks a
    #: breakpoint; writes were simply not counted, which understated a run
    #: that primed a large prefix - the cheaper half was priced and the
    #: more expensive half was free.
    CACHE_READ_MULTIPLIER = 0.1
    CACHE_WRITE_MULTIPLIER = 1.25

    def cost(self, tokens_in: int, tokens_out: int,
             cache_read: int = 0, cache_write: int = 0) -> float:
        """USD for this many tokens, on the rates in `models.json`.

        Four counts, because a run has four: uncached input, cache reads,
        cache writes, and output. A caller that omits `cache_write` gets the
        old answer, which is why it defaults to zero rather than raising -
        but `summary.json` passes all four.
        """
        def _n(value) -> int:
            try:
                return max(int(value or 0), 0)
            except (TypeError, ValueError):
                return 0

        rate_in = self.usd_per_mtok_in
        return round(
            (_n(tokens_in) * rate_in
             + _n(cache_read) * rate_in * self.CACHE_READ_MULTIPLIER
             + _n(cache_write) * rate_in * self.CACHE_WRITE_MULTIPLIER
             + _n(tokens_out) * self.usd_per_mtok_out) / 1e6, 6)

    def credential(self) -> str:
        for name in self.api_key_env:
            value = os.environ.get(name, "")
            if value:
                return value
        return ""


def table_version() -> int:
    try:
        return int(_raw().get("version") or 0)
    except (TypeError, ValueError):
        return 0


def known() -> dict[str, Model]:
    raw = _raw()
    defaults = raw.get("defaults") if isinstance(raw.get("defaults"), dict) else {}
    out: dict[str, Model] = {}
    for key, spec in (raw.get("models") or {}).items():
        if not isinstance(spec, dict):
            continue
        merged = {**defaults, **spec}
        envs = merged.get("api_key_env") or []
        out[key] = Model(
            key=key,
            provider=str(merged.get("provider") or "anthropic"),
            display=str(merged.get("display") or key),
            api_base=str(merged.get("api_base") or ""),
            api_key_env=[str(e) for e in envs] if isinstance(envs, list) else [],
            context_window=int(merged.get("context_window") or 200000),
            max_output_tokens=int(merged.get("max_output_tokens") or 4096),
            usd_per_mtok_in=float(merged.get("usd_per_mtok_in") or 0.0),
            usd_per_mtok_out=float(merged.get("usd_per_mtok_out") or 0.0),
            roles=[str(r) for r in (merged.get("roles") or [])],
            allow_insecure_base=bool(merged.get("allow_insecure_base")),
            note=str(merged.get("note") or ""),
            superseded_by=str(merged.get("superseded_by") or ""),
        )
    return out


def roles() -> dict[str, str]:
    raw = _raw().get("roles")
    return {str(k): str(v) for k, v in raw.items()} if isinstance(raw, dict) else {}


def get(key: str) -> Model | None:
    return known().get(str(key or "").strip())


def for_role(role: str, policy: str = "cheap", exclude_family: str = "",
             usable_only: bool = True) -> Model | None:
    """The model to use for a role.

    `cheap` takes the least expensive candidate that the table says can do the
    job; `strong` takes the most expensive. The choice is only ever made among
    models the table lists for the role - a cost policy that could pick a
    model unfit for the task would be a false economy, and the planner is
    where that costs the engagement rather than money.

    `exclude_family` is how a review stays cross-family: two models that agree
    because they share a prior are not a check.

    `usable_only` drops candidates whose credential is not set, and defaults
    to on because the alternative is worse than it looks: `local` is priced at
    zero, so cost ordering puts it ahead of every paid model, and `--role
    breadth` resolved to a loopback server that is almost never running. A
    role that resolves to a model the operator cannot call is not a cheap
    answer, it is a run that dies on its first request. Pass False to ask what
    the table *says*, independent of this machine.
    """
    role = str(role or "").strip()
    cands = [m for m in known().values() if role in m.roles]
    if exclude_family:
        cands = [m for m in cands if family(m.key) != exclude_family]
    if usable_only:
        usable = [m for m in cands if m.credential()]
        # Anthropic models resolve their credential through the config chain
        # (OAuth store, OpenCode) rather than only an env var, so a missing
        # variable does not mean unusable for them.
        usable += [m for m in cands
                   if m.provider == "anthropic" and not m.credential()]
        cands = usable
    # A model the table marks DEPRECATED is one that stops answering on a
    # date, so it is never a selection - only an explicit --model.
    live = [m for m in cands
            if "DEPRECATED" not in (m.note or "").upper()]
    cands = live or cands

    # ...and a model whose published successor this machine can call is not a
    # selection either. `strong` ranks by PRICE as a proxy for capability,
    # which held while each generation cost more than the last and inverted
    # when it stopped: with the current generation priced below the previous
    # flagship, `strong` picked claude-opus-4-5 at 15/75 over
    # claude-opus-5-5 at 4/20 - an older model at 3.75x the cost, for the
    # planner role whose own description says a wrong call there costs the
    # engagement. `superseded_by` is the published successor relation, so
    # this fixes the inversion without inventing a capability ranking.
    keys = {m.key for m in cands}
    current = []
    for model in cands:
        successor = getattr(model, "superseded_by", "") or ""
        if successor and successor in keys:
            heir = get(successor)
            if heir is not None and (not usable_only or heir.credential()
                                     or heir.provider == "anthropic"):
                continue
        current.append(model)
    cands = current or cands

    if not cands:
        return None

    def price(m: Model) -> float:
        return m.usd_per_mtok_in + m.usd_per_mtok_out
    return (min(cands, key=price) if policy != "strong"
            else max(cands, key=price))


def family(key: str) -> str:
    """The lineage a model belongs to, for the cross-family review rule."""
    k = str(key or "").lower()
    for name in ("claude", "gpt", "deepseek", "gemini", "llama", "qwen",
                 "mistral", "grok"):
        if name in k:
            return name
    model = get(key)
    return (model.provider if model else "") or "unknown"
