# The arg0 path — the pointer to /bin/sh — deep

Companion to `the-arg0-path.md`.

ROP composes ret-terminated gadgets into a program on the stack — the chain is addresses and argument values; rop_chain.py assembles the three common shapes, the rest is struct.pack.
