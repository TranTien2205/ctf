# Smallbin's double-link check — 2.30+


glibc 2.30+ verifies `victim->bck->fd == victim` before unlink: the
backward link's forward must point home — the check that killed the
classic unlink.

## Around it

- The fake links must be self-consistent in BOTH directions — a full
  fake chunk inside controlled memory satisfies it.
- Or the write targets a context where the check doesn't run (tcache,
  fastbin top).

## Falsifier

Only one direction is forgeable: unlink is closed — use tcache/fastbin
paths that skip the check.
