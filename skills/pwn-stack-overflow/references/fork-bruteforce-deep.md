# Fork-server canary brute-force — deep

A forking service (per-connection fork) reuses ONE canary across connections — brute it byte-by-byte through the crash-or-not signal.

## Mechanism internals

The chain is a layout, not a payload: each qword on the smashed stack is either a gadget address or a consumed argument, in order. The three invariants: (1) the offset to saved RIP is measured, not assumed — every build can shift it; (2) each gadget's consumed stack slots must be filled before the next address; (3) the chain ends only on an address that exists at runtime — PIE means base+offset.

## Boundary conditions

- The canary is the countermeasure: a leak or a write-around is required, else __stack_chk_fail.
- PIE + no leak means every address is unknown — a leak or a partial-overwrite trick is mandatory.
- Bad bytes in the read path (\x00 \x0a \x20 for most fgets/scanf) kill addresses containing them — pick different gadgets.
- movaps alignment inside libc faults on a misaligned stack — an extra ret gadget fixes parity.
- One-shot services can't re-trigger — the leak and the smash compose in one input, or the chain must be leak-free.

## Falsifier

Falsifier — the server execs per connection (new canary each time) or doesn't fork: each connection has a different canary; no stable oracle.

## Highest-cost traps

- Worst case 8 × 256 = 2048 connections — feasible.
- Correct byte keeps the process alive; wrong byte trips __stack_chk_fail.
- The oracle is 'did it crash', a clean binary answer.

## Cross-references

`canary-bypass.md` · `remote-vs-local.md`
