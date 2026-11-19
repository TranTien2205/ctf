# Detecting the reuse case — when this class applies


The class applies when: IP control is proven AND NX is on AND the
payload must borrow code rather than inject it.

## Signals

- A stack/format overwrite confirmed (cyclic offset verified).
- NX reported by the triage — no RWX page.
- The exploit needs actions the bug alone can't express (calls,
  syscalls, writes).

## The boundary test

If shellcode can run (RWX page or NX off): the class doesn't apply —
inject, don't chain.

## Falsifier

No IP control yet: the upstream primitive is the real class — return
to it first.
