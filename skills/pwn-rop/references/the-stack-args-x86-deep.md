# Stack args — the x86 call layout — deep

Companion to `the-stack-args-x86.md`.

ROP composes ret-terminated gadgets into a program on the stack — the chain is addresses and argument values; rop_chain.py assembles the three common shapes, the rest is struct.pack.
