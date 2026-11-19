# call reg — the indirect call gadget


`call rax; ret`-shaped: calls the register's target then returns —
a call AND a continue — a call that doesn't end the chain.

## The use

`call rax` where rax = your function: the call fires, then the ret
continues the chain — a mid-chain call.
