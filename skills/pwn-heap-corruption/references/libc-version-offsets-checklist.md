# Computing libc offsets — leak to base — checklist

Companion to `libc-version-offsets.md`.

## Checklist

- [ ] main_arena symbol: unsorted-bin fd/bk on the first big free.
- [ ] __free_hook/__malloc_hook: derived from the arena offset.
- [ ] system/other imports: from the base once known.
- [ ] The offset differs per libc build — the 2.31 offset is not 2.35's.
- [ ] If the challenge ships its libc, compute from THAT file, not from a
