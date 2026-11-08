---
name: pwn-code-reuse
description: >
  Action-oriented depth skill for ROP and code reuse. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: pwn-stack-overflow, pwn-format-string.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [pwn, pwn-code-reuse, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# ROP and code reuse

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

this class presupposes control of the instruction pointer, so confirm that first; then read the protections to decide whether a leak is needed at all, and build the leak chain and verify the leaked value looks like a libc address before chaining further

**Falsifier** — the observation that closes this class: the gadgets present cannot express the call -- no controllable argument register, or no writable page to pivot into -- which tools/pwn_triage.py reports from the executable segments it actually scanned, since ROPgadget and ropper are absent here
## Recognise

This class presupposes control of the instruction pointer — a confirmed stack
or format-string overwrite — with NX on, so the payload is borrowed code, not
injected code.

## Confirm

Read the protection sheet `tools/pwn_triage.py` already produced: PIE or ASLR
decides whether a leak is needed at all, RELRO decides whether GOT is a
reachable write, and its gadget report names what the binary can express.

| Shape | Route |
|---|---|
| dynamic binary, libc supplied or leakable | ret2libc — `system`, `execve` gadgets |
| static binary | syscall gadgets or `int 0x80` |
| no `pop rdi` but `__libc_csu_init` present | ret2csu — the universal call primitive |
| write what/where needed | GOT entry, `.data`, or a `read` into a writable page |

Confirmation is the target action observed — a shell prompt, a read of the flag
path — never a clean exit after the chain.

## Traps

- On x86-64 a `ret` gadget before the final call fixes stack alignment; a chain
  that crashes inside `system` on `movaps` is an alignment bug, not a bad chain.
- The remote libc must match — leak a resolved symbol and identify the version
  (`tools/gadget_lookup.py`, libc database) before hard-coding offsets.
- `ROPgadget`/`ropper` are absent here; `r2 /R` and the `pwn_triage.py` gadget
  report are the local answer.

## Operational probe

```bash
python3 tools/pwn_triage.py ./chal      # protections + gadgets in one report
r2 -c "/R pop rdi" ./chal
```

## Routing

Shares signals with: `../pwn-stack-overflow/`, `../pwn-format-string/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/pwn-rop/references/rop-chains.md`
- `skills/pwn-rop/references/ret2libc.md`
- `skills/ctf-pwn/rop-and-shellcode.md`

| Any ROP/code-reuse question | `references/gadget-selection.md` |

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
