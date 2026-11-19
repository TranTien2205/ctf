# Long chains — the ordering discipline


A chain of many gadgets has ordering constraints: each pop consumes
its arg slot; the sequence must compose without register interference.

## The rule

- A pop clobbers its register only — other regs survive.
- Order so that a register needed LATER is set LATER (a gadget may
  clobber a reg you set earlier — check each gadget's full instruction).
- A gadget like `pop rdi; pop r15; ret` sets BOTH — the r15 is a
  scratch you tolerate.

## Falsifier

Two needed settings conflict (one gadget clobbers the other): reorder
or find a non-clobbering gadget.
