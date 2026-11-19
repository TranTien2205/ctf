# ROP basics — code reuse when NX is on — deep

Return-oriented programming: chain existing code fragments ending in 'ret' to do work without injecting code. pwn-code-reuse is the owning class; this file is the bridge.

## Mechanism internals

The chain is a layout, not a payload: each qword on the smashed stack is either a gadget address or a consumed argument, in order. The three invariants: (1) the offset to saved RIP is measured, not assumed — every build can shift it; (2) each gadget's consumed stack slots must be filled before the next address; (3) the chain ends only on an address that exists at runtime — PIE means base+offset.

## Boundary conditions

- The canary is the countermeasure: a leak or a write-around is required, else __stack_chk_fail.
- PIE + no leak means every address is unknown — a leak or a partial-overwrite trick is mandatory.
- Bad bytes in the read path (\x00 \x0a \x20 for most fgets/scanf) kill addresses containing them — pick different gadgets.
- movaps alignment inside libc faults on a misaligned stack — an extra ret gadget fixes parity.
- One-shot services can't re-trigger — the leak and the smash compose in one input, or the chain must be leak-free.

## Falsifier

Falsifier — the gadgets needed don't exist in the binary (or a needed constant can't be loaded): ROP fails; need a leak or a different primitive.

## Highest-cost traps

- Small static binaries have few gadgets — check if __libc_csu_init exists for the universal gadgets.
- A missing 'pop rdx' gadget is the usual hole — find it via the mov rdx gadgets or a different call.
- Every gadget in the chain must be reachable at runtime (PIE → need base leak).

## Commands

```bash
python3 tools/pwn_triage.py ./chal --gadgets
r2 -A ./chal && /R pop rdi
```

## Cross-references

`../pwn-code-reuse/` · `ret2libc.md`
