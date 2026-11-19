# The PIE code leak — getting the base — deep

Companion to `the-pie-code-leak.md`.

ROP composes ret-terminated gadgets into a program on the stack — the chain is addresses and argument values; rop_chain.py assembles the three common shapes, the rest is struct.pack.
