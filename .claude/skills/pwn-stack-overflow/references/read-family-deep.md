# The read-family matrix — which input function and what it allows — deep

Different input functions allow different byte filters and bounds — the read function decides which shellcode/chain bytes survive.

## Mechanism internals

The chain is a layout, not a payload: each qword on the smashed stack is either a gadget address or a consumed argument, in order. The three invariants: (1) the offset to saved RIP is measured, not assumed — every build can shift it; (2) each gadget's consumed stack slots must be filled before the next address; (3) the chain ends only on an address that exists at runtime — PIE means base+offset.

## Boundary conditions

- The canary is the countermeasure: a leak or a write-around is required, else __stack_chk_fail.
- PIE + no leak means every address is unknown — a leak or a partial-overwrite trick is mandatory.
- Bad bytes in the read path (\x00 \x0a \x20 for most fgets/scanf) kill addresses containing them — pick different gadgets.
- movaps alignment inside libc faults on a misaligned stack — an extra ret gadget fixes parity.
- One-shot services can't re-trigger — the leak and the smash compose in one input, or the chain must be leak-free.

## Falsifier

Falsifier — the read is bounded to less than the saved-state distance: no write reaches the return address; not this class.

## Highest-cost traps

- scanf %s stops at whitespace — \x20\x09\x0a are banned bytes.
- read(n) where n is a signed int and checked 'n <= sizeof(buf)' without 'n > 0' — negative n passes.
- fgets is safe BY DESIGN unless the size arg is wrong — check the arg.

## Commands

```bash
r2 -A ./chal && pdf @ <vuln>
```

## Cross-references

`bad-chars.md` · `boundary-cases.md`
