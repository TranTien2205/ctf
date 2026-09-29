# tools/ad — the attack–defense control plane

Jeopardy and attack–defense are different games, and this tree was built for the
first one. `tools/hooks.py` gates **one** verified flag; `tools/decide.py` budgets
probes against **one** target; a chain card records **one** solve. None of that
fits a contest where the flag rotates every tick, where you are also the target,
and where the best source of exploits is your own inbound traffic.

So this is a sibling control plane, not a replacement. It does not write
`challenges/<name>/state.json` and it does not go through `hooks.py`. The
jeopardy loop is untouched.

Placed here rather than in a separate tree on purpose — the measurement behind
that choice is in the `ctf-v2-specialize-tools-not-split-tree` memory: `skills/`
does not bloat per-session load, and what was actually web-biased was `tools/`.

## The four assumptions that change

| Jeopardy (the rest of this tree) | Attack–defense (here) |
|---|---|
| one target, one flag, `hooks.py pre-flag` is the finish | flags rotate every tick; you need a farm, not a verdict |
| you only attack | you are also the target, and availability is scored |
| hypotheses come from source and chain cards | the best ones arrive in your own capture, written by other teams |
| a probe budget stops you sinking time | over-patching costs more than the exploit did |

## The tools

| File | What it is for |
|---|---|
| `sla_check.py` | run the service's own health checks; `--compare` refuses a patch that broke something which previously worked |
| `flag_farm.py` | run one exploit against every team every tick, submit new flags, and name the teams that have stopped yielding |
| `traffic_mine.py` | rank captured requests against a baseline and hand back a replay template — this is how you steal another team's exploit |
| `selftest.py` | offline proof of all of the above; no network, no sockets, no subprocess |
| `RUNBOOK.md` | the first thirty minutes, and the steady-state loop |

Each prints JSON on stdout, like the rest of the tree.

## The one output to read every tick

`flag_farm.py` prints `immune`: teams that returned nothing while others
returned flags. They have patched. Their patch is the shortest and most precise
description of the bug you are exploiting, and reading it is faster than
re-deriving it. That field is the reason this tool reports per-team rather than
a total.

## Guards, deliberately

`flag_farm.py` refuses to start unless the config names an `authorized_event`
and lists team hosts **individually**. There is no discovery and no CIDR
expansion, so it can only ever reach hosts the operator typed. This is a contest
tool for an authorized event, and it is shaped so it cannot quietly become
something else. `CLAUDE.md` scopes this repo to authorized CTF and lab work,
jeopardy and attack–defense; that scope is what this directory is for.

## Status — read this before trusting any of it

**None of this has been executed.** It was written while the sandbox in that
session refused to run Bash, so every file here is unrun code.

It has, however, been read back line by line, and that review found four real
defects which are already fixed. They are listed because they say what kind of
mistake to look for in the rest:

- `traffic_mine.score()` matched only the raw query and body. Real payloads are
  URL-encoded, so `id=1'%20OR%201=1--` never matched a pattern written with
  `\s+`, and the SQL case in the selftest would have failed. It now scans the
  path as well, and both the raw and the URL-decoded form.
- the Java serialization magic bytes `AC ED 00 05` were unmatchable: the capture
  is decoded with `errors="replace"`, so those bytes arrive as U+FFFD. Replaced
  with `rO0AB`, the same header in the base64 form it travels in.
- `flag_farm.run_exploit()` scanned only stdout, and carried a leftover
  `proc.returncode * ""`. It now scans stderr too — losing a flag because the
  exploit printed it to the other pipe is a silly way to lose points.
- `flag_farm.tick()` compared `t.get("id") != cfg.get("skip_self")`, which
  silently dropped every team with no id when `skip_self` was unset.

What that review cannot catch is anything that only shows up at runtime, so:

- `python3 tools/ad/selftest.py` has **not** been run. Run it first; it is
  offline and exercises the decision logic of all three tools.
- `test/run_all.sh` has **not** been run since these files were added, and the
  gate is what makes a change count in this tree.
- The tools are not yet listed in `AGENTS.md`. The gate checks that new tooling
  is documented, so it will likely fail until the rows below are added — and
  `AGENTS.md` edits are supposed to be approved first, which is why they are
  proposed here rather than applied.

Proposed rows for the `AGENTS.md` tool table:

| Tool | Use it when |
|---|---|
| `tools/ad/sla_check.py` | attack–defense: before and after every patch. `--compare` exits non-zero when a check that used to pass now fails, which is the only signal that should block a patch |
| `tools/ad/flag_farm.py` | attack–defense: one exploit against every team every tick, with duplicate suppression and a per-team `immune` list that names who has already patched |
| `tools/ad/traffic_mine.py` | attack–defense: rank your own captured traffic against a baseline to recover another team's working exploit, with a ready replay command |

And a line for the tool-layer selftest block in `test/run_all.sh`, next to
`tools/web/selftest.py`:

```
python3 tools/ad/selftest.py
```

## What is still missing

Tools are the control plane; the knowledge layer is not built yet. Per the
`ctf-v2-taxonomy-is-generated` memory, bug classes come from
`build/make_bug_classes.py` and each needs its own `skills/<id>/` directory, a
`field-notes.md`, a `registry.json` entry, and the generators re-run — none of
which can be done without a working shell. Candidates, in order of expected
return:

1. `ad-traffic-mining` — the skill behind `traffic_mine.py`. Highest return of
   anything in this list.
2. `ad-patch-without-breaking-sla` — where to patch (in front of the service or
   in its source), how to keep legitimate behaviour, how to roll back.
3. `ad-service-triage` — a router: given a service, find the flag store, the
   endpoints that reach it, and the author's deliberate oddity. Close enough to
   the existing `white-box-intended-path` to build on it.
4. `ad-persistence-and-backdoor-hunt` — not DFIR-as-history but "find what the
   organiser planted, in thirty minutes, before anyone uses it".

The eight `dfir-*` skills already in the tree cover the incident-response half
of the scenario, but every one of them is `catalogue`: standard published
knowledge with no solve in this tree behind it. Treat them as checklists.
