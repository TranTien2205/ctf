# The security checks — what glibc verifies


glibc hardens each version; the corruption must satisfy the checks on
the path it takes.

## The checklist per technique

- free(): size sane, aligned; tcache key check (2.29+); double-free
  detection.
- fastbin unlink: chunk size vs bin size match.
- smallbin unlink: fd->bk == chunk && bk->fd == chunk (2.30+).
- tcache_get: aligned; counts consistent; e->key cleared on take (2.32+).
- _int_malloc: unsorted chunk size sane; nextsize invariants.
- malloc top: size not absurd (2.29+ force-check).

## Reading the abort message

glibc prints the check name — "malloc(): corrupted top size", "double
free or corruption (fasttop)" — the message names which check caught
you: that's the check to bypass, not the technique to abandon.

## Falsifier

Every path's checks reject the corruption: the primitive needs a
different entry, not more force.
