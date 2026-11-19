# More stack args — the x86 multi-arg — deep

Companion to `the-stack-arg2.md`.

ROP composes ret-terminated gadgets into a program on the stack — the chain is addresses and argument values; rop_chain.py assembles the three common shapes, the rest is struct.pack.
