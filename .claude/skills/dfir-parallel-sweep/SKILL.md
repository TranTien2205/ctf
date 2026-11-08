---
name: dfir-parallel-sweep
description: >
  Run an artifact-bundle investigation as eight bounded measurements at once
  instead of one artifact family at a time. Split the bundle by artifact family
  with subagent_fanout --dfir, spawn one ctf-dfir-* subagent per family, and merge
  the returned measurements through a validator that refuses any report claiming
  more than it measured. Use it on a Sherlock or a triage collection with many
  questions over one bundle; skip it for a single question answerable from one
  artifact, and never let it become eight parallel guesses.
tags: [process, method, subagents, fan-out, dfir, forensics, falsifier, ctf]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 2
  on_stuck: pivot
  stop_conditions:
    - "a report arrives whose evidence is not a verbatim artifact excerpt"
    - "two sweeps produce no family whose falsifier broke"
    - "a family reports a missing parser and no install has been attempted"
evidence_level: catalogue
---
# DFIR parallel sweep — Process Skill

**Catalogue method.** No chain card proves the *sweep*. One Sherlock has now been
solved in this tree — Brutus, 2026-10-01, which raised
`dfir-authentication-trace` to **verified** — but it was answered by working two
artifacts directly, not by fanning out, so it is evidence about the Linux
primitives and not about this procedure. `tools/subagent_fanout.py --dfir` reports
the real state in `chain_recall` rather than pretending to look. Treat what follows
as a procedure, not as experience of a solve.

What grounds it is the shape of the work, which is measurably different from a web
challenge in two ways that change the whole structure.

## Why this is not the web sweep with different nouns

**One investigation QUESTION is one challenge.** A Sherlock ships a numbered list
of questions over a single bundle. `tools/decide.py` budgets 25 probes and 45
active minutes **per challenge**, which fits one question and not twenty — so
twenty questions are twenty `state.py` challenges, named `<sherlock>-q1`,
`<sherlock>-q2`, and parked and revived independently. Treating the whole Sherlock
as one challenge spends the budget on question 3 and then forces a class switch on
seventeen questions nobody worked.

**There is no target, so there is no write.** Every artifact is supplied and
static. The web sweep has exactly one write-shaped family (`race`) that proposes
and hands back; the DFIR sweep has **none**, and a regression test enforces that.
There is no `--write-budget` to grant and no blast radius to read, which makes
every family safe to run in parallel without coordination.

A third difference is about this machine rather than the category: **most Windows
artifact families have no parser installed here.** `evtx_dump`, `chainsaw`,
`hayabusa`, python `Evtx`, `regipy`, `python-registry`, `volatility3` and `plaso`
are all absent, and `pip` is EXTERNALLY-MANAGED. So a family's first honest answer
is often "present but unparseable today, and this is the install". That is a
`transport` result — evidence about this box, never about the host under
investigation — and it can never confirm anything.

## When not to use it

- **One question answerable from one artifact.** Open the router, read the one
  depth file, answer it. A fan-out costs 7–10 minutes per agent whatever the task.
- **`chain_recall` reports `cards_exist`.** Once this tree has solved a Sherlock,
  a matching card beats eight parallel guesses — run its probe first.
- **Nothing is extracted yet.** `--dfir` wants the *extracted* directory. Run the
  recon family, or `tools/forensics/artifact_inventory.py`, first.

## First probe

Do not open a parser. Split the bundle, and look at what it actually contains:

```bash
python3 tools/subagent_fanout.py --dfir <extracted-bundle-dir> \
        --challenge <sherlock>-q1
```

Every class field in the output is read from `knowledge/bug-classes.json` — each
class's own `first_probe`, `falsifier`, `skill`, `depth_refs` and `evidence_level`
— plus `already_measured_dead_elsewhere` drawn from every kill map in
`knowledge/attempts/`.

The DFIR-specific field is **`artifacts_that_fired`**, and it exists because a
Sherlock ships no application source: every `dfir-*` class carries
`source_signals: []` on purpose, so a source grep matches nothing. What stands in
for it is the bundle inventory — each class's `observation_signals` matched against
the artifact **filenames** first and a bounded read of the small **text** files
second, with `where` saying which. The walk is capped (20k files, 400 text files,
256 KB each) because the bundle corpus on this box is 44 GB, and a truncated walk
reports `walk_truncated: true` rather than hiding it.

The first probe answers one question:

> **Which artifact families does this bundle actually contain, and which of them
> can this machine read today?**

A family whose `artifacts_that_fired` is empty is the cheapest to **park**, not to
run: nothing in the bundle points at it.

## The eight families

| Family | Subagent | What it owns |
|---|---|---|
| recon | `ctf-dfir-recon` | the artifact inventory, and which families are parseable today |
| linux | `ctf-dfir-linux` | the **Linux** half: auth.log, wtmp/btmp, journald, sudo, cron, systemd, authorized_keys |
| windows-events | `ctf-dfir-windows-events` | the **Windows event-log** half: logons, process creation, script blocks, cleared logs |
| registry-execution | `ctf-dfir-registry-execution` | the **on-disk** half: Run keys, Services, TaskCache, WMI, Amcache, ShimCache, Prefetch |
| filesystem | `ctf-dfir-filesystem` | the **timestamp** half: one UTC axis over `$MFT`/`$J`, and SI versus FN for timestomping |
| network | `ctf-dfir-network` | captures and flow logs: per-peer volume, DNS, SNI, beacon periodicity |
| cloud | `ctf-dfir-cloud` | CloudTrail, S3 access, VPC flow, Azure sign-in, M365 unified audit |
| memory-malware | `ctf-dfir-memory-malware` | a memory image or a sample, **statically**. Owns no taxonomy class and hands its indicators to the family that does |

