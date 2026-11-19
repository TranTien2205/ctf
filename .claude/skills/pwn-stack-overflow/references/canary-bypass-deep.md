# Stack canary — leak it or write around it — deep

A stack canary is a random word placed before the saved frame; smashing past it trips __stack_chk_fail. The bypass is always the same shape: get the canary's value, keep it intact in your payload.

## Mechanism internals

The chain is a layout, not a payload: each qword on the smashed stack is either a gadget address or a consumed argument, in order. The three invariants: (1) the offset to saved RIP is measured, not assumed — every build can shift it; (2) each gadget's consumed stack slots must be filled before the next address; (3) the chain ends only on an address that exists at runtime — PIE means base+offset.

## Boundary conditions

- The canary is the countermeasure: a leak or a write-around is required, else __stack_chk_fail.
- PIE + no leak means every address is unknown — a leak or a partial-overwrite trick is mandatory.
- Bad bytes in the read path (\x00 \x0a \x20 for most fgets/scanf) kill addresses containing them — pick different gadgets.
- movaps alignment inside libc faults on a misaligned stack — an extra ret gadget fixes parity.
- One-shot services can't re-trigger — the leak and the smash compose in one input, or the chain must be leak-free.

## Falsifier

Falsifier — no leak primitive exists and the canary blocks every write path: the class's stack route is closed; other classes (format-string, heap) may remain.

## Highest-cost traps

- A forking server (per-connection fork) reuses ONE canary — byte-at-a-time brute is feasible (~256 × 8 checks).
- The canary sits between locals and saved regs — your write must land past it intact.
- A leaked canary is valid only for that process/fork — re-leak per connection if the server doesn't fork.

## Commands

```bash
r2 -A ./chal && pdf @ main | grep fs:0x28
```

## Cross-references

`protection-modes.md` · `format-string-leak.md` · `pie-leak.md`
