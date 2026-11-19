# LD_PRELOAD angle — the env injection — deep

Companion to `the-ld-preload.md`.

ROP composes ret-terminated gadgets into a program on the stack — the chain is addresses and argument values; rop_chain.py assembles the three common shapes, the rest is struct.pack.
