# Arg order — which pop first


The pops' order is free — but a gadget's side effects constrain it:
a `pop rdi; pop r15` that ALSO writes r15's memory must come after
r15 is safe to clobber.

## The rule

Set the registers in the order the chain needs them USED; a register
used early is set early only if nothing clobbers it.
