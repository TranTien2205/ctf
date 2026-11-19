# libc gadgets — when the binary is thin


The binary's gadgets may be scarce — the LIBC's are abundant: with a
libc leak, the gadget set includes all of libc's code.

## The consequence

- A binary with no `pop rdx` can borrow libc's `pop rdx`.
- One-gadget lives in libc — the shortcut target.

## Falsifier

No libc leak: only the binary's own gadgets are addressable.
