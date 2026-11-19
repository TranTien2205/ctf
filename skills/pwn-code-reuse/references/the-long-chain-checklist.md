# Long chains — the ordering discipline — checklist

Companion to `the-long-chain.md`.

## Checklist

- [ ] A pop clobbers its register only — other regs survive.
- [ ] Order so that a register needed LATER is set LATER (a gadget may
- [ ] A gadget like `pop rdi; pop r15; ret` sets BOTH — the r15 is a
