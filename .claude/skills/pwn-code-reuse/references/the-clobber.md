# The clobber — gadgets that touch more


Real gadgets aren't clean: `pop rdi; ret` is clean, but `pop rdi; add
[rax], ebx; ret` also writes memory — audit each gadget's full tail.

## The audit

Read every gadget's FULL instruction sequence — a gadget that also
pops another register, writes memory, or jumps has side effects that
may clobber the chain.

## The safe choice

Prefer gadgets ending exactly in `pop rX; ret` — minimal side effects.
