#!/usr/bin/env python3
"""Check that every attack-defense subagent definition still says what it must.

A prohibition in a prompt is decorative until something reads it back. This does
that: it parses each `.claude/agents/ad-*.md`, confirms the frontmatter restricts
the tool list at all, confirms the write capability is DECLARED rather than left
to be inferred, and confirms the canonical prohibition block is present verbatim.

    python3 tools/ad/agent_lint.py
    python3 tools/ad/agent_lint.py --json

The one design point worth stating: an agent's read-only status is enforced by its
`tools:` line, not by its prose. An agent with no Bash and no Edit physically
cannot send a request or change a file, whatever its prompt says. So the check
that matters most here is check 3 -- a missing or `*` tool list leaves the
restriction undefined and the subagent inherits everything.

Stdlib only, and deliberately not YAML. PyYAML is present on this box, but a step
the gate depends on should not need a third-party package. The frontmatter format
is therefore narrow on purpose: a first line that is exactly `---`, a closing
`---`, and `key: value` split on the first colon.

`audit()` never raises. A missing directory or an unreadable file becomes an entry
in `failures`, because a traceback inside the offline selftest fails the whole gate
with no useful message.

Output is JSON on stdout, like every other tool in this tree. Exit 0 when
`failures` is empty; warnings never fail the gate, because the one deliberate
FILL-IN below has to survive until the estate's real path is known on the day.
"""
import argparse
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
AGENT_DIR = os.path.join(ROOT, ".claude", "agents")
PROHIBITIONS = os.path.join(ROOT, "agent", "ad-prohibitions.md")
ROLES = os.path.join(ROOT, "agent", "ad-roles.md")
PREFIX = "ad-"

# A tool entry that can change a file or send a request. `Bash` is listed bare
# because a scoped Bash(...) entry is narrower and is handled separately.
WRITE_TOOLS = ("Write", "Edit", "NotebookEdit")
MIN_DESCRIPTION = 40
# The sentence every prohibition block must contain, chosen because it is the one
# an agent is most likely to reason its way around.
PROHIBITION_ANCHOR = "these are not preferences"


