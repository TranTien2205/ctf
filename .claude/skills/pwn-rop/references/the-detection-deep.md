# Detecting the ROP case — when this skill applies — deep

Companion to `the-detection.md`.

ROP composes ret-terminated gadgets into a program on the stack — the chain is addresses and argument values; rop_chain.py assembles the three common shapes, the rest is struct.pack.
