# Offset measurement — getting the exact byte count — deep

The offset IS the bug's geometry: input_start → saved_return_address. Measure it empirically; never guess.

## Mechanism internals

The chain is a layout, not a payload: each qword on the smashed stack is either a gadget address or a consumed argument, in order. The three invariants: (1) the offset to saved RIP is measured, not assumed — every build can shift it; (2) each gadget's consumed stack slots must be filled before the next address; (3) the chain ends only on an address that exists at runtime — PIE means base+offset.

## Boundary conditions

- The canary is the countermeasure: a leak or a write-around is required, else __stack_chk_fail.
- PIE + no leak means every address is unknown — a leak or a partial-overwrite trick is mandatory.
- Bad bytes in the read path (\x00 \x0a \x20 for most fgets/scanf) kill addresses containing them — pick different gadgets.
- movaps alignment inside libc faults on a misaligned stack — an extra ret gadget fixes parity.
- One-shot services can't re-trigger — the leak and the smash compose in one input, or the chain must be leak-free.

## Falsifier

Falsifier — no input length produces a faulting RIP holding pattern bytes: the write doesn't reach saved state at this length; re-check the bound.

## Highest-cost traps

- The pattern is de Bruijn — every 4-byte window is unique; --find needs the 4 bytes from RIP.
- Offset = bytes to saved RIP; padding = offset - (bytes that precede it including saved RBP).
- The crash message's fault address in dmesg/stderr may be the DATA not RIP — read the register.

## Commands

```bash
python3 tools/pwn_cyclic.py 300
python3 tools/pwn_cyclic.py --find 0x6161616c
python3 tools/pwn_cyclic.py --selftest
```

## Cross-references

`cyclic-offset.md` · `tools-pwn-cyclic.md`
