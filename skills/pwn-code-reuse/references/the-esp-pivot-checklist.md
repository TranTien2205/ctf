# The esp/rsp pivot — moving the stack — checklist

Companion to `the-esp-pivot.md`.

## Checklist

- [ ] `leave; ret` — rsp = rbp; pop rbp; ret — rbp control pivots.
- [ ] `xchg eax/esp`-shaped — direct.
- [ ] `pop rsp` — rare but direct.
- [ ] `add rsp, N` — skip N bytes of the frame.
