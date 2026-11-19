# mmap variants — the flags question — checklist

Companion to `the-mmap-variant.md`.

## Checklist

- [ ] MAP_ANONYMOUS|MAP_PRIVATE = 0x22 — the usual.
- [ ] If r10 can't be set: use MAP_SHARED with a valid fd, or a different
