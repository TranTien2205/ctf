# The array's end — the NULL sentinel — deep

Companion to `the-arr-end.md`.

ROP composes ret-terminated gadgets into a program on the stack — the chain is addresses and argument values; rop_chain.py assembles the three common shapes, the rest is struct.pack.
