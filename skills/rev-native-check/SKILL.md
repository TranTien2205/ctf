---
name: rev-native-check
description: >
  Action-oriented depth skill for Native deciding check. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: rev-bytecode-vm, pwn-stack-overflow.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [rev, rev-native-check, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# Native deciding check

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

locate the input read, follow the value to the comparison, and quote the disassembly that carries it: a described check is not a measured one. r2 -A then afl then pdf @ main; gdb is absent, so r2 -d is the debugger

**Falsifier** — the observation that closes this class: the comparison is against a value computed at run time from something you cannot observe or supply, so replicating the check in python cannot produce the input
## Recognise

A native binary reads input and prints a verdict. The work is locating **the
deciding check** — the one comparison the flag actually passes through — and
replicating it, not describing the whole binary.

## Confirm

Locate the input read, follow the value to the comparison, and quote the
disassembly that carries it. Then replicate the check in Python and verify: a
replicated check that produces the accepted input is the solve; a described
check is not a measured one.

| Pattern | Where it usually sits |
|---|---|
| literal `strcmp`/`memcmp` | the answer is one `strings` away or one xref from the read |
| per-character transform then compare | replicate the transform in Python |
| table-driven check | dump the table, invert the mapping |
| anti-debug or packer wrapper | `../rev-triage/references/packer-analysis.md` first — the check is underneath |

## Traps

- A comparison against a value computed at run time from something you cannot
  supply means replication cannot produce the input — that is the class
  falsifier, not a harder instance.
- `radare2` is the dynamic story here: `r2 -d` debugs, `r2 -A` analyses, `pdf @
  main` disassembles. There is no `gdb`.
- Read the xrefs **to** the success/failure strings — they walk you backwards
  to the check faster than `afl` walks you forwards.

## Operational probe

```bash
r2 -A ./chal
r2 -c "afl; iz" ./chal          # functions, then strings — find the verdict text
```

## Routing

Shares signals with: `../rev-bytecode-vm/`, `../pwn-stack-overflow/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/ctf-reverse/patterns-ctf.md`
- `skills/ctf-reverse/tools.md`
- `skills/rev-triage/references/packer-analysis.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