Between them they cover all seven `dfir-*` classes in the taxonomy, and a
regression test fails if
any class is left without a family.

**Three classes are owned by two families each, and the split is explicit.**
`dfir-execution-trace` is answerable from the event log *or* from what persisted on
disk; `dfir-antiforensics-trace` splits into a cleared-log half and a timestamp
half; `dfir-authentication-trace` splits Windows from Linux. Every such family
carries an `owns` field, and a second regression test fails if one does not — read
`owns` before spawning both, or two agents measure the same artifact and the main
thread cannot tell which report answered the question.

The grouping is by **probe**, exactly as in the web sweep: `linux` and
`windows-events` cover the same three classes and are still separate families,
because `tools/forensics/linux_auth.py` and a converted EVTX record set have
nothing in common — not the artifact, not the parser, not the traps.

## The sweep

Spawn the surviving families **in one message so they run concurrently**. Run
`recon` **first and alone**: every other family routes against its inventory, and
it is what tells you which families are blocked on an absent parser. Three to five
is the useful range after that; eight at once is a sweep, not a wave.

While they run, **you drive the spine yourself**: read the question list, decide
which questions depend on which, and create the `state.py` challenge for the one
you are working.

Then validate before believing any of it:

```bash
python3 tools/subagent_fanout.py --validate report.json
python3 tools/subagent_fanout.py --merge reports/*.json --challenge <sherlock>
```

`--merge` prints the commands for **you** to run, and for a `dfir-*` class it
prints a **`pre-flag` template, not `post-probe`** — because a Sherlock answer is a
fact read from a supplied artifact rather than a verdict won by a probe:

```bash
python3 tools/hooks.py pre-flag <sherlock>-qN --value '<ANSWER>' \
  --source artifact --evidence '<verbatim record excerpt>'
```

The `<ANSWER>` placeholder is deliberate. Mapping a measured record to the value a
numbered question actually asked for is a judgement, and a tool that guessed it
would be inventing the one field nobody can check afterwards. A family that
measured and found nothing emits a line for `knowledge/attempts/<challenge>.json`
instead, so the next attempt does not re-walk a dead artifact family.

## The failures this method has, and the guard for each

**A subagent summarising instead of quoting.** "The log shows a successful logon"
is hypothesizer output; the evidence is the record's own bytes.
`--validate` refuses a report whose `evidence` is not a verbatim substring of its
own `response_excerpt` — and every `tools/forensics/` primitive emits the matched
record verbatim for exactly this reason, so no excerpt is ever hand-copied.

**Parallel subagents racing the ledger.** Seven of them calling
`tools/hooks.py post-probe` would write one `state.json` at once and spend a single
question's 25-probe budget in one round. So no `ctf-dfir-*` agent runs the hooks,
and none has an `Edit` tool.

**A missing parser read as an absent artifact.** These are opposite findings and
they look identical in a one-line report. Every primitive here degrades to
`parser_ok: false` with the install command, and `fkit.downgrade()` makes a
confirmation impossible when no parser ran — the forensics analogue of refusing to
confirm on a dead connection.

**An empty filter read as a closed class.** Three causes are indistinguishable from
outside: the ids are absent, the converter spells the field differently, or the log
does not cover the window. Each family's brief requires saying which one was ruled
out before reporting a family dead.

**Breadth reading as coverage.** Eight families reporting is not eight families
closed. A family that returned `not-measured` was never closed; one whose
`artifacts_that_fired` was empty was never pointed at. Say both plainly.

**The wrong-shaped answer.** This is the failure unique to the category: a correct
finding submitted in the wrong format is graded wrong and costs an attempt. Read
`skills/dfir-sherlock-triage/answer-discipline.md` **before the first answer**, not
after the first rejection — the timezone and precision rules there lose more
answers than the analysis does.

## The DFIR primitives each family reaches for

`python3 tools/forensics/selftest.py` proves these offline — 37 cases against real
fixture bytes, including the group whose only job is to show that a primitive which
ran no parser, or whose filter matched nothing, **cannot propose a confirmation**.

| Instead of | Run |
|---|---|
| reading a thousand-file bundle by eye | `artifact_inventory.py` — classifies every file and names ONE route, parsing nothing |
| `jq` over converted event records | `evtx_query.py` — filters, sorts explicitly, reports whether the input was chronological, and prints the matched record verbatim |
| four exports read side by side | `timeline_merge.py` — one UTC axis, every assumption stated with the rows it affected, unparsed rows counted not dropped, `--gap` for the hole |
| a regex over auth.log and a guess about wtmp | `linux_auth.py` — syslog plus binary utmp, stdlib only; refuses a timestamp answer from a log that carries no year, and ranks addresses by failures FOLLOWED by an acceptance |
| a `jq` one-liner over a CloudTrail tree | `cloudtrail_query.py` — walks the gzipped nested delivery, counts what it skipped, refuses to answer from a record carrying `errorCode`, and surfaces the assuming identity behind a role session |

## Roles

Every `ctf-dfir-*` agent is a `reader` and a `writer` in the `AGENTS.md` sense.
None is the machine that verifies. The agent proposes; `tools/hooks.py` and
`tools/decide.py` decide.

Related: [[web-parallel-sweep]] for the same method on a live web target,
[[parallel-layer-sweep]] for a white-box handout split into generic layers, and
[[ir-live-estate-triage]] when the estate is live and compromised rather than
handed over as a bundle.
