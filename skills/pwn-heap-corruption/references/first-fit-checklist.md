# First-fit and bin order — where allocs come from — checklist

Companion to `first-fit.md`.

## Checklist

- [ ] 1. tcache: exact-size match, LIFO.
- [ ] 2. fastbin: exact-size match, LIFO.
- [ ] 3. unsorted: first-fit, one scan — leftovers get sorted into
- [ ] 4. small/large: best-fit sorted lists.
- [ ] 5. top chunk: split from the wilderness.
- [ ] 6. mmap: huge requests skip the heap entirely.
- [ ] Same-size LIFO: the last freed is the next returned — the basis of
- [ ] Large allocs skip tcache — they hit unsorted/bin paths directly.
