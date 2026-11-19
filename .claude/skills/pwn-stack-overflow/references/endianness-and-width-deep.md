# Endianness and register width — x86 vs x64 — deep

x86 (32-bit) args go on the stack; x64 args go in rdi/rsi/rdx. Pattern chunks and addresses are 4 vs 8 bytes. Get the width right or the chain is garbage.

## Mechanism internals

The chain is a layout, not a payload: each qword on the smashed stack is either a gadget address or a consumed argument, in order. The three invariants: (1) the offset to saved RIP is measured, not assumed — every build can shift it; (2) each gadget's consumed stack slots must be filled before the next address; (3) the chain ends only on an address that exists at runtime — PIE means base+offset.

## Boundary conditions

- The canary is the countermeasure: a leak or a write-around is required, else __stack_chk_fail.
- PIE + no leak means every address is unknown — a leak or a partial-overwrite trick is mandatory.
- Bad bytes in the read path (\x00 \x0a \x20 for most fgets/scanf) kill addresses containing them — pick different gadgets.
- movaps alignment inside libc faults on a misaligned stack — an extra ret gadget fixes parity.
- One-shot services can't re-trigger — the leak and the smash compose in one input, or the chain must be leak-free.

## Falsifier

Falsifier — you built an x64-style chain on a 32-bit binary (or vice versa): the arg placement is wrong; rebuild.

## Highest-cost traps

- On x86, 'pop rdi' doesn't exist — args literally go on the stack.
- Return address is 4 bytes on x86, 8 on x64 — the padding differs.

## Commands

```bash
readelf -h ./chal | grep Class
```

## Cross-references

`boundary-cases.md` · `rop-basics.md`
