# The arg-offset sweep — the precise protocol — checklist

Companion to `arg-offset-sweep-protocol.md`.

## Checklist

- [ ] 1. Send 'AAAABBBB' + '.%N$p' for N=1..~30.
- [ ] 2. The N printing 0x4242424241414141 (or the aligned variant) is your arg
- [ ] 3. If the marker straddles a boundary, you'll see it at N and N+1 — pick
- [ ] 4. Record N — all %N$ ops use it.
