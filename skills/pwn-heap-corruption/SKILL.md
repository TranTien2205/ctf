---
name: pwn-heap-corruption
description: >
  Action-oriented depth skill for Heap allocator corruption. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: pwn-stack-overflow.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [pwn, pwn-heap-corruption, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# Heap allocator corruption

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

answer the glibc version question first, because tcache behaviour, double-free detection and fd mangling differ sharply across versions, then map the allocation lifecycle and name the primitive the bug gives before choosing any technique

**Falsifier** — the observation that closes this class: the pointer is cleared on free and every index is bounds-checked, so no freed object is reachable; gdb is absent here, so runtime confirmation is radare2 in debug mode or observable program behaviour
## Recognise

The bug lives between allocated objects: use-after-free, double-free, an
overflow that reaches chunk metadata, or an index that reads/writes past an
allocation. The first question is never the bug — it is the allocator version.

## Confirm

Answer the glibc version first (`libc.so.6` shipped, `strings` version line, or
the challenge's stated base image): tcache behaviour, double-free detection and
fd mangling differ sharply across versions, and a technique written for 2.27
dies silently on 2.36.

| Version feature | Consequence |
|---|---|
| tcache bins (2.26+) | freed chunks go to per-thread bins first |
| tcache count check (2.29+) | naive double-free is detected |
| safe-linking (2.32+) | fd pointers are mangled — a leak is required to aim them |
| unsorted-bin leak | first free of a larger chunk leaks libc pointers |

Then map the allocation layout — which chunks you allocate, free, and in what
order — and drive the corruption to overlapping chunks or a poisoned `fd`.

## Traps

- A pointer cleared on free and bounds-checked indexes close the class — no
  freed object is reachable.
- `gdb` is absent here: `r2 -d ./chal` with `dmh` commands is the runtime heap
  view.
- Heap feng shui is order-sensitive; script the alloc/free sequence rather than
  clicking through it interactively.

## Operational probe

```bash
python3 tools/pwn_triage.py ./chal
r2 -d ./chal          # dmh, dmhf for the heap walk
```

## Routing

Shares signals with: `../pwn-stack-overflow/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/ctf-pwn/heap-techniques.md`
- `skills/ctf-pwn/heap-fsop.md`

| Any heap-corruption question | `references/chunk-abuse.md` |

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
