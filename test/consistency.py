#!/usr/bin/env python3
"""Cross-file consistency: does the system still agree with itself?

Every check here exists because the alternative is a document, a registry or a
prompt that names something which no longer exists. In a system whose whole
claim is that it does not invent things, a README naming a command that was
renamed is not a cosmetic problem.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from argus.broker.serve import merge                                  # noqa: E402
from argus.broker.servers import SERVER_NAMES                         # noqa: E402
from argus.knowledge import playbook                                  # noqa: E402
from argus.ledger import proof as matrix                              # noqa: E402
from argus.runtime import profile as profile_mod                      # noqa: E402
from argus.util import read_json                                      # noqa: E402

FAILURES: list[str] = []
COUNT = 0
SERVER = merge(list(SERVER_NAMES))
TOOL_NAMES = set(SERVER.tools)


def check(label: str, condition: bool, detail: str = "") -> None:
    global COUNT
    COUNT += 1
    if not condition:
        FAILURES.append(f"{label}: {detail}")
        print(f"  [FAIL] {label}" + (f" — {detail}" if detail else ""))


def markdown_files() -> list[Path]:
    out = []
    for path in ROOT.rglob("*.md"):
        if any(part in ("engagements", ".git", "node_modules") for part in path.parts):
            continue
        out.append(path)
    return sorted(out)


# --- imports -----------------------------------------------------------------

def test_imports() -> None:
    print("\nimports")
    modules = sorted(path.relative_to(ROOT).with_suffix("").as_posix().replace("/", ".")
                     for path in (ROOT / "argus").rglob("*.py")
                     if "__pycache__" not in path.parts)
    for module in modules:
        name = module.removesuffix(".__init__")
        result = subprocess.run([sys.executable, "-c", f"import {name}"], cwd=ROOT,
                                capture_output=True, text=True, timeout=120, check=False)
        check(f"import {name}", result.returncode == 0,
              (result.stderr or "").strip().splitlines()[-1] if result.returncode else "")


# --- registries agree with disk ---------------------------------------------

def test_skills() -> None:
    print("\nskills")
    registry = read_json(ROOT / "skills" / "registry.json", {})
    registered = {entry["name"] for entry in registry.get("skills", [])}
    on_disk = {path.parent.name for path in (ROOT / "skills").glob("*/SKILL.md")}
    check("the skill registry matches the directories", registered == on_disk,
          f"only in registry: {sorted(registered - on_disk)}; "
          f"only on disk: {sorted(on_disk - registered)}")
    for entry in registry.get("skills", []):
        check(f"skill file exists: {entry['path']}", (ROOT / entry["path"]).is_file())
        check(f"skill has a description: {entry['name']}", bool(entry.get("summary")))
    index = (ROOT / "skills" / "INDEX.md").read_text(encoding="utf-8")
    for name in re.findall(r"`([a-z0-9-]+)`", index):
        if (ROOT / "skills" / name).is_dir() or name in matrix.MATRIX or name in (
                "argus", "knowledge.playbook", "extending-argus"):
            continue
        check(f"INDEX.md names something real: {name}",
              name in matrix.MATRIX or name in playbook.known_classes()
              or (ROOT / "skills" / name).is_dir(),
              "named in INDEX.md but is neither a skill nor a class")


def test_playbook() -> None:
    print("\nplaybook")
    for name in playbook.known_classes():
        for step in playbook.ladder(name):
            check(f"playbook {name}/{step['step']} names a real tool",
                  step["tool"] in TOOL_NAMES, f"{step['tool']} is not a registered tool")
            check(f"playbook {name}/{step['step']} declares a known tier",
                  step.get("tier") in ("passive", "active", "intrusive"), str(step.get("tier")))
            check(f"playbook {name}/{step['step']} says why it exists", bool(step.get("why")))
    for step in playbook.recon_ladder():
        check(f"recon ladder step {step['step']} names a real tool",
              step["tool"] in TOOL_NAMES, step["tool"])


def test_exploit_registry() -> None:
    print("\nexploit registry")
    registry = read_json(ROOT / "scripts" / "exploits" / "registry.json", {})
    for entry in registry.get("scripts", []):
        path = ROOT / "scripts" / "exploits" / entry["id"] / entry.get("entry", "run.py")
        check(f"exploit script exists: {entry['id']}", path.is_file(), str(path))
        check(f"exploit {entry['id']} names a class in the matrix",
              matrix.spec_for(entry.get("vuln_class", "")) is not None,
              str(entry.get("vuln_class")))
        check(f"exploit {entry['id']} declares a tier",
              entry.get("tier") in ("passive", "active", "intrusive"), str(entry.get("tier")))
        check(f"exploit {entry['id']} declares its preconditions",
              bool(entry.get("preconditions")))
    template = ROOT / "scripts" / "exploits" / "_template"
    check("the exploit template is present", (template / "run.py").is_file()
          and (template / "meta.json").is_file())


def test_workflows() -> None:
    print("\nworkflows")
    from argus.orchestrator import planner as planner_mod
    from argus.orchestrator import workflows as workflows_mod
    for workflow in workflows_mod.available():
        data = workflows_mod.load(workflow["name"])
        ids = [task.get("id") for task in data.get("tasks") or []]
        check(f"workflow {workflow['name']} has unique task ids",
              len(ids) == len(set(ids)), str(ids))
        for task in data.get("tasks") or []:
            check(f"workflow {workflow['name']}/{task.get('id')} has a known kind",
                  task.get("kind") in planner_mod.KINDS, str(task.get("kind")))
            check(f"workflow {workflow['name']}/{task.get('id')} has a known mode",
                  task.get("mode") in ("passive", "active", "intrusive"), str(task.get("mode")))
            if task.get("vuln_class"):
                check(f"workflow {workflow['name']}/{task.get('id')} names a real class",
                      matrix.spec_for(task["vuln_class"]) is not None, task["vuln_class"])
            for dependency in task.get("inputs") or []:
                check(f"workflow {workflow['name']}/{task.get('id')} dependency exists",
                      dependency in ids, dependency)
            check(f"workflow {workflow['name']}/{task.get('id')} has acceptance criteria",
                  bool(task.get("done_when")))


def test_profiles() -> None:
    print("\nmodel profiles")
    known = set(profile_mod.known())
    for role, models in profile_mod.roles().items():
        for model in models:
            check(f"role {role} names a known model: {model}", model in known)
    for model in known:
        model_profile = profile_mod.load(model)
        check(f"profile {model} declares a provider", bool(model_profile.provider))
        check(f"profile {model} declares a family", model_profile.family != "unknown",
              model_profile.family)
        check(f"profile {model} has a sane step budget", 1 <= model_profile.max_steps <= 200,
              str(model_profile.max_steps))
        check(f"profile {model} has a tool dialect",
              model_profile.tool_dialect in ("anthropic", "openai", "google", "text", "mock"),
              model_profile.tool_dialect)


def test_runner_tool_sets() -> None:
    print("\nrunner tool sets")
    from argus.orchestrator.runner import TOOL_SETS
    for kind, prefixes in TOOL_SETS.items():
        for prefix in prefixes:
            check(f"tool set {kind} prefix {prefix} matches something",
                  any(name.startswith(prefix) for name in TOOL_NAMES), prefix)
        check(f"tool set {kind} includes the ledger",
              any(name.startswith("ledger.") for name in TOOL_NAMES
                  if name.startswith(tuple(prefixes))), str(prefixes))


# --- the CLI and the docs agree ---------------------------------------------

def cli_commands() -> set[str]:
    from argus.cli import build_parser
    parser = build_parser()
    for action in parser._actions:                                    # noqa: SLF001
        if getattr(action, "choices", None) and isinstance(action.choices, dict):
            return set(action.choices)
    return set()


def test_cli() -> None:
    print("\ncli")
    commands = cli_commands()
    check("the cli exposes commands", bool(commands))
    for command in sorted(commands):
        result = subprocess.run([sys.executable, "-m", "argus.cli", command, "--help"],
                                cwd=ROOT, capture_output=True, text=True, timeout=60, check=False)
        check(f"argus {command} --help works", result.returncode == 0,
              (result.stderr or "").strip()[-200:])


def test_docs_name_real_things() -> None:
    print("\ndocumentation")
    commands = cli_commands()
    for path in markdown_files():
        text = path.read_text(encoding="utf-8")
        relative = path.relative_to(ROOT)
        # `(?<![\w-])` so that "extending-argus\ndescription:" is not read as the
        # command `argus description`. The hyphen matters: \b alone matched it.
        for command in set(re.findall(r"(?<![\w-])argus\s+([a-z][a-z-]{2,})\b", text)):
            if command in ("plan", "run"):
                continue
            check(f"{relative} names a real argus command: {command}",
                  command in commands, f"not a subcommand; have {sorted(commands)}")
        # Not preceded by `/` and not a filename: `argus/ledger/proof.py` is a path,
        # not a tool call, and an earlier version of this check read it as one.
        # Every server name belongs in this alternation. A server missing from it
        # is a server whose tool names are never checked against the registry,
        # which is the one failure this check exists to prevent.
        for tool in set(re.findall(r"(?<![\w/.-])((?:recon|http|fuzz|scan|exploit|proof|web"
                                   r"|session|ledger|knowledge)\.[a-z_]+)(?![\w./-])", text)):
            if tool.endswith((".py", ".json", ".md")):
                continue
            check(f"{relative} names a real tool: {tool}", tool in TOOL_NAMES,
                  "no such tool in the broker")
        for reference in set(re.findall(r"`((?:argus|test|scripts|skills|workflows|docs)/"
                                        r"[A-Za-z0-9_./-]+)`", text)):
            target = ROOT / reference.rstrip("/.")
            check(f"{relative} names a real path: {reference}",
                  target.exists() or target.with_suffix(".py").exists(), str(target))


def test_proof_matrix_documented() -> None:
    print("\nproof matrix coverage")
    index = (ROOT / "skills" / "INDEX.md").read_text(encoding="utf-8")
    registry = read_json(ROOT / "skills" / "registry.json", {})
    covered = {klass for entry in registry.get("skills", [])
               for klass in (entry.get("classes") or [])}
    for entry in registry.get("skills", []):
        for klass in entry.get("classes") or []:
            check(f"skill {entry['name']} claims a class in the matrix: {klass}",
                  matrix.spec_for(klass) is not None or klass in matrix.CANDIDATE_ONLY, klass)
    undocumented = [name for name in matrix.classes()
                    if name != "dos" and name not in covered]
    # The gap is allowed; what is not allowed is an undocumented class that the
    # index does not admit to. A skills directory that looks complete when it is
    # not is worse than a short one that says where it ends.
    for name in undocumented:
        check(f"INDEX.md admits that {name} has no depth skill", name in index,
              "class has no depth skill and is not listed in the 'no depth skill yet' section")


def test_baseline() -> None:
    print("\nbaseline")
    baseline = read_json(ROOT / "test" / "baseline.json", {})
    actual = {
        "tools": len(TOOL_NAMES),
        "servers": len(SERVER_NAMES),
        "proof_classes": len(matrix.classes()),
        "playbook_classes": len(playbook.known_classes()),
        "skills": len(list((ROOT / "skills").glob("*/SKILL.md"))),
        "workflows": len(list((ROOT / "workflows").glob("*.json"))),
        "model_profiles": len(profile_mod.known()),
        "cli_commands": len(cli_commands()),
        "proof_cases": len((read_json(ROOT / "test" / "cases" / "proof_cases.json", {})
                            .get("cases") or [])),
    }
    for key, expected in (baseline.get("minimum") or {}).items():
        check(f"baseline {key} >= {expected}", actual.get(key, 0) >= expected,
              f"now {actual.get(key)}")
    print("  counts: " + ", ".join(f"{key}={value}" for key, value in actual.items()))


def test_mcp_handshake() -> None:
    print("\nmcp handshake")
    requests = [
        {"jsonrpc": "2.0", "id": 1, "method": "initialize",
         "params": {"protocolVersion": "2025-06-18", "capabilities": {},
                    "clientInfo": {"name": "gate", "version": "1"}}},
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
         "params": {"name": "proof.requirement", "arguments": {"vuln_class": "rce"}}},
        {"jsonrpc": "2.0", "id": 4, "method": "nonexistent/method"},
    ]
    stdin = "\n".join(json.dumps(request) for request in requests) + "\n"
    result = subprocess.run([sys.executable, "-m", "argus.broker.serve", "all"], cwd=ROOT,
                            input=stdin, capture_output=True, text=True, timeout=120, check=False)
    replies = [json.loads(line) for line in result.stdout.splitlines() if line.strip()]
    by_id = {reply.get("id"): reply for reply in replies}
    check("initialize answers with a protocol version",
          (by_id.get(1, {}).get("result") or {}).get("protocolVersion") == "2025-06-18",
          json.dumps(by_id.get(1, {}))[:200])
    check("tools/list returns every tool",
          len(((by_id.get(2, {}).get("result") or {}).get("tools") or [])) == len(TOOL_NAMES),
          str(len(((by_id.get(2, {}).get("result") or {}).get("tools") or []))))
    check("tools/call returns content and no error",
          (by_id.get(3, {}).get("result") or {}).get("isError") is False,
          json.dumps(by_id.get(3, {}))[:200])
    check("an unknown method answers with a JSON-RPC error",
          by_id.get(4, {}).get("error", {}).get("code") == -32601,
          json.dumps(by_id.get(4, {}))[:200])
    check("a notification produces no reply", None not in by_id or len(replies) == 4,
          f"{len(replies)} replies for 4 requests with ids")


def test_tool_contracts() -> None:
    print("\ntool contracts")
    for name, spec in SERVER.tools.items():
        check(f"{name} has a description", len(spec.description.strip()) > 40)
        check(f"{name} declares a tier", spec.tier in ("passive", "active", "intrusive"))
        schema = spec.schema
        check(f"{name} has an object schema", schema.get("type") == "object")
        for argument in schema.get("required") or []:
            check(f"{name} required argument {argument} is declared",
                  argument in (schema.get("properties") or {}), argument)
        if spec.touches_target and spec.vuln_class is None:
            check(f"{name} accepts a hypothesis id",
                  "hypothesis_id" in (schema.get("properties") or {}))
        if spec.proves:
            check(f"{name} proves a shape the matrix knows",
                  spec.proves in {matrix.spec_for(k).kind for k in matrix.classes()},
                  spec.proves)


def main() -> int:
    test_imports()
    test_skills()
    test_playbook()
    test_exploit_registry()
    test_workflows()
    test_profiles()
    test_runner_tool_sets()
    test_cli()
    test_docs_name_real_things()
    test_proof_matrix_documented()
    test_tool_contracts()
    test_mcp_handshake()
    test_baseline()
    print(f"\n{COUNT - len(FAILURES)}/{COUNT} consistency checks passed")
    if FAILURES:
        print("\nFAILURES:")
        for failure in FAILURES:
            print(f"  - {failure}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
