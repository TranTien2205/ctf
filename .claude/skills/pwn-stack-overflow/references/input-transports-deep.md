# Input transports — where the smash's bytes come from — deep

stdin, argv, env, a socket, a file — each transport carries the payload with its own byte restrictions and re-trigger semantics.

## Mechanism internals

The chain is a layout: qword-by-qword, gadget addresses interleaved with their consumed stack slots, ending on an address that exists at runtime. Invariants: the offset is measured not assumed; each gadget's consumed slots are filled before the next address; PIE means every static address is base+offset.

## Boundary conditions

- Canary blocks a naive smash — leak or write around it.
- PIE + no leak means addresses are unknown.
- Bad bytes in the read path truncate addresses containing them.
- movaps alignment faults on a misaligned stack — ret-pad.
- One-shot services can't re-trigger — compose leak+smash in one input.

## Falsifier

Falsifier — the transport isn't what you assumed (e.g., it's a socket field, not stdin): the byte-filtering/re-trigger rules change.

## Highest-cost traps

- A socket read is raw bytes; a fgets stops at newline.
- argv/env \x00 restriction kills null bytes in addresses.
- A file-read payload can contain any byte.

## Cross-references

`read-family.md` · `bad-chars.md` · `argv-control.md`
