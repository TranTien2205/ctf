# The esp/rsp pivot — moving the stack


A pivot gadget moves rsp into your controlled region — the chain
continuation depends on where rsp lands.

## The gadgets

- `leave; ret` — rsp = rbp; pop rbp; ret — rbp control pivots.
- `xchg eax/esp`-shaped — direct.
- `pop rsp` — rare but direct.
- `add rsp, N` — skip N bytes of the frame.

## Falsifier

No pivot exists and the real frame is the only chain space.
