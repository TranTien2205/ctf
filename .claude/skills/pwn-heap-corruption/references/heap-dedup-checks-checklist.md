# The security checks — what glibc verifies — checklist

Companion to `heap-dedup-checks.md`.

## Checklist

- [ ] free(): size sane, aligned; tcache key check (2.29+); double-free
- [ ] fastbin unlink: chunk size vs bin size match.
- [ ] smallbin unlink: fd->bk == chunk && bk->fd == chunk (2.30+).
- [ ] tcache_get: aligned; counts consistent; e->key cleared on take (2.32+).
- [ ] _int_malloc: unsorted chunk size sane; nextsize invariants.
- [ ] malloc top: size not absurd (2.29+ force-check).
