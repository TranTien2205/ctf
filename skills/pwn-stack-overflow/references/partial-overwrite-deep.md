# Partial overwrite — low-byte control without a full leak — deep

Can't leak a full pointer? Overwrite only the low 1-2 bytes of a saved return or GOT entry — redirect to a nearby target in the same page.

## Mechanism internals

The chain is a layout: qword-by-qword, gadget addresses interleaved with their consumed stack slots, ending on an address that exists at runtime. Invariants: the offset is measured not assumed; each gadget's consumed slots are filled before the next address; PIE means every static address is base+offset.

## Boundary conditions

- Canary blocks a naive smash — leak or write around it.
- PIE + no leak means addresses are unknown.
- Bad bytes in the read path truncate addresses containing them.
- movaps alignment faults on a misaligned stack — ret-pad.
- One-shot services can't re-trigger — compose leak+smash in one input.

## Falsifier

Falsifier — the low-byte-controlled target doesn't include any useful gadget/function: no partial redirect is possible.

## Highest-cost traps

- The low bytes are the least ASLR'd — a 12-bit-page is deterministic.
- Same-page redirect: useful for reaching a gadget one page over.
- Works on saved return addresses and GOT entries alike.

## Cross-references

`pie-leak.md` · `fgot-overwrite.md`
