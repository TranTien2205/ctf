# ret2libc — call libc functions via a leak — deep

When the binary imports no system but links libc, a leak of ANY libc address plus the known offset reaches system()/execve(). The chain is leak → compute base → call.

## Mechanism internals

The chain is a layout, not a payload: each qword on the smashed stack is either a gadget address or a consumed argument, in order. The three invariants: (1) the offset to saved RIP is measured, not assumed — every build can shift it; (2) each gadget's consumed stack slots must be filled before the next address; (3) the chain ends only on an address that exists at runtime — PIE means base+offset.

## Boundary conditions

- The canary is the countermeasure: a leak or a write-around is required, else __stack_chk_fail.
- PIE + no leak means every address is unknown — a leak or a partial-overwrite trick is mandatory.
- Bad bytes in the read path (\x00 \x0a \x20 for most fgets/scanf) kill addresses containing them — pick different gadgets.
- movaps alignment inside libc faults on a misaligned stack — an extra ret gadget fixes parity.
- One-shot services can't re-trigger — the leak and the smash compose in one input, or the chain must be leak-free.

## Falsifier

Falsifier — no leak primitive exists (no read to an address you control, no puts of a pointer): libc base stays hidden; ret2libc is out without it.

## Highest-cost traps

- The libc VERSION matters for offsets — leak more than one address or fingerprint it.
- puts(GOT[x]) prints the resolved address of x — if x isn't resolved yet it's the PLT address; call it once first.
- system needs '/bin/sh' — a leak of libc gives the string too (search the leaked range or compute its offset).

## Commands

```bash
r2 -A ./chal && is @ libc
readelf -r ./chal | grep GOT
```

## Cross-references

`ret2plt.md` · `pie-leak.md` · `rop-basics.md`
