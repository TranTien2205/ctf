# The gadget tail — reading past the headline — checklist

Companion to `the-gadget-tail.md`.

## Checklist

- [ ] `pop rdi; pop r14; ret` — consumes two qwords.
- [ ] `pop rdi; call rax` — a call in the middle.
- [ ] `pop rdi; mov [r15], r14; ret` — a memory write side effect.