def split_frontmatter(text):
    """(frontmatter dict, body) or (None, reason)."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return None, "the file does not open with a --- frontmatter line"
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            front = {}
            for raw in lines[1:index]:
                if not raw.strip() or raw.lstrip().startswith("#"):
                    continue
                key, sep, value = raw.partition(":")
                if not sep:
                    continue
                front[key.strip()] = value.strip()
            return front, "\n".join(lines[index + 1:])
    return None, "the frontmatter is never closed by a second --- line"


def tool_entries(value):
    """'Read, Grep, Bash(python3 x:*)' -> ['Read', 'Grep', 'Bash(python3 x:*)']."""
    out, depth, current = [], 0, ""
    for char in value:
        if char == "(":
            depth += 1
        elif char == ")":
            depth = max(0, depth - 1)
        if char == "," and depth == 0:
            out.append(current.strip())
            current = ""
        else:
            current += char
    if current.strip():
        out.append(current.strip())
    return [entry for entry in out if entry]


def declares_write(entries):
    """True when a tool on the list can change a file or run an arbitrary command."""
    for entry in entries:
        bare = entry.split("(")[0].strip()
        if bare in WRITE_TOOLS:
            return True
        if bare == "Bash" and "(" not in entry:
            return True
    return False


def check_agent(path, prohibition_text):
    """Every failing and warning check for one agent file. Never raises."""
    name = os.path.basename(path)
    stem = name[:-3] if name.endswith(".md") else name
    failures, warnings = [], []

    def fail(check, detail):
        failures.append({"file": name, "check": check, "detail": detail})

    def warn(check, detail):
        warnings.append({"file": name, "check": check, "detail": detail})

    try:
        with open(path, encoding="utf-8") as handle:
            text = handle.read()
    except OSError as exc:
        fail("readable", "cannot read the file: %s" % exc)
        return failures, warnings

    front, body = split_frontmatter(text)
    if front is None:
        fail("frontmatter", body)
        return failures, warnings

    # 1. the name matches the filename, so which one resolves the subagent is moot
    if front.get("name") != stem:
        fail("name", "name is %r but the filename stem is %r; keep them equal so it "
                     "does not matter which one the runner resolves"
             % (front.get("name"), stem))

    # 2. a description short enough to be useless is worse than none: the runner
    #    selects on it
    description = front.get("description") or ""
    if len(description) < MIN_DESCRIPTION:
        fail("description", "description is %d characters; under %d is not enough for "
                            "a runner to pick this agent over another"
             % (len(description), MIN_DESCRIPTION))

    # 3. THE check. An undefined tool list means the subagent inherits everything,
    #    and read-only status becomes prose rather than enforcement.
    raw_tools = front.get("tools")
    entries = tool_entries(raw_tools or "")
    if raw_tools is None:
        fail("tools", "no tools line: the restriction is undefined, so the subagent "
                      "inherits every tool including the ones that can restart a service")
    elif not entries:
        fail("tools", "the tools line is empty")
    elif any(entry.strip() == "*" for entry in entries):
        fail("tools", "tools contains '*', which grants everything and is the same as "
                      "having no tools line at all")

    # 4. write capability is DECLARED, never inferred
    writes = declares_write(entries)
    want = "WRITE-CAPABLE: yes" if writes else "WRITE-CAPABLE: no"
    other = "WRITE-CAPABLE: no" if writes else "WRITE-CAPABLE: yes"
    if want not in body:
        fail("write-declared",
             "tools %s a file-changing entry, so the body must contain the line %r"
             % ("carry" if writes else "carry no", want))
    elif other in body:
        fail("write-declared", "the body contains both %r and %r" % (want, other))

    # 5. the prohibitions, verbatim. A paraphrase is how a rule quietly softens.
    if PROHIBITION_ANCHOR not in body:
        fail("prohibitions", "the body does not carry the prohibition block "
                             "(anchor %r missing)" % PROHIBITION_ANCHOR)
    else:
        missing = [line.strip() for line in prohibition_text.split("\n")
                   if line.strip().startswith(tuple("123456789"))
                   and line.strip() not in [b.strip() for b in body.split("\n")]]
        if missing:
            warn("prohibitions-verbatim",
                 "%d numbered prohibition line(s) are not byte-identical to "
                 "agent/ad-prohibitions.md; re-copy the block" % len(missing))

    # 6. every repository path the prose names has to exist, or the agent sends the
    #    operator to a file that is not there
    for ref in sorted(set(re.findall(r"tools/[A-Za-z0-9_./-]+\.(?:py|md|sh)", text))):
        if not os.path.isfile(os.path.join(ROOT, ref)):
            fail("paths", "names %s, which does not exist" % ref)

    # 7. the deliberate placeholder. A warning, never a failure: the estate's real
    #    path is unknown until the day, and narrowing it by hand is a preflight step.
    if "FILL-IN" in text:
        warn("fill-in", "carries a FILL-IN marker that must be resolved at preflight")

    return failures, warnings


def audit():
    """The whole check, as one dict. Never raises."""
    failures, warnings, agents = [], [], []

    prohibition_text = ""
    if not os.path.isfile(PROHIBITIONS):
        failures.append({"file": "agent/ad-prohibitions.md", "check": "exists",
                         "detail": "the canonical prohibition block is missing, so "
                                   "there is nothing for an agent to carry"})
    else:
        try:
            with open(PROHIBITIONS, encoding="utf-8") as handle:
                prohibition_text = handle.read()
        except OSError as exc:
            failures.append({"file": "agent/ad-prohibitions.md", "check": "readable",
                             "detail": str(exc)})

    roles_rows = 0
    if not os.path.isfile(ROLES):
        warnings.append({"file": "agent/ad-roles.md", "check": "exists",
                         "detail": "no roles index, so a runner that does not read "
                                   ".claude/agents/ cannot discover these agents"})
    else:
        try:
            with open(ROLES, encoding="utf-8") as handle:
                roles_text = handle.read()
            roles_rows = sum(1 for line in roles_text.split("\n")
                             if line.startswith("|") and PREFIX in line)
        except OSError as exc:
            warnings.append({"file": "agent/ad-roles.md", "check": "readable",
                             "detail": str(exc)})

    if not os.path.isdir(AGENT_DIR):
        failures.append({"file": ".claude/agents", "check": "exists",
                         "detail": "the agent directory does not exist"})
    else:
        for name in sorted(os.listdir(AGENT_DIR)):
            if not (name.startswith(PREFIX) and name.endswith(".md")):
                continue
            agents.append(name)
            agent_failures, agent_warnings = check_agent(
                os.path.join(AGENT_DIR, name), prohibition_text)
            failures.extend(agent_failures)
            warnings.extend(agent_warnings)

    if not agents:
        warnings.append({"file": AGENT_DIR, "check": "population",
                         "detail": "no %s*.md agent definitions found" % PREFIX})
    elif roles_rows and roles_rows < len(agents):
        warnings.append({"file": "agent/ad-roles.md", "check": "index-complete",
                         "detail": "%d agents on disk but %d rows name one in the index"
                                   % (len(agents), roles_rows)})

    return {"mode": "ad-agent-lint", "agents": len(agents), "agent_files": agents,
            "roles_rows": roles_rows, "failures": failures, "warnings": warnings}


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true",
                        help="print on one line instead of indented")
    args = parser.parse_args()
    report = audit()
    print(json.dumps(report, ensure_ascii=False,
                     indent=None if args.json else 1))
    return 1 if report["failures"] else 0


if __name__ == "__main__":
    sys.exit(main())
