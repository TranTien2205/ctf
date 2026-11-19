# The show op — the leak channel — checklist

Companion to `the-show-op.md`.

## Checklist

- [ ] show on a tcache'd chunk → mangled fd + (pos) — heap leak data.
- [ ] show on an unsorted chunk → main_arena address — the libc leak.
- [ ] show on a UAF-overlapped chunk → the overlapping object's fields.
