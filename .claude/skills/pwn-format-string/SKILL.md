---
name: pwn-format-string
description: >
  Action-oriented depth skill for Format-string read or write. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: pwn-stack-overflow.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [pwn, pwn-format-string, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# Format-string read or write

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

send a handful of %p in one request and read the leaked words back, which is the cheapest confirmation in pwn, then locate your own buffer with %N$p before deciding read against write

**Falsifier** — the observation that closes this class: the format argument is a literal and the user value is an argument to it, so nothing is interpreted; and full RELRO reported by tools/pwn_triage.py closes the GOT-overwrite route whatever the leak is worth
## Recognise

User input lands where a format string belongs: `printf(buf)`, `fprintf(f, buf)`,
`snprintf(dst, n, buf)` with no format argument of its own. The cheapest
confirmation in pwn lives here.

## Confirm

Send a short run of `%p` and read the leaked words back — a `%p` that returns a
stack pointer confirms the primitive in one probe. Then locate your own buffer:
`AAAA.%N$p` scanning `N` until `0x41414141` returns, which fixes the argument
offset every `%n` write depends on.

| Primitive | What it buys |
|---|---|
| `%p` / `%x` reads | stack, libc and binary addresses — the leak |
| `%s` at a planted pointer | arbitrary read |
| `%n` / `%hn` / `%hhn` | arbitrary write — GOT entry, return address, `__malloc_hook` on old glibc |

## Traps

- The format argument being a **literal** closes the class — `printf("%s", buf)`
  interprets nothing.
- Full RELRO closes the GOT route; the remaining targets are the saved return
  and allocator hooks.
- On x86-64 the first several variadic arguments live in registers — the stack
  offset you measured for `%p` is not argument index zero.
- A blind format string returns no output; it needs a crash oracle and is a
  different budget, not a harder version of this class.

## Operational probe

```text
%p.%p.%p.%p            # leaked words?
AAAA.%N$p              # N where 0x41414141 returns = buffer offset
```

## Routing

Shares signals with: `../pwn-stack-overflow/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/ctf-pwn/format-string.md`
- `skills/pwn-binary-triage/SKILL.md`

| Any format-string question | `references/read-and-write.md` |

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
