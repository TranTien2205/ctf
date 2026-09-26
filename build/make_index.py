#!/usr/bin/env python3
"""Regenerate skills/INDEX.md from the registry and the bug-class taxonomy.

The prose is written here; the tables are generated, so the index cannot claim a
skill that does not exist or miss one that does.
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "skills", "INDEX.md")

PROLOGUE = """# Skill Index — the only routing table

This file, `skills/registry.json` and `knowledge/bug-classes.json` are the single
source of truth for which skill to open. `SKILL_GUIDE.md`, `ctf.py` and every
SKILL.md defer to them. `test/regression.py` fails if a path here does not exist,
if a skill on disk is missing from the registry, or if a bug class has no skill.

Ask the tools instead of reading these tables by eye:

```bash
python3 tools/classify.py     "<observation>"   # or --source <path>  -> bug class
python3 tools/skill_select.py "<observation>"   # or --source <path>  -> which skill
python3 tools/chain_match.py  "<observation>"   # or --source <path>  -> solved chains
```

`classify.py` names the bug class and its first probe. `skill_select.py` returns
exactly one router and at most one depth skill. `chain_match.py` says whether this
shape has already been solved here.

## Why the discipline exists

The depth corpus is roughly {corpus_tokens:,} tokens across {corpus_files} files. Opening
`skills/{biggest_dir}/` alone is about {biggest_tokens:,}. A router is 100–1,300 tokens and a
bug-class skill 500–1,200. Reading a corpus before a probe has produced a signal
costs a large share of the context window and anchors the next hypothesis on
whatever that file happened to describe.

## Load order (hard rule)

```
1 entry     ctf-playbook            classify + time-box          (always, once)
2 router    <category>-triage       signal -> class -> probe      (exactly one)
3 probe     run the cheapest discriminating probe                 (before any depth)
4 class     one bug-class skill     only after its signal fired
5 reference one named file          never a whole directory
```

Open counts: entry 1, router 1, depth 1, reference at most 2. To change category,
re-run `tools/skill_select.py`; never open a second router to browse.

## Evidence levels

Every bug-class skill declares one, and it changes how much weight its content
carries:

| Level | Meaning |
|---|---|
| `verified` | a chain card in `knowledge/chains/` proves this class was solved here |
| `catalogue` | a real, standard class that nothing here has solved yet — a starting point, not local experience |

A catalogue skill is never presented as experience. Promotion happens through the
loop in `LEARNING_LOOP.md`, never by editing the label.
"""

EPILOGUE = """
## Skills that are not routed to automatically

`ctf-writeup` is opened after a flag is verified, to record the chain.
`security-skill-evaluation` is opened when judging whether a skill earns its
place. `ctf-malware` is reached from `rev-triage` or `forensics-triage`.
`ctf-playbook` is the entry point and is never a depth target.

## Chain reuse comes before depth

```bash
python3 tools/chain_match.py "<observation>"
python3 tools/chain_match.py --source ./challenge-src
```

A matching chain supplies a candidate and its cheapest confirming probe. It is
never proof. Scoring, preconditions and the mismatch rule are in
`HYPOTHESIS_PROTOCOL.md`.

## Adding a bug class

1. Add the class to `build/make_bug_classes.py` with signals, first probe and
   falsifier. Start it at `catalogue` unless a chain card already proves it.
2. `python3 build/make_bug_classes.py` then `python3 build/make_class_skills.py`
   to generate the skill and its `field-notes.md`.
3. `python3 build/make_registry.py` and `python3 build/make_index.py`.
4. `bash test/run_all.sh`. A class without a skill, or a skill missing from the
   registry, fails the gate.

## Adding any other skill

