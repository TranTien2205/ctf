# The chain builder — rop_chain.py — checklist

Companion to `the-builder.md`.

## Checklist

- [ ] Finds the pop gadgets itself in the binary.
- [ ] Packs `pop rdi/rsi/rdx` chains in argument order.
- [ ] Inserts a bare `ret` when the qword count leaves rsp misaligned.
- [ ] ret2plt resolves the stub itself: walks .rela.plt to the symbol's
