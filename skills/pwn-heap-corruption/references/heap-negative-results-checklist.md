# Heap negative results — the kill map — checklist

Companion to `heap-negative-results.md`.

## Checklist

- [ ] tcache dup — key check fired on every attempt.
- [ ] fastbin — couldn't drain tcache (only 3 frees allowed).
- [ ] unsorted write — bck->fd check rejected.
- [ ] hooks — glibc 2.35, absent.
- [ ] FSOP — no write reached the FILE.
- [ ] ret-addr — no stack leak obtainable.
