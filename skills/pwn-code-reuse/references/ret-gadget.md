# The bare ret — stack alignment


A lone `ret` gadget in the chain consumes one qword and advances rsp —
its real job: fixing 16-byte alignment before a call target that needs
it (movaps crashes inside system/libc otherwise).

## When it's needed

- system()/many libc calls require 16-byte rsp alignment at entry —
  a chain landing mid-function on a misaligned rsp crashes on movaps.
- Insert one `ret` before the call target — the crash becomes a clean
  call.

## Diagnostic

A chain that crashes inside libc at `movaps` is alignment, not a bad
chain — add a ret.

## Falsifier

The crash isn't in an alignment-sensitive instruction: the ret isn't
the fix — re-examine the chain.
