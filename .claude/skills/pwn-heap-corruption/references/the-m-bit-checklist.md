# The M bit — the mmap marker — checklist

Companion to `the-m-bit.md`.

## Checklist

- [ ] A chunk wrongly M-flagged: free() munmaps it — "munmap_chunk():
- [ ] Rarely useful directly; mainly a "don't" — don't accidentally set M.
