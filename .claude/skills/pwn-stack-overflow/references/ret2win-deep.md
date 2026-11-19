# ret2win / ret2func — jump to a function in the binary — deep

The simplest chain: a function in the binary does what you want (calls system, prints the flag). Overwrite the return address with its address — no libc needed.

## Mechanism internals

The chain is a layout, not a payload: each qword on the smashed stack is either a gadget address or a consumed argument, in order. The three invariants: (1) the offset to saved RIP is measured, not assumed — every build can shift it; (2) each gadget's consumed stack slots must be filled before the next address; (3) the chain ends only on an address that exists at runtime — PIE means base+offset.

## Boundary conditions

- The canary is the countermeasure: a leak or a write-around is required, else __stack_chk_fail.
- PIE + no leak means every address is unknown — a leak or a partial-overwrite trick is mandatory.
- Bad bytes in the read path (\x00 \x0a \x20 for most fgets/scanf) kill addresses containing them — pick different gadgets.
- movaps alignment inside libc faults on a misaligned stack — an extra ret gadget fixes parity.
- One-shot services can't re-trigger — the leak and the smash compose in one input, or the chain must be leak-free.

## Falsifier

Falsifier — no function does what you need and the binary exposes no system-like call site: ret2win is out; go to ret2plt/ret2libc.

## Highest-cost traps

- PIE: the function's address is base+offset — need a leak of the base first.
- Call targets need the right args on the stack — ret2win with no args is the easy case.
- Stack alignment (movaps): some functions crash on misaligned RSP — pad with a ret gadget first.

## Commands

```bash
r2 -A ./chal && afl
r2 -A ./chal && pdf @ win
```

## Cross-references

`offset-measurement.md` · `ret2plt.md` · `rop-basics.md`
