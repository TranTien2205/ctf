# pop-all gadgets — the bulk register setter


`pop rbx; pop rbp; pop r12; pop r13; pop r14; pop r15; ret`-shaped
gadgets (the csu tail) set six registers at once — the universal
setup.

## The cost

Consumes six qwords — the chain must supply all six even when only a
few are used.
