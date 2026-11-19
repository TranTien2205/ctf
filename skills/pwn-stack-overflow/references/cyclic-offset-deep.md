# Offset measurement — the cyclic pattern — deep

The first deliverable of every stack challenge: the exact byte offset from your input's start to the saved return address. tools/pwn_cyclic.py makes the De Bruijn pattern; a faulting register reads the offset back.

## Mechanism internals

The chain is a layout, not a payload: each qword on the smashed stack is either a gadget address or a consumed argument, in order. The three invariants: (1) the offset to saved RIP is measured, not assumed — every build can shift it; (2) each gadget's consumed stack slots must be filled before the next address; (3) the chain ends only on an address that exists at runtime — PIE means base+offset.

## Boundary conditions

- The canary is the countermeasure: a leak or a write-around is required, else __stack_chk_fail.
- PIE + no leak means every address is unknown — a leak or a partial-overwrite trick is mandatory.
- Bad bytes in the read path (\x00 \x0a \x20 for most fgets/scanf) kill addresses containing them — pick different gadgets.
- movaps alignment inside libc faults on a misaligned stack — an extra ret gadget fixes parity.
- One-shot services can't re-trigger — the leak and the smash compose in one input, or the chain must be leak-free.

## Falsifier

Falsifier — the faulting register never holds pattern bytes at any length: no write reaches the saved return address. Re-check the read bound; it is probably capped below the saved-state distance.

## Highest-cost traps

- A crash inside the copy (segfault writing the input) is not control — you need the fault at function-return time.
- 32-bit vs 64-bit pattern: --find takes 4 bytes regardless; check the register width.
- The fault address in the log may be the pattern chunk itself, not RIP — read the right register.

## Commands

```bash
python3 tools/pwn_cyclic.py 200
python3 tools/pwn_cyclic.py --find 0x6161616c
```

## Cross-references

`control-flow.md` · `offset-measurement.md`
