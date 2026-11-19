# tools/pwn_triage.py — the protection report — deep

First contact: protections with the evidence for each, dangerous imports annotated, essential gadgets, and the routes each protection leaves open.

## Mechanism internals

The chain is a layout, not a payload: each qword on the smashed stack is either a gadget address or a consumed argument, in order. The three invariants: (1) the offset to saved RIP is measured, not assumed — every build can shift it; (2) each gadget's consumed stack slots must be filled before the next address; (3) the chain ends only on an address that exists at runtime — PIE means base+offset.

## Boundary conditions

- The canary is the countermeasure: a leak or a write-around is required, else __stack_chk_fail.
- PIE + no leak means every address is unknown — a leak or a partial-overwrite trick is mandatory.
- Bad bytes in the read path (\x00 \x0a \x20 for most fgets/scanf) kill addresses containing them — pick different gadgets.
- movaps alignment inside libc faults on a misaligned stack — an extra ret gadget fixes parity.
- One-shot services can't re-trigger — the leak and the smash compose in one input, or the chain must be leak-free.

## Falsifier

Falsifier — the report and the binary disagree: the report's evidence is authoritative; re-read it.

## Highest-cost traps

- Absent-tool story: no pwntools/gdb/ROPgadget — this is the stdlib-only triage.
- A STATIC binary's __stack_chk_fail import doesn't mean the canary is enabled — read the evidence.
- python3 tools/pwnstatic/selftest.py proves the triage against readelf offline.

## Commands

```bash
python3 tools/pwn_triage.py ./chal
python3 tools/pwn_triage.py ./chal --gadgets
python3 tools/pwnstatic/selftest.py
```

## Cross-references

`protection-modes.md`
