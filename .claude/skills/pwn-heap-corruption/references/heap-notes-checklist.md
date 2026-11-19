# Field notes — what to record during a heap run — checklist

Companion to `heap-notes.md`.

## Checklist

- [ ] the glibc version and how it was determined
- [ ] the menu ops and their allocator mapping
- [ ] the bug's primitive (UAF/dup/overflow/oob)
- [ ] the leaks obtained (which source, which range)
- [ ] the technique attempted and the check that caught it (the abort
- [ ] the alloc/free sequence that worked
- [ ] the write target and its firing condition
