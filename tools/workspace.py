#!/usr/bin/env python3
"""Provision the agents' workspace for one challenge, outside this repository.

Two zones, deliberately. `/home/kali/ctf-work` is where subagents have full
rights: they write exploits, save responses and leave notes there, and nothing in
it is load-bearing for the toolkit. This repository is the other zone -- agents
read it constantly and write to it never.

Before this existed each agent invented its own layout under /tmp, which cost a
measured failure: two agents chose the same scratch path and one deleted the
other's staged work mid-run. A named layout with a private per-agent directory
removes the collision, and a persistent workspace means what an agent produces
survives for the main thread and for the next agent.

    python3 tools/workspace.py <challenge>              # create and print the paths
    python3 tools/workspace.py <challenge> --agent web-session
    python3 tools/workspace.py --list
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WORK = os.environ.get("CTF_WORKSPACE", "/home/kali/ctf-work")


def paths_for(challenge, agent=None):
    base = os.path.join(WORK, "challenges", challenge)
    out = {
        "workspace_root": WORK,
        "challenge": base,
        "artifacts": os.path.join(base, "artifacts"),
        "exploits": os.path.join(base, "exploits"),
        "notes": os.path.join(base, "notes.md"),
        "agents": os.path.join(base, "agents"),
        "shared": os.path.join(WORK, "shared"),
    }
    if agent:
        out["agent_dir"] = os.path.join(base, "agents", agent)
    return out


def provision(challenge, agent=None):
    p = paths_for(challenge, agent)
    for key in ("artifacts", "exploits", "agents", "shared"):
        os.makedirs(p[key], exist_ok=True)
    if agent:
        os.makedirs(p["agent_dir"], exist_ok=True)
    if not os.path.exists(p["notes"]):
        with open(p["notes"], "w", encoding="utf-8") as fh:
            fh.write("# %s — shared notes\n\n"
                     "Anything the next agent or the main thread should read. Append;\n"
                     "do not rewrite another agent's section.\n" % challenge)
    return p


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("challenge", nargs="?")
    ap.add_argument("--agent", help="also create this agent's private subdirectory")
    ap.add_argument("--list", action="store_true", help="what already exists")
    a = ap.parse_args()

    if a.list or not a.challenge:
        base = os.path.join(WORK, "challenges")
        rows = []
        for name in sorted(os.listdir(base)) if os.path.isdir(base) else []:
            d = os.path.join(base, name)
            if not os.path.isdir(d):
                continue
            files = sum(len(f) for _, _, f in os.walk(d))
            agents = os.path.join(d, "agents")
            rows.append({"challenge": name, "files": files,
                         "agents": sorted(os.listdir(agents))
                         if os.path.isdir(agents) else []})
        print(json.dumps({"workspace_root": WORK, "challenges": rows,
                          "note": "agents have FULL rights here; this repository is "
                                  "read-only for them"}, indent=2))
        return 0

    p = provision(a.challenge, a.agent)
    p["rules"] = [
        "full rights inside workspace_root; never write into the ctf-v2 repository",
        "work in agent_dir, and never delete anything above it -- agents run in "
        "parallel and have already destroyed each other's work by sharing a path",
        "an exploit the main thread should run goes in exploits/",
        "anything the next agent should read is APPENDED to notes.md",
    ]
    print(json.dumps(p, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
