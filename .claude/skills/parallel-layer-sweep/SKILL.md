---
name: parallel-layer-sweep
description: >
  Close a layered white-box challenge in parallel instead of one layer at a
  time. Split the handout into independent mechanism layers with novel_plan,
  hand each layer plus its own falsifier to one ctf-layer-prober subagent, and
  merge the returned measurements through a validator that refuses any report
  claiming more than it measured. Use it on a multi-layer handout when no chain
  card is a strong match; not on a single-endpoint challenge.
tags: [process, method, subagents, fan-out, falsifier, white-box, ctf]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 2
  on_stuck: pivot
  stop_conditions:
    - "a layer report arrives whose evidence is not a verbatim response excerpt"
    - "two full sweeps produce no layer whose falsifier broke"
    - "a layer can only be measured by a write-shaped probe"
evidence_level: catalogue
---
# Parallel layer sweep — Process Skill

**Catalogue method.** No chain card proves it. What grounds it is a measured
retrospective from this repository: the `CSCV2026/diemthi` attempt closed
**eleven mechanism layers serially**, each by a cheap read-only measurement that
did not depend on any other layer's result. Eleven independent measurements run
one after another is the time sink; the challenge was lost on the clock, not on
the technique. Treat what follows as a procedure to run, not as experience of a
solve.

## When not to use it

- A chain card is a **strong** match (`status: candidate` from `chain_match.py`).
  Then run the card's own `first_confirming_probe` first — a sweep is slower than
  a known answer.
- The handout has one endpoint and one sink. There is nothing to fan out.
- The layer can only be measured by a write. A subagent must not write, and a
  shared instance is easy to break permanently.

## First probe

Do not send a request. Split the handout, and look at what has already been
closed:

```bash
python3 tools/subagent_fanout.py --brief <handout> \
        --challenge <name> --target <base-url>
```

That runs `tools/novel_plan.py` for you and emits one brief per layer, each
carrying its `first_probe`, its own `falsifier`, a five-probe ceiling, and —
this is the part that saves the most time — `already_measured_dead_elsewhere`,
drawn from every kill map in `knowledge/attempts/`.

The first probe is the answer to one question:

> **Which of these layers has this repository already measured dead, and which
> one has never been touched?**

A layer that a previous attempt closed is not worth a subagent. Read its
`measurement` and its `reopen_if`, and spend the budget elsewhere.

## The sweep

Launch one `ctf-layer-prober` per remaining layer, **in parallel**, each with
exactly one brief. Each prober reads the named files, runs at most five
read-only probes, and returns the contract JSON from
`python3 tools/subagent_fanout.py --contract`.

Then validate every report before believing any of it:

```bash
python3 tools/subagent_fanout.py --validate  report.json
python3 tools/subagent_fanout.py --merge     reports/*.json --challenge <name>
```

`--merge` prints the `hooks.py post-probe` commands for **you** to run. It does
not write `state.json`, and neither do the probers.

## The two failures this method has, and the guard for each

**A subagent summarising instead of quoting.** A sentence like "the template
evaluated arithmetic" is hypothesizer output; the evidence is the literal `49` in
the response. `--validate` refuses a report whose `evidence` is not a verbatim
substring of its own `response_excerpt`, so this fails loudly instead of
becoming a belief. Measured: eight adversarial reports, six refused with the
exact reason, two honest ones accepted — including a negative.

**Parallel probers racing the ledger.** If each prober called
`tools/hooks.py post-probe` itself, five of them would write one `state.json`
at once and spend the per-class probe budget in parallel — destroying the single
rule `tools/decide.py` exists to enforce. The probers therefore have no Write
tool and are told not to run `hooks.py` or `state.py` at all. You merge; they
measure.

## What to do with the result

- A layer whose **falsifier broke** is the next thing to work. Run its own probe
  yourself, through the hooks, and let `tools/decide.py` name the step after it.
- A layer whose **falsifier held** is a measurement worth keeping. Write it into
  `knowledge/attempts/<challenge>.json` with what was measured and the
  precondition that would reopen it, or the next attempt walks it again — which
  is the exact failure this skill exists to prevent.
- A layer reported `not-measured` was never closed. Say so; do not let a sweep's
  breadth read as coverage.

## Roles

A prober is a `reader` and a `writer` in the `AGENTS.md` sense. It never becomes
the machine that verifies. The agent proposes; `hooks.py` and `decide.py` decide.
