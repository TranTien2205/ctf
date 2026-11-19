# Heap leaks — where the addresses come from — checklist

Companion to `heap-leak.md`.

## Checklist

- [ ] UAF read of a freed tcache chunk: its fd leaks (mangled — de-mangle
- [ ] Reading `pos` itself: a chunk's own address embedded anywhere.
- [ ] main_arena pointers (unsorted leak) are libc, not heap — don't
- [ ] An app's own "print object" path may leak a heap pointer directly.
