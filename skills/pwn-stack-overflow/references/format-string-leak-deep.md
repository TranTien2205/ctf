# Format string as a leak primitive — deep

A format-string read (%p, %s, %x) dumps stack/registers — the leak primitive that feeds canary and PLE leaks. Ownership is pwn-format-string's class; this file is the bridge.

## Mechanism internals

The chain is a layout, not a payload: each qword on the smashed stack is either a gadget address or a consumed argument, in order. The three invariants: (1) the offset to saved RIP is measured, not assumed — every build can shift it; (2) each gadget's consumed stack slots must be filled before the next address; (3) the chain ends only on an address that exists at runtime — PIE means base+offset.

## Boundary conditions

- The canary is the countermeasure: a leak or a write-around is required, else __stack_chk_fail.
- PIE + no leak means every address is unknown — a leak or a partial-overwrite trick is mandatory.
- Bad bytes in the read path (\x00 \x0a \x20 for most fgets/scanf) kill addresses containing them — pick different gadgets.
- movaps alignment inside libc faults on a misaligned stack — an extra ret gadget fixes parity.
- One-shot services can't re-trigger — the leak and the smash compose in one input, or the chain must be leak-free.

## Falsifier

Falsifier — the format-string isn't controllable to the needed depth, or the target value isn't on the stack: no leak via this path.

## Highest-cost traps

- The leak is pwn-format-string's mechanism — this file only explains the chain.
- Different stack depths each call — the offset to the canary varies; measure once, use it.

## Commands

```bash
r2 -A ./chal && pdf @ <func_with_printf>
```

## Cross-references

`../pwn-format-string/` · `canary-bypass.md` · `pie-leak.md`