Directory with `SKILL.md`, an entry in `build/make_registry.py` under `PORTED`
(or hand-written in the registry), then regenerate and run the gate.
"""


def main():
    with open(os.path.join(ROOT, "skills", "registry.json"), encoding="utf-8") as handle:
        registry = json.load(handle)
    with open(os.path.join(ROOT, "knowledge", "bug-classes.json"), encoding="utf-8") as handle:
        taxonomy = json.load(handle)
    by_id = {entry["id"]: entry for entry in registry["skills"]}

    # Measure the corpus instead of asserting a remembered size. The prose used
    # to hardcode "622,000 tokens across 190 files"; the tree had grown to 309
    # files and ~759,000 tokens, so the one number the index exists to justify
    # was the number it got wrong.
    corpus_files = corpus_bytes = 0
    per_dir = {}
    skills_root = os.path.join(ROOT, "skills")
    for base, dirs, names in os.walk(skills_root):
        for name in names:
            if not name.endswith(".md"):
                continue
            size = os.path.getsize(os.path.join(base, name))
            corpus_files += 1
            corpus_bytes += size
            top = os.path.relpath(base, skills_root).split(os.sep)[0]
            per_dir[top] = per_dir.get(top, 0) + size
    biggest = max(per_dir.items(), key=lambda kv: kv[1]) if per_dir else ("", 0)
    prologue = PROLOGUE.format(corpus_tokens=round(corpus_bytes / 4, -3).__int__(),
                               corpus_files=corpus_files,
                               biggest_dir=biggest[0],
                               biggest_tokens=round(biggest[1] / 4, -3).__int__())

    lines = [prologue, "", "## Category routers", "",
             "| Observed evidence | Router | Tokens | Next |", "|---|---|---|---|"]
    router_hint = {
        "web-triage": "HTTP target, web framework, web source",
        "pwn-binary-triage": "ELF/PE plus input, crash, checksec",
        "rev-triage": "binary, bytecode or firmware to understand",
        "crypto-triage": "ciphertext, modulus, nonce, hash",
        "forensics-triage": "PCAP, disk, memory, media, logs",
        "osint-triage": "name, handle, photo, domain in public sources",
        "ai-iot-triage": "LLM endpoint, model file, IoT firmware or protocol",
        "ctf-misc": "jail, encoding chain, game or VM, programming task",
    }
    for entry in registry["skills"]:
        if entry["layer"] != "router":
            continue
        nxt = ", ".join("`%s`" % t for t in entry["routes_to"][:3]) or "—"
        if len(entry["routes_to"]) > 3:
            nxt += " …"
        lines.append("| %s | `%s` | ~%.1fk | %s |" % (
            router_hint.get(entry["id"], entry["id"]), entry["path"],
            entry["skill_tokens"] / 1000, nxt))

    lines += ["", "`ctf-misc` is both router and depth for its category, and it is the last",
              "resort: try a named category first.", "",
              "## Web bug classes", "",
              "Open one only after a probe or a source read produced its signal.", "",
              "| Class | Evidence | Closed when (falsifier) | Skill |", "|---|---|---|---|"]
    for cls in taxonomy["classes"]:
        entry = by_id.get(cls["id"])
        if entry is None:
            continue
        mark = "verified" if cls["evidence_level"] == "verified" else "catalogue"
        lines.append("| %s | %s | %s | `%s` |" % (
            cls["name"], mark, cls["falsifier"].split(",")[0][:72], cls["skill"]))

    lines += ["", "Full signal lists, first probes and blast-radius notes are in",
              "`knowledge/bug-classes.json`. Do not copy them here — the classifier reads",
              "that file and this table would drift.", "",
              "## Supporting depth skills", "",
              "| Skill | Layer | Tokens | Opened when |", "|---|---|---|---|"]
    extra_when = {
        "ctf-web": "a narrower web class lacked the variant; open one named file",
        "ctf-pwn": "the crash is reproduced and a named technique is needed",
        "ctf-reverse": "the runtime or packer is named",
        "ctf-crypto": "the primitive parameters are collected",
        "ctf-forensics": "the artifact type is identified",
        "ctf-osint": "one unique pivot is extracted",
        "ctf-ai-ml": "the AI/IoT sub-type is decided",
        "ctf-malware": "obfuscated script, PE/.NET sample, or captured C2 traffic",
        "pwn-rop": "instruction-pointer control is proven and NX forces code reuse",
        "web-chromedriver": "an admin bot exists and a client-side payload needs debugging",
        "web-websocket": "a ws:// channel or realtime feature carries the flag path",
        "web-source-map": "the front-end bundle is the only available source",
        "web-xs-leaks": "an HttpOnly cookie blocks XSS and a bot visits attacker pages",
        "web-info-disclosure": "an exposed file, debug route, or verbose error is observed",
        "mcp-agent-security": "the target is an LLM, an agent, or a tool server",
        "ctf-writeup": "a flag is verified and the chain must be recorded",
        "security-skill-evaluation": "a skill is being added, promoted, or removed",
    }
    for entry in registry["skills"]:
        if entry.get("bug_class") or entry["layer"] in ("entry", "router"):
            continue
        lines.append("| `%s` | %s | ~%.1fk | %s |" % (
            entry["path"], entry["layer"], entry["skill_tokens"] / 1000,
            extra_when.get(entry["id"], "see registry use_when")))

    lines.append(EPILOGUE)
    with open(OUT, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))
    print(json.dumps({"written": os.path.relpath(OUT, ROOT),
                      "routers": sum(1 for e in registry["skills"] if e["layer"] == "router"),
                      "classes": len(taxonomy["classes"]),
                      "other_depth": sum(1 for e in registry["skills"]
                                         if not e.get("bug_class")
                                         and e["layer"] in ("depth", "reference"))}))


if __name__ == "__main__":
    main()
