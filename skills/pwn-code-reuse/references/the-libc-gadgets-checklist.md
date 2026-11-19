# libc gadgets — when the binary is thin — checklist

Companion to `the-libc-gadgets.md`.

## Checklist

- [ ] A binary with no `pop rdx` can borrow libc's `pop rdx`.
- [ ] One-gadget lives in libc — the shortcut target.
