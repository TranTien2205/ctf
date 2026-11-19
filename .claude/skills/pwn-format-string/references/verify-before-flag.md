# Verify before flag — the staged landing


Before firing the redirect, verify every piece: the offset, the planted
pointer, the count arithmetic, the target's address. A misfired write is
unrecoverable.

## Checks

- Offset verified — N correct (marker seen).
- Pointer planted — the arg holds it (check via %p).
- Count right — the value (the arithmetic).
- Target exists — the address valid (symbols).

## Falsifier

Any verification fails: fix that stage before the write.
