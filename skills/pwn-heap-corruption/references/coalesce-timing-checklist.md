# When consolidation fires — the trigger map — checklist

Companion to `coalesce-timing.md`.

## Checklist

- [ ] free() of a non-fastbin/tcache chunk adjacent to a free one.
- [ ] _int_malloc on an unsorted sweep.
- [ ] malloc_consolidate called on large requests.
- [ ] free() of the chunk just below top (top-merge).
