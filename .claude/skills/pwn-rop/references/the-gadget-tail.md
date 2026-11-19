# The gadget tail — reading past the headline


A gadget's full tail may do more than its headline instruction:

- `pop rdi; pop r14; ret` — consumes two qwords.
- `pop rdi; call rax` — a call in the middle.
- `pop rdi; mov [r15], r14; ret` — a memory write side effect.

## The audit

    pd 6 @ gadget_addr

Read the whole sequence to the ret — budget the side effects.
