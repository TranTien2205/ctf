# Protections — canary, PIE, NX, RELRO, ASLR — deep

tools/pwn_triage.py reports each protection WITH the evidence that decided it. The sheet determines the whole chain — read it before touching a payload.

## Mechanism internals

The chain is a layout, not a payload: each qword on the smashed stack is either a gadget address or a consumed argument, in order. The three invariants: (1) the offset to saved RIP is measured, not assumed — every build can shift it; (2) each gadget's consumed stack slots must be filled before the next address; (3) the chain ends only on an address that exists at runtime — PIE means base+offset.

## Boundary conditions

- The canary is the countermeasure: a leak or a write-around is required, else __stack_chk_fail.
- PIE + no leak means every address is unknown — a leak or a partial-overwrite trick is mandatory.
- Bad bytes in the read path (\x00 \x0a \x20 for most fgets/scanf) kill addresses containing them — pick different gadgets.
- movaps alignment inside libc faults on a misaligned stack — an extra ret gadget fixes parity.
- One-shot services can't re-trigger — the leak and the smash compose in one input, or the chain must be leak-free.

## Falsifier

Falsifier — the protections report contradicts your read of the binary: the report carries the evidence; trust the evidence, not the label.

## Highest-cost traps

- A STATIC binary carries __stack_chk_fail even when built -fno-stack-protector — confirm the canary from the %fs:0x28 load, not the import.
- PIE + no leak = you need a partial-address write or an info-leak primitive first.
- 'NX' on Linux stack-NX; data/bss writable but not executable regardless.

## Commands

```bash
python3 tools/pwn_triage.py ./chal
python3 tools/pwn_triage.py ./chal --gadgets
readelf -h ./chal | grep Type
```

## Cross-references

`tools-pwn-triage.md` · `canary-bypass.md` · `pie-leak.md`
