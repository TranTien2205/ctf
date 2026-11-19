# Detecting the buffer — finding the sink — deep

White-box: grep for the read functions and array bounds. Black-box: send patterns and watch for crashes at growing lengths.

## Mechanism internals

The chain is a layout, not a payload: each qword on the smashed stack is either a gadget address or a consumed argument, in order. The three invariants: (1) the offset to saved RIP is measured, not assumed — every build can shift it; (2) each gadget's consumed stack slots must be filled before the next address; (3) the chain ends only on an address that exists at runtime — PIE means base+offset.

## Boundary conditions

- The canary is the countermeasure: a leak or a write-around is required, else __stack_chk_fail.
- PIE + no leak means every address is unknown — a leak or a partial-overwrite trick is mandatory.
- Bad bytes in the read path (\x00 \x0a \x20 for most fgets/scanf) kill addresses containing them — pick different gadgets.
- movaps alignment inside libc faults on a misaligned stack — an extra ret gadget fixes parity.
- One-shot services can't re-trigger — the leak and the smash compose in one input, or the chain must be leak-free.

## Falsifier

Falsifier — every read is properly bounded: no stack-corruption exists; other classes own it.

## Highest-cost traps

- sprintf/vsprintf into a stack buffer with user input is a hidden format-string too.
- memcpy of a computed length can be influenced via the computed n.
- strcpy of an env/argv value is the same class via a different transport.

## Commands

```bash
grep -nE 'gets|strcpy|strcat|scanf|read|memcpy|sprintf' source.c
```

## Cross-references

`detect-buffer.md` → `read-family.md`
