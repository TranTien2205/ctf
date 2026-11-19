# Padding the frame — the 248 bytes — deep

Companion to `the-frame-pad.md`.

ROP composes ret-terminated gadgets into a program on the stack — the chain is addresses and argument values; rop_chain.py assembles the three common shapes, the rest is struct.pack.
