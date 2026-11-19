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

Shares signals with: `../pwn-stack-overflow/` and `../pwn-format-string/`.
Check those before committing to this one.

Depth, one named file at a time:

- `skills/ctf-pwn/heap-techniques.md`
- `skills/ctf-pwn/heap-fsop.md`

The `references/` corpus (one file per question, `*-deep` / `*-checklist` /
`-map` companions for most):

| Question | File |
|---|---|
| Any heap-corruption question | `references/chunk-abuse.md` |
| The runbook start to finish | `references/workflow.md` |
| Foundations | `references/glibc-version-first.md`, `references/chunk-anatomy.md`, `references/the-bins.md`, `references/first-fit.md`, `references/bin-map.md` |
| Bugs to primitives | `references/the-bug-shapes.md`, `references/primitive-matrix.md`, `references/uaf-primitive.md`, `references/double-free.md`, `references/off-by-one.md`, `references/index-array-bug.md` |
| Techniques | `references/tcache-poisoning.md`, `references/fastbin-dup.md`, `references/the-unsorted-write.md`, `references/house-of-force.md`, `references/house-of-spirit.md`, `references/large-bin-attack.md`, `references/overlapping-chunks.md`, `references/fake-chunk.md` |
| Version gates | `references/version-feature-map.md`, `references/safe-linking.md`, `references/tcache-key.md`, `references/the-consistency-checks.md`, `references/free-hook.md`, `references/vtable-check.md` |
| Leaks | `references/unsorted-bin-leak.md`, `references/heap-leak.md`, `references/environ-leak.md`, `references/libc-version-offsets.md` |
| Grooming | `references/heap-feng-shui.md`, `references/guard-chunks.md`, `references/the-free-order.md`, `references/coalesce-order.md` |
| Endings | `references/write-targets-heap.md`, `references/fsop-basics.md`, `references/system-binsh.md`, `references/one-gadget.md`, `references/the-endgame-table.md` |
| Diagnosis | `references/heap-crash-map.md`, `references/r2-heap-view.md`, `references/troubleshoot.md`, `references/anti-patterns.md` |
| Discipline | `references/evidence.md`, `references/falsifiers.md`, `references/the-checklist.md`, `references/the-glossary.md`, `references/the-map-index.md`, `references/heap-negative-results.md`, `references/heap-boundary.md` |

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
