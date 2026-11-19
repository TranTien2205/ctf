# malloc() checks — the gates on allocation


_int_malloc verifies bin-walk integrity: the checks your poisoned bins
must pass.

## The gates

- unsorted: bck->fd == victim; size sane.
- smallbin unlink: fd->bk == chunk && bk->fd == chunk (2.30+).
- largebin: size ordering consistent.
- tcache get: e->key cleared after take (2.32+); counts decremented.
- top: size not absurd (2.29+).

## Exploitation reading

A poisoned bin survives only if the walk's checks pass — the "arbitrary
alloc" is gated by the bin's own invariants.

## Falsifier

The walk's checks reject the corruption: the aim must satisfy the bin's
invariants, not just the fd field.
