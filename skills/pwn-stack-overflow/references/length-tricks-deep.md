# Length field tricks — when the input length is the bug — deep

The read's n is attacker-influenced or miscomputed: signed-n checks, integer wrap, off-by-one — the length IS the vulnerability.

## Mechanism internals

The chain is a layout, not a payload: each qword on the smashed stack is either a gadget address or a consumed argument, in order. The three invariants: (1) the offset to saved RIP is measured, not assumed — every build can shift it; (2) each gadget's consumed stack slots must be filled before the next address; (3) the chain ends only on an address that exists at runtime — PIE means base+offset.

## Boundary conditions

- The canary is the countermeasure: a leak or a write-around is required, else __stack_chk_fail.
- PIE + no leak means every address is unknown — a leak or a partial-overwrite trick is mandatory.
- Bad bytes in the read path (\x00 \x0a \x20 for most fgets/scanf) kill addresses containing them — pick different gadgets.
- movaps alignment inside libc faults on a misaligned stack — an extra ret gadget fixes parity.
- One-shot services can't re-trigger — the leak and the smash compose in one input, or the chain must be leak-free.

## Falsifier

Falsifier — the length is genuinely bounded and your input can't influence it: the read is safe; check a different input path.

## Highest-cost traps

- A signed 'n <= size' check passes negative n — the classic length bug.
- Off-by-one only buys one byte — useful for canary LSB zeroing or a one-byte frame-pointer shift.
- n from a network length field can wrap through int truncation.

## Commands

```bash
r2 -A ./chal && pdf @ <vuln> | grep -iE 'read|call|cmp'
```

## Cross-references

`read-family.md`
