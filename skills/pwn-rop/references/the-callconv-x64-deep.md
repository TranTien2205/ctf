# x64 SysV deep — the register order — deep

Companion to `the-callconv-x64.md`.

ROP composes ret-terminated gadgets into a program on the stack — the chain is addresses and argument values; rop_chain.py assembles the three common shapes, the rest is struct.pack.
