# The tail check — ret or die


The last instruction of every gadget: ret (0xc3) or equivalent —
a gadget that doesn't reach a ret ends the chain.

## The audit

Every gadget must END in a transfer that continues the chain —
ret usually; jmp/call with a controlled target also.
