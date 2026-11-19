# The pivot — moving the stack


When the buffer can't hold the chain: redirect rsp to a controlled
region.

## The gadgets

- `pop rsp; ret` — rsp = the next qword.
- `leave; ret` — rsp = rbp; then a ret pops from there (set rbp
  first via the saved-rbp slot or a pop rbp).
- `xchg rsp, rax; ret` — if rax holds the region.
- `add rsp, N; ret` — a partial skip.

## The planted chain

The real chain lives at the region the overflow + a write planted.
