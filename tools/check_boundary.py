#!/usr/bin/env python3
"""Fail if anything in this tree teaches machine, Active Directory or box work.

This tree is jeopardy CTF only. Machine boxes, Active Directory and box
privilege escalation belong to the other toolkit, and the rule is easy to break
by accident: a skill gets ported, an example gets copied, and a Kerberoasting
walkthrough ends up sitting next to the SSTI notes.

The guard is deliberately about *methodology* terms, not technique names. A
kernel exploit or a SUID binary can be the whole point of a jeopardy challenge,
so those are not blocked; "Kerberoasting to Domain Admin" cannot be.

Run by `test/run_all.sh` as a required step. Exit 1 on any violation.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Machine, AD and cross-toolkit markers. Lower-cased before matching.
BLOCKED = (
    # cross-toolkit paths and skill names
    "/security-toolkit/",
    "knowledge-base",
    "solver/triage.py",
    "htb-machine-methodology",
    "linux-privesc",
    "ad-enumeration",
    # named Active Directory attack tooling and methodology
    "bloodhound",
    "rubeus",
    "crackmapexec",
    "netexec",
    "certipy",
    "path to domain admin",
    "dcsync",
    "golden ticket",
    "silver ticket",
    "pass-the-hash",
    "ntlm relay",
)
# Deliberately NOT blocked, because they have real jeopardy uses in this tree:
# secretsdump and kerberoast (offline hive and PCAP analysis in ctf-forensics),
# "lateral movement" (detecting it in logs), "active directory" and "domain
# controller" (naming the boundary, or describing a capture). A substring guard
# cannot judge intent, so it only carries markers that have no CTF reading.

# Files whose job is to STATE the boundary, so they must be able to name it.
# Keep this list short: every entry is a file that can mention the other toolkit
# without teaching it.
DECLARES_BOUNDARY = {
    "README.md", "DESIGN.md", "AGENTS.md", "CLAUDE.md", "PROMPT.md",
    "SYSTEM_AUDIT.md", "V2_CHANGES.md", "SKILL_GUIDE.md",
    "tools/check_boundary.py", "test/regression.py", "test/gate-exemptions.json",
    "skills/ctf-misc/jails-and-shells.md",
}

# ".claude" holds git worktrees that agents run in. Each is a full copy of the
# tree, including THIS file, so scanning them reports this file's own marker
# list as a violation. A worktree is a transient checkout, not authored
# content, and the real copy is scanned anyway.
SKIP_DIRS = {".git", ".claude", "__pycache__", "cache", "raw", "challenges"}


def violations():
    hits = []
    for base, dirs, names in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in names:
            if not name.endswith((".py", ".md", ".yaml", ".json", ".sh")):
                continue
            path = os.path.join(base, name)
            rel = os.path.relpath(path, ROOT).replace(os.sep, "/")
            if rel in DECLARES_BOUNDARY:
                continue
            try:
                text = open(path, encoding="utf-8", errors="replace").read().lower()
            except OSError:
                continue
            for token in BLOCKED:
                if token in text:
                    hits.append((rel, token))
    return hits


def main():
    hits = violations()
    print("boundary: %d violation(s)" % len(hits))
    for rel, token in hits[:20]:
        print("  %s  ->  %s" % (rel, token))
    if hits:
        print("\nThis tree is jeopardy CTF only. Move the content to the machine "
              "toolkit, or rewrite the example in CTF terms.")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
