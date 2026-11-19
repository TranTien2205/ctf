# GOT overwrite — partial RELRO — deep

Under partial RELRO, the GOT stays writable: overwrite an imported function's GOT slot to point at system/another function — the next call to it goes to your target.

## Mechanism internals

The chain is a layout, not a payload: each qword on the smashed stack is either a gadget address or a consumed argument, in order. The three invariants: (1) the offset to saved RIP is measured, not assumed — every build can shift it; (2) each gadget's consumed stack slots must be filled before the next address; (3) the chain ends only on an address that exists at runtime — PIE means base+offset.

## Boundary conditions

- The canary is the countermeasure: a leak or a write-around is required, else __stack_chk_fail.
- PIE + no leak means every address is unknown — a leak or a partial-overwrite trick is mandatory.
- Bad bytes in the read path (\x00 \x0a \x20 for most fgets/scanf) kill addresses containing them — pick different gadgets.
- movaps alignment inside libc faults on a misaligned stack — an extra ret gadget fixes parity.
- One-shot services can't re-trigger — the leak and the smash compose in one input, or the chain must be leak-free.

## Falsifier

Falsifier — full RELRO: the GOT is read-only; no GOT write applies.

## Highest-cost traps

- The write must reach the GOT — stack smashes reach stack only; need arb-write or a far-enough smash.
- Partial RELRO leaves GOT writable; full RELRO binds it readonly at startup.
- A GOT overwrite needs the target's real address — a leak if ASLR.

## Commands

```bash
readelf -d ./chal | grep -i relro
readelf -r ./chal
```

## Cross-references

`ret2libc.md` · `write-where.md`
