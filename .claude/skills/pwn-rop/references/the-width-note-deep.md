# The width — 8 vs 4 bytes — deep

Companion to `the-width-note.md`.

ROP composes ret-terminated gadgets into a program on the stack — the chain is addresses and argument values; rop_chain.py assembles the three common shapes, the rest is struct.pack.
