# The PIE code leak — getting the base — checklist

Companion to `the-pie-code-leak.md`.

## Checklist

- [ ] A saved return address readable on the stack.
- [ ] A printed code pointer (a debug print, a fmtstr).
- [ ] A GOT entry pointing into the binary (rare — GOT points at libc).
