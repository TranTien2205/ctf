# Stack alignment — the movaps crash — deep

x64 libc functions (especially system, printf) use movaps on the stack, which faults on misaligned RSP. A chain that crashes on the call site needs an extra 'ret' gadget for alignment.

## Mechanism internals

The chain is a layout, not a payload: each qword on the smashed stack is either a gadget address or a consumed argument, in order. The three invariants: (1) the offset to saved RIP is measured, not assumed — every build can shift it; (2) each gadget's consumed stack slots must be filled before the next address; (3) the chain ends only on an address that exists at runtime — PIE means base+offset.

## Boundary conditions

- The canary is the countermeasure: a leak or a write-around is required, else __stack_chk_fail.
- PIE + no leak means every address is unknown — a leak or a partial-overwrite trick is mandatory.
- Bad bytes in the read path (\x00 \x0a \x20 for most fgets/scanf) kill addresses containing them — pick different gadgets.
- movaps alignment inside libc faults on a misaligned stack — an extra ret gadget fixes parity.
- One-shot services can't re-trigger — the leak and the smash compose in one input, or the chain must be leak-free.

## Falsifier

Falsifier — the crash isn't alignment (it's a real arg/register problem): the ret-pad doesn't fix it; re-debug the chain.

## Highest-cost traps

- The classic symptom: 'works locally, crashes remotely' — a 16-byte alignment shift.
- An even vs odd number of returns before the call is what matters.

## Commands

```bash
r2 -A ./chal && /R ret
```

## Cross-references

`ret2libc.md` · `troubleshoot.md`
