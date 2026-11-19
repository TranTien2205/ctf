# The stack pivot — when the chain doesn't fit — checklist

Companion to `the-pivot.md`.

## Checklist

- [ ] `leave; ret` — rsp = rbp; rbp = [rsp]; rsp += 8 — if rbp is
- [ ] `xchg rsp, rXX; ret` — direct move.
- [ ] `add rsp, N; ret` — skip N bytes.
- [ ] 1. Control a buffer's address (a known writable region).
- [ ] 2. Fill it with the real chain.
- [ ] 3. The first stage pivots rsp into it.
