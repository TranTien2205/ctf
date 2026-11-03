"""Workflows: reusable plan templates.

A workflow is not a second execution engine. It is a plan with holes in it, so
the thing the scheduler runs is the same artifact whether a model wrote it, the
deterministic planner wrote it, or an operator picked a template off the shelf.
That keeps one code path and makes the three comparable — which is the point, if
you want to know whether the planner was worth its tokens.

Shipped workflows are JSON, so no dependency is needed to read them. A workflow
you write yourself may be YAML when PyYAML happens to be installed.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .. import config
from ..ledger.state import State
from ..util import now_iso, read_json, write_json
from . import planner as planner_mod

PLACEHOLDER_RE = re.compile(r"\{\{\s*([a-z_][a-z0-9_]*)\s*\}\}")


def directory() -> Path:
    return config.WORKFLOWS


def available() -> list[dict]:
    out = []
    for path in sorted(directory().glob("*")):
        if path.suffix not in (".json", ".yaml", ".yml"):
            continue
        data = _load_file(path)
        if not data:
            continue
        out.append({"name": data.get("name") or path.stem, "file": path.name,
                    "description": data.get("description", ""),
                    "variables": data.get("variables") or [],
                    "tasks": len(data.get("tasks") or [])})
    return out


def load(name: str) -> dict:
    for suffix in (".json", ".yaml", ".yml"):
        path = directory() / f"{name}{suffix}"
        if path.is_file():
            data = _load_file(path)
            if data is None:
                raise ValueError(f"{path} could not be read")
            return data
    raise FileNotFoundError(f"no workflow {name!r} in {directory()}; "
                            f"available: {[w['name'] for w in available()]}")


def _load_file(path: Path) -> dict | None:
    if path.suffix == ".json":
        return read_json(path)
    try:
        import yaml                                                  # noqa: PLC0415
    except ImportError:
        return None
    try:
        with open(path, encoding="utf-8") as handle:
            return yaml.safe_load(handle)
    except Exception:                                                # noqa: BLE001
        return None


def instantiate(engagement: str, name: str, variables: dict | None = None) -> dict:
    """Fill a template's placeholders and write it as this engagement's plan."""
    workflow = load(name)
    state = State.load(engagement)
    values = dict(variables or {})
    values.setdefault("engagement", engagement)
    values.setdefault("objective", state.data["objective"])
    targets = list(state.data["targets"])
    if "target" not in values:
        if not targets:
            raise ValueError("this workflow needs a target, and the engagement has none: "
                             f"argus target {engagement} <url>")
        values["target"] = targets[0]
    missing = [variable for variable in (workflow.get("variables") or [])
               if variable not in values]
    if missing:
        raise ValueError(f"workflow {name!r} needs {missing}; pass them with --var k=v")

    tasks = []
    for index, raw in enumerate(workflow.get("tasks") or [], start=1):
        filled = _fill(raw, values)
        filled.setdefault("id", f"{name}-{index:02d}")
        tasks.append(planner_mod.blank_task(**filled))
    known = {task["id"] for task in tasks}
    for task in tasks:
        task["inputs"] = [dependency for dependency in task["inputs"] if dependency in known]
    plan = {"engagement": engagement, "objective": state.data["objective"],
            "created": now_iso(), "created_by": f"workflow:{name}",
            "note": workflow.get("description", ""), "variables": values, "tasks": tasks}
    write_json(config.Paths(engagement).plan, plan)
    return plan


def _fill(value, values: dict):
    if isinstance(value, str):
        def replace(match):
            key = match.group(1)
            return str(values.get(key, match.group(0)))
        return PLACEHOLDER_RE.sub(replace, value)
    if isinstance(value, list):
        return [_fill(item, values) for item in value]
    if isinstance(value, dict):
        return {key: _fill(item, values) for key, item in value.items()}
    return value


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(prog="argus-workflows")
    parser.add_argument("--engagement", default=None)
    parser.add_argument("--use", default=None, help="instantiate this workflow as the plan")
    parser.add_argument("--var", action="append", default=[], help="k=v, repeatable")
    args = parser.parse_args(argv)
    if not args.use:
        for workflow in available():
            print(f"{workflow['name']:20} {workflow['tasks']:>2} tasks  "
                  f"vars={workflow['variables']}\n{'':20} {workflow['description'][:90]}")
        return 0
    if not args.engagement:
        parser.error("--use needs --engagement")
    variables = dict(item.split("=", 1) for item in args.var if "=" in item)
    plan = instantiate(args.engagement, args.use, variables)
    print(planner_mod.render(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
