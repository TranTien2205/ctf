# The .dynamic section — the linker's data — deep

Companion to `the-dyn-sec.md`.

ROP composes ret-terminated gadgets into a program on the stack — the chain is addresses and argument values; rop_chain.py assembles the three common shapes, the rest is struct.pack.
