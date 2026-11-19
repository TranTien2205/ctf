# The movaps crash — diagnosing misalignment


system() and other libc functions assume 16-byte rsp at entry — a chain
landing with rsp misaligned crashes on `movaps [rsp+..], xmm..`.

## The fix

Insert a bare `ret` gadget before the call — each ret advances rsp by
8; one ret usually restores alignment.

## The rule of thumb

If the call site was reached by an odd number of pushes since a known-
aligned point, add a ret.

## Falsifier

The crash is at a different instruction (not an xmm store): the cause
isn't alignment — check the actual faulting insn.
