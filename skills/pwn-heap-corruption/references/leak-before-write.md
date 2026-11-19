# Leak before write — the order that survives versions


On modern glibc, the write aim needs a leaked address (safe-linking);
the version's hooks may be gone entirely. Leak first, always.

## The leak ladder

1. Unsorted-bin fd/bk → libc base (the free leak).
2. Heap fd de-mangle → heap base (safe-linking requires it).
3. environ (libc offset) → stack.
4. A leaked code pointer → binary base (PIE).

## Why the order

Every version-gated write (safe-linking aim, hook addresses, FSOP
vtable) consumes an address only a leak supplies. A leakless write is a
blind write — only deterministic targets remain.

## Falsifier

No leak primitive exists at all (no dangling read, no info disclosure):
only version-tolerant, address-free techniques remain — often none.
