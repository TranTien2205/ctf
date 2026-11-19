# Libc fingerprinting — which libc is it? — deep

A leaked libc address is only useful with the right libc VERSION's offsets: fingerprint the version from two leaked symbols or the libc.so the challenge ships.

## Mechanism internals

The chain is a layout: qword-by-qword, gadget addresses interleaved with their consumed stack slots, ending on an address that exists at runtime. Invariants: the offset is measured not assumed; each gadget's consumed slots are filled before the next address; PIE means every static address is base+offset.

## Boundary conditions

- Canary blocks a naive smash — leak or write around it.
- PIE + no leak means addresses are unknown.
- Bad bytes in the read path truncate addresses containing them.
- movaps alignment faults on a misaligned stack — ret-pad.
- One-shot services can't re-trigger — compose leak+smash in one input.

## Falsifier

Falsifier — the leaked address doesn't match any known libc version's deltas: the leak isn't a libc pointer, or the libc is nonstandard.

## Highest-cost traps

- A single leaked address doesn't identify the version — you need two.
- The shipped libc.so.6 is authoritative — prefer it over fingerprints.
- Wrong-version offsets make the chain crash at the wrong address.

## Commands

```bash
nm -D libc.so.6 | grep -iE ' system$| execve$| puts$'
readelf -s libc.so.6 | grep system
```

## Cross-references

`ret2libc.md` · `pie-leak.md`
