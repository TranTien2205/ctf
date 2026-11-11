---
name: pwn-stack-overflow
description: >
  Action-oriented depth skill for Stack memory corruption. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: pwn-format-string, pwn-code-reuse.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [pwn, pwn-stack-overflow, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# Stack memory corruption

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

run python3 tools/pwn_triage.py on the binary FIRST for the protections with the evidence that decided each, then measure the exact offset to the saved return address empirically with a cyclic pattern -- pwntools is absent here, so `python3 tools/pwn_cyclic.py <len>` generates the De Bruijn pattern and `python3 tools/pwn_cyclic.py --find <faulting-register>` reads the offset back

**Falsifier** — the observation that closes this class: the read is bounded by a length the input cannot influence, so no write reaches saved state; note that a STATIC binary carries __stack_chk_fail even when built -fno-stack-protector, so confirm a canary from the %fs:0x28 load in the disassembly rather than from the import
## Recognise

A native binary takes input and something reads past the buffer: `gets`, an
unbounded `scanf %s`, `strcpy`, a `read` with a length the caller trusts. The
prize is the saved return address; the first deliverable is the exact offset to
it.

## Confirm

`tools/pwn_triage.py` **first** — it reports every protection with the evidence
that decided it, and the protection sheet decides the whole chain. Then measure
the offset with a cyclic/de Bruijn pattern and prove control: the saved return
address holds your four marker bytes.

| Protection | What it changes |
|---|---|
| canary | a smashing write trips `__stack_chk_fail` before the return |
| PIE | no absolute gadget or data address until a leak lands |
| NX | the payload is code reuse — `../pwn-code-reuse/` — not shellcode |
| NX off | `python3 tools/sc_gen.py execve64|execve86|cat64|rev64` emits tested shellcode stubs (`--raw` for hex only; output reports any `\x00\x0a\x0d\x20` bytes present) |
| full RELRO | closes GOT as a write target |

## Traps

- A **static** binary can carry the `__stack_chk_fail` symbol without the check
  being enabled — read the protections report, not the string table.
- The length field may be attacker-influenced but bounded elsewhere; a read
  capped below the saved-state distance is not this class.
- Send the cyclic pattern once and record the fault address; guessing offsets
  burns the probe budget.

## Operational probe

```bash
python3 tools/pwn_triage.py ./chal
r2 -A ./chal && afl
# cyclic(offset-pattern) -> crash -> read faulted RIP, recover exact offset
```

## Routing

Shares signals with: `../pwn-format-string/`, `../pwn-code-reuse/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/ctf-pwn/overflow-basics.md`
- `skills/pwn-binary-triage/SKILL.md`

| Any stack-corruption question | `references/control-flow.md` |

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
