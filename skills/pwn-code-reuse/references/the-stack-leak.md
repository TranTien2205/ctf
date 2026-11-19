# The stack leak — for ret-addr targets


A saved-return write or a pivot target needs a stack address — leaked
via a saved rbp, an argv/env pointer, or libc's environ.

## Sources

- A saved rbp in the dump — *rbp+8 = saved ret.
- environ — libc global → stack pointer.
- An argv pointer — the stack top.

## Falsifier

No stack address is derivable: ret-addr writes can't aim — use
non-stack targets.
