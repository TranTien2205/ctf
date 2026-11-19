# The stack pivot — when the chain doesn't fit


When the controllable region is too small for the full chain: pivot rsp
into a bigger region — `leave; ret` or `xchg/add rsp`-shaped gadgets
move the stack.

## The gadgets

- `leave; ret` — rsp = rbp; rbp = [rsp]; rsp += 8 — if rbp is
  controllable, rsp moves to rbp.
- `xchg rsp, rXX; ret` — direct move.
- `add rsp, N; ret` — skip N bytes.

## The recipe

1. Control a buffer's address (a known writable region).
2. Fill it with the real chain.
3. The first stage pivots rsp into it.

## Falsifier

No pivot gadget exists and no controllable region is mapped: the
chain is bounded by the real buffer's size.
