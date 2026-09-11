#!/usr/bin/env python3
"""Fail if CTF runtime files reference the machine/red-team runtime."""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
bad = ("/security-toolkit/", "knowledge-base", "solver/triage.py", "htb-machine-methodology", "linux-privesc")
hits = []
for base, dirs, names in os.walk(ROOT):
    dirs[:] = [d for d in dirs if d not in {".git", "__pycache__", "cache", "raw"}]
    for name in names:
        if not name.endswith((".py", ".md", ".yaml", ".json")):
            continue
        path = os.path.join(base, name)
        try:
            text = open(path, encoding="utf-8", errors="replace").read()
        except OSError:
            continue
        for token in bad:
            if token in text and path != os.path.abspath(__file__) and path not in (os.path.join(ROOT, "README.md"), os.path.join(ROOT, "DESIGN.md")):
                hits.append((path, token))
print("boundary: %d violation(s)" % len(hits))
for path, token in hits[:20]:
    print(path, token)
sys.exit(1 if hits else 0)
