# The send path — getting bytes down the wire — deep

Companion to `the-send-path2.md`.

ROP composes ret-terminated gadgets into a program on the stack — the chain is addresses and argument values; rop_chain.py assembles the three common shapes, the rest is struct.pack.
