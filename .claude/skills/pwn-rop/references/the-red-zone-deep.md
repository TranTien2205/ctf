# The red zone — the 128 bytes below rsp — deep

Companion to `the-red-zone.md`.

ROP composes ret-terminated gadgets into a program on the stack — the chain is addresses and argument values; rop_chain.py assembles the three common shapes, the rest is struct.pack.
