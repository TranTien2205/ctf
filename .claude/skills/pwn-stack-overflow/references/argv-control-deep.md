# Input via argv — when the read is the command line — deep

Some binaries take input as argv[1] instead of stdin: the overflow is in an argument. The payload goes in the argument position.

## Mechanism internals

The chain is a layout, not a payload: each qword on the smashed stack is either a gadget address or a consumed argument, in order. The three invariants: (1) the offset to saved RIP is measured, not assumed — every build can shift it; (2) each gadget's consumed stack slots must be filled before the next address; (3) the chain ends only on an address that exists at runtime — PIE means base+offset.

## Boundary conditions

- The canary is the countermeasure: a leak or a write-around is required, else __stack_chk_fail.
- PIE + no leak means every address is unknown — a leak or a partial-overwrite trick is mandatory.
- Bad bytes in the read path (\x00 \x0a \x20 for most fgets/scanf) kill addresses containing them — pick different gadgets.
- movaps alignment inside libc faults on a misaligned stack — an extra ret gadget fixes parity.
- One-shot services can't re-trigger — the leak and the smash compose in one input, or the chain must be leak-free.

## Falsifier

Falsifier — the input isn't argv — check stdin/protocol paths.

## Highest-cost traps

- \x00 can't appear in argv — no null bytes in the payload.
- The shell interprets the arg — quote it or pass raw bytes via subprocess.

## Commands

```bash
./chal $(python3 -c 'print("A"*100)')
```

## Cross-references

`read-family.md`
