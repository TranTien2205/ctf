# The final walk — the chain executed


Mentally executing the chain, register state at each ret:

- after pop rdi: rdi=binsh
- after ret: rsp+8 (aligned)
- at system: rdi=binsh, rsp aligned → the call is valid
- system's return → exit

## The verify

The r2 -d walk confirms the mental model — a divergence is the bug.
