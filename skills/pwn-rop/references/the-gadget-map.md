# The gadget map — what to search first


Order the /R searches by scarcity:

1. `/R syscall` — decides the static route.
2. `/R pop rdx` — the scarce arg pop.
3. `/R pop rax` — the syscall number setter.
4. `/R pop rsi`, `/R pop rdi` — the common ones.
5. `/R leave`, `/R mov` — pivots and writes.
6. `/R ret` — the aligner (usually abundant).

## The tool shortcut

`--gadgets` reports the essential set — the absence list is the
route's first constraint.
