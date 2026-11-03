"""The engagement ledger: what was found, what was tried, what is still open.

`state.json` stays small and readable — evidence bodies live in their own files
under `evidence/` and the ledger keeps only an index. That split is what lets a
long engagement keep a complete audit trail without the state file growing into
something no model can be shown and no human will read.

This module is the data layer: it loads, queries, mutates in memory and writes
atomically. It enforces *structure*, not *policy*. Every budget, every refusal
and every proof requirement lives in `hooks.py`, which is the only module the
rest of the system is allowed to write through.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Iterable

from .. import config
from ..util import (append_jsonl, bound, new_id, now, now_iso, read_json,
                    redact, sha256_text, write_json)

SCHEMA = 1

OPEN, CONFIRMED, FALSIFIED, PARKED = "open", "confirmed", "falsified", "parked"
# Recon is not a hypothesis: it has no class to falsify and no proof to meet. It
# gets a reserved pseudo-hypothesis so its commands are still scoped, budgeted
# and recorded exactly like every other command.
RECON = "recon"
PRIORITY_DEFAULT = 50
PRIORITY_REVIVED = 40
PRIORITY_PARKED = 0

# The escalation ladder a spent budget climbs instead of stopping. An exhausted
# budget changes strategy; it does not end the engagement.
LADDER = ("reuse_known_chain", "reclassify_surface", "research_target_stack",
          "widen_surface", "fleet_sweep", "operator_handoff")


@dataclass
class Budget:
    scope: str
    probes: int
    probe_limit: int
    minutes: float
    minute_limit: float

    @property
    def probes_left(self) -> int:
        return max(0, self.probe_limit - self.probes)

    @property
    def minutes_left(self) -> float:
        return max(0.0, self.minute_limit - self.minutes)

    @property
    def spent(self) -> bool:
        return self.probes >= self.probe_limit or self.minutes >= self.minute_limit

    def to_dict(self) -> dict:
        return {"scope": self.scope, "probes": self.probes, "probe_limit": self.probe_limit,
                "minutes": round(self.minutes, 1), "minute_limit": self.minute_limit,
                "probes_left": self.probes_left, "spent": self.spent}


def _blank(name: str, objective: str) -> dict:
    stamp = now_iso()
    return {
        "schema": SCHEMA,
        "engagement": name,
        "objective": objective,
        "created": stamp,
        "updated": stamp,
        "status": "open",
        "rules_of_engagement": {"tiers": [config.TIER_PASSIVE, config.TIER_ACTIVE],
                                "window": None, "no_touch": [], "authorisation": None},
        "targets": {},
        "surface": [],
        "hypotheses": [],
        "probes": [],
        "evidence_index": [],
        "findings": [],
        "strategies_used": [],
        "notes": [],
    }


class State:
    def __init__(self, paths: config.Paths, data: dict):
        self.paths = paths
        self.data = data

    # --- lifecycle -----------------------------------------------------------

    @classmethod
    def create(cls, name: str, objective: str = "", scope: dict | None = None,
               tiers: Iterable[str] | None = None, authorisation: str | None = None) -> "State":
        paths = config.Paths(name).ensure()
        if paths.state.exists():
            raise FileExistsError(f"engagement {name} already exists at {paths.dir}")
        data = _blank(paths.name, objective)
        if tiers:
            data["rules_of_engagement"]["tiers"] = [t for t in tiers if t in config.TIERS]
        data["rules_of_engagement"]["authorisation"] = authorisation
        state = cls(paths, data)
        write_json(paths.scope, scope or {"in_scope": [], "out_of_scope": [], "allowed_ports": []})
        state.save()
        state.event("engagement.created", {"objective": objective, "tiers": data["rules_of_engagement"]["tiers"]})
        return state

    @classmethod
    def load(cls, name: str) -> "State":
        paths = config.Paths(name)
        data = read_json(paths.state)
        if data is None:
            raise FileNotFoundError(f"no engagement {name!r}: create it first")
        return cls(paths, data)

    @classmethod
    def load_or_create(cls, name: str, **kwargs) -> "State":
        try:
            return cls.load(name)
        except FileNotFoundError:
            return cls.create(name, **kwargs)

    def save(self) -> "State":
        self.data["updated"] = now_iso()
        write_json(self.paths.state, self.data)
        return self

    def event(self, kind: str, payload: dict | None = None, actor: str = "main") -> None:
        append_jsonl(self.paths.events, {"ts": now_iso(), "kind": kind, "actor": actor,
                                         "payload": payload or {}})

    # --- scope ---------------------------------------------------------------

    @property
    def scope(self):
        from .scope import Scope
        return Scope.from_dict(read_json(self.paths.scope, {}))

    def set_scope(self, scope_dict: dict) -> None:
        write_json(self.paths.scope, scope_dict)
        self.event("scope.set", scope_dict)

    @property
    def tiers(self) -> list[str]:
        return list(self.data["rules_of_engagement"].get("tiers") or [])

    # --- targets and surface -------------------------------------------------

    def add_target(self, target: str, note: str = "") -> dict:
        """Targets are keyed by origin.

        `http://host:8080`, `http://host:8080/`, and `host:8080` are one target.
        Keying on the raw string instead produced three entries for one service,
        which then made the recon ladder look unfinished forever.
        """
        from .scope import origin_of
        key = origin_of(target)
        entry = self.data["targets"].get(key)
        if entry is None:
            entry = {"target": key, "first_seen": now_iso(), "urls": [], "notes": [],
                     "stack": {}}
            self.data["targets"][key] = entry
        if target not in entry.setdefault("urls", []) and target != key:
            entry["urls"].append(target)
        if note:
            entry["notes"].append(note)
        return entry

    def add_surface(self, target: str, kind: str, value: str, source: str = "",
                    detail: dict | None = None) -> dict:
        existing = next((s for s in self.data["surface"]
                         if s["target"] == target and s["kind"] == kind and s["value"] == value), None)
        if existing:
            if source and source not in existing["sources"]:
                existing["sources"].append(source)
            if detail:
                existing["detail"].update(detail)
            return existing
        item = {"id": new_id("sf"), "target": target, "kind": kind, "value": value,
                "sources": [source] if source else [], "detail": detail or {}, "seen": now_iso()}
        self.data["surface"].append(item)
        return item

    def surface_for(self, target: str | None = None, kind: str | None = None) -> list[dict]:
        return [s for s in self.data["surface"]
                if (target is None or s["target"] == target) and (kind is None or s["kind"] == kind)]

    # --- hypotheses ----------------------------------------------------------

    def add_hypothesis(self, target: str, vuln_class: str, statement: str,
                       entry_point: dict | None = None, priority: int = PRIORITY_DEFAULT,
                       falsifier: str = "") -> dict:
        item = {"id": new_id("hy"), "target": target, "vuln_class": vuln_class,
                "statement": statement, "entry_point": entry_point or {}, "priority": priority,
                "status": OPEN, "falsifier": falsifier, "opened": now_iso(), "closed": None,
                "closed_by": None, "probe_ids": [], "finding_id": None}
        self.data["hypotheses"].append(item)
        return item

    def hypothesis(self, hypothesis_id: str) -> dict | None:
        return next((h for h in self.data["hypotheses"] if h["id"] == hypothesis_id), None)

    def open_hypotheses(self, target: str | None = None) -> list[dict]:
        items = [h for h in self.data["hypotheses"]
                 if h["status"] == OPEN and (target is None or h["target"] == target)]
        return sorted(items, key=lambda h: (-h["priority"], h["opened"]))

    def set_hypothesis_status(self, hypothesis_id: str, status: str, reason: str = "",
                              evidence_id: str | None = None) -> dict:
        item = self.hypothesis(hypothesis_id)
        if item is None:
            raise KeyError(f"no hypothesis {hypothesis_id}")
        item["status"] = status
        item["closed"] = now_iso() if status in (CONFIRMED, FALSIFIED) else None
        item["closed_by"] = {"reason": reason, "evidence_id": evidence_id} if reason else item.get("closed_by")
        if status == PARKED:
            item["priority"] = PRIORITY_PARKED
        return item

    def revive_hypothesis(self, hypothesis_id: str, reason: str) -> dict:
        item = self.set_hypothesis_status(hypothesis_id, OPEN, reason)
        item["priority"] = max(item["priority"], PRIORITY_REVIVED)
        return item

    # --- probes --------------------------------------------------------------

    def record_probe(self, hypothesis_id: str, vuln_class: str, target: str, tool: str,
                     command: Any, result: str, evidence_id: str | None = None,
                     duration_ms: int | None = None, exit_code: int | None = None,
                     actor: str = "main", step: str = "") -> dict:
        from .scope import origin_of
        item = {"id": new_id("pr"), "hypothesis_id": hypothesis_id, "vuln_class": vuln_class,
                "target": target, "origin": origin_of(target), "tool": tool,
                "command": command if isinstance(command, list) else str(command),
                "step": step, "result": result, "evidence_id": evidence_id, "duration_ms": duration_ms,
                "exit_code": exit_code, "actor": actor, "ts": now_iso(), "epoch": now()}
        self.data["probes"].append(item)
        hypothesis = self.hypothesis(hypothesis_id)
        if hypothesis is not None:
            hypothesis["probe_ids"].append(item["id"])
        return item

    def probes_for(self, vuln_class: str | None = None, target: str | None = None) -> list[dict]:
        from .scope import origin_of
        origin = origin_of(target) if target else None
        return [p for p in self.data["probes"]
                if (vuln_class is None or p["vuln_class"] == vuln_class)
                and (origin is None
                     or p.get("origin", origin_of(p["target"])) == origin)]

    def steps_done(self, vuln_class: str, target: str | None = None) -> list[str]:
        return [p.get("step") or "" for p in self.probes_for(vuln_class, target) if p.get("step")]

    # --- evidence ------------------------------------------------------------

    def add_evidence(self, record: dict) -> dict:
        """Write one evidence file and index it. Bodies are bounded and redacted
        here, because this is the last point before text reaches the disk."""
        record = dict(record)
        record.setdefault("id", new_id("ev"))
        record.setdefault("kind", "probe")
        record.setdefault("ts", now_iso())
        for field in ("stdout_span", "stderr_span", "callback_payload"):
            if record.get(field):
                record[field] = redact(bound(str(record[field]), config.TOOL_OUTPUT_CAP, tail=2000))
        response = record.get("response")
        if isinstance(response, dict) and response.get("body_span"):
            response["body_span"] = redact(bound(str(response["body_span"]), 60_000, tail=2000))
        path = self.paths.evidence / f"{record['id']}.json"
        write_json(path, record)
        summary = record.get("summary") or _summarise(record)
        self.data["evidence_index"].append({
            "id": record["id"], "kind": record["kind"], "ts": record["ts"],
            "vuln_class": record.get("vuln_class"), "target": record.get("target"),
            "hypothesis_id": record.get("hypothesis_id"), "nonce": record.get("nonce"),
            "summary": bound(summary, 300), "sha256": sha256_text(str(record)),
            "file": str(path.relative_to(self.paths.dir)),
        })
        return record

    def load_evidence(self, evidence_ids: Iterable[str]) -> list[dict]:
        out = []
        for evidence_id in evidence_ids:
            record = read_json(self.paths.evidence / f"{evidence_id}.json")
            if record is not None:
                out.append(record)
        return out

    def evidence_for(self, hypothesis_id: str | None = None,
                     vuln_class: str | None = None) -> list[dict]:
        ids = [e["id"] for e in self.data["evidence_index"]
               if (hypothesis_id is None or e.get("hypothesis_id") == hypothesis_id)
               and (vuln_class is None or e.get("vuln_class") == vuln_class)]
        return self.load_evidence(ids)

    # --- findings ------------------------------------------------------------

    def add_finding(self, finding: dict) -> dict:
        finding = dict(finding)
        finding.setdefault("id", new_id("fi"))
        finding.setdefault("recorded", now_iso())
        self.data["findings"].append(finding)
        return finding

    def finding(self, finding_id: str) -> dict | None:
        return next((f for f in self.data["findings"] if f["id"] == finding_id), None)

    # --- budgets -------------------------------------------------------------

    def active_minutes(self, probes: list[dict]) -> float:
        """Wall time between consecutive probes, with any gap longer than
        IDLE_GAP_MINUTES excluded. A pause is parking, not work."""
        stamps = sorted(p.get("epoch") or 0 for p in probes if p.get("epoch"))
        if len(stamps) < 2:
            return 0.0
        total, gap_cap = 0.0, config.IDLE_GAP_MINUTES * 60
        for earlier, later in zip(stamps, stamps[1:]):
            delta = later - earlier
            if 0 < delta <= gap_cap:
                total += delta
        return total / 60.0

    def budget(self, vuln_class: str | None = None, target: str | None = None) -> Budget:
        if vuln_class:
            probes = self.probes_for(vuln_class=vuln_class, target=target)
            return Budget(f"class:{vuln_class}" + (f"@{target}" if target else ""), len(probes),
                          config.PROBE_BUDGET_PER_CLASS, self.active_minutes(probes),
                          config.MINUTE_BUDGET_PER_CLASS)
        probes = self.probes_for(target=target)
        return Budget(f"target:{target}" if target else "engagement", len(probes),
                      config.PROBE_BUDGET_PER_TARGET, self.active_minutes(probes),
                      config.MINUTE_BUDGET_PER_TARGET)

    def strategy_used(self, rung: str) -> None:
        if rung in LADDER and rung not in self.data["strategies_used"]:
            self.data["strategies_used"].append(rung)

    def next_strategy(self) -> str | None:
        return next((rung for rung in LADDER if rung not in self.data["strategies_used"]), None)

    # --- views ---------------------------------------------------------------

    def digest(self, limit: int = 12) -> dict:
        """The compact view handed to a model or printed by the CLI. Everything a
        next decision needs, and nothing a context window cannot hold."""
        return {
            "engagement": self.data["engagement"],
            "objective": self.data["objective"],
            "status": self.data["status"],
            "tiers": self.tiers,
            "targets": list(self.data["targets"]),
            "surface_counts": _counts(self.data["surface"], "kind"),
            "hypotheses": {
                "open": [{"id": h["id"], "class": h["vuln_class"], "target": h["target"],
                          "priority": h["priority"], "statement": bound(h["statement"], 160),
                          "probes": len(h["probe_ids"])} for h in self.open_hypotheses()[:limit]],
                "counts": _counts(self.data["hypotheses"], "status"),
            },
            "probes": {"total": len(self.data["probes"]),
                       "by_class": _counts(self.data["probes"], "vuln_class"),
                       "recent": [{"tool": p["tool"], "class": p["vuln_class"], "result": p["result"],
                                   "ts": p["ts"]} for p in self.data["probes"][-5:]]},
            "findings": [{"id": f["id"], "class": f.get("vuln_class"), "grade":
                          (f.get("proof") or {}).get("grade"), "title": bound(f.get("title", ""), 120)}
                         for f in self.data["findings"]],
            "budget": self.budget().to_dict(),
            "strategies_used": self.data["strategies_used"],
            "next_strategy": self.next_strategy(),
        }


def _counts(items: list[dict], field: str) -> dict:
    out: dict[str, int] = {}
    for item in items:
        key = str(item.get(field))
        out[key] = out.get(key, 0) + 1
    return dict(sorted(out.items(), key=lambda kv: -kv[1]))


def _summarise(record: dict) -> str:
    bits = [record.get("kind", "probe")]
    if record.get("tool"):
        bits.append(str(record["tool"]))
    response = record.get("response") or {}
    if response.get("status"):
        bits.append(f"HTTP {response['status']}")
    if record.get("exit_code") is not None:
        bits.append(f"exit {record['exit_code']}")
    extracted = record.get("extracted") or {}
    if extracted:
        bits.append(",".join(f"{k}={v}" for k, v in list(extracted.items())[:3]))
    return " ".join(str(b) for b in bits)
