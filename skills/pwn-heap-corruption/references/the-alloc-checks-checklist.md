# malloc() checks — the gates on allocation — checklist

Companion to `the-alloc-checks.md`.

## Checklist

- [ ] unsorted: bck->fd == victim; size sane.
- [ ] smallbin unlink: fd->bk == chunk && bk->fd == chunk (2.30+).
- [ ] largebin: size ordering consistent.
- [ ] tcache get: e->key cleared after take (2.32+); counts decremented.
- [ ] top: size not absurd (2.29+).
