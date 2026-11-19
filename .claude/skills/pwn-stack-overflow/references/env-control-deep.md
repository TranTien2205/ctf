# Input via environment — env-var buffers — deep

Environment variables land on the stack too: getenv() + strcpy into a buffer is a stack overflow via an env var.

## Mechanism internals

The chain is a layout, not a payload: each qword on the smashed stack is either a gadget address or a consumed argument, in order. The three invariants: (1) the offset to saved RIP is measured, not assumed — every build can shift it; (2) each gadget's consumed stack slots must be filled before the next address; (3) the chain ends only on an address that exists at runtime — PIE means base+offset.

## Boundary conditions

- The canary is the countermeasure: a leak or a write-around is required, else __stack_chk_fail.
- PIE + no leak means every address is unknown — a leak or a partial-overwrite trick is mandatory.
- Bad bytes in the read path (\x00 \x0a \x20 for most fgets/scanf) kill addresses containing them — pick different gadgets.
- movaps alignment inside libc faults on a misaligned stack — an extra ret gadget fixes parity.
- One-shot services can't re-trigger — the leak and the smash compose in one input, or the chain must be leak-free.

## Falsifier

Falsifier — the env var isn't copied to a stack buffer or is validated first: not this route.

## Highest-cost traps

- env vars can't contain \x00 — same restriction as argv.
- env placement shifts stack addresses — a stack-target exploit needs the env accounted for.

## Commands

```bash
X=$(python3 -c 'print("A"*200)') ./chal
```

## Cross-references

`read-family.md`
