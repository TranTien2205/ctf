# x86 cdecl deep — the stack args — deep

Companion to `the-callconv-x86.md`.

ROP composes ret-terminated gadgets into a program on the stack — the chain is addresses and argument values; rop_chain.py assembles the three common shapes, the rest is struct.pack.
