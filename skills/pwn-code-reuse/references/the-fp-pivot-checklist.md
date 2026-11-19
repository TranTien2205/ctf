# The saved-fp pivot — leave;ret explained — checklist

Companion to `the-fp-pivot.md`.

## Checklist

- [ ] 1. Overflow sets rbp = your-chain-buffer (in a second write or a
- [ ] 2. The function's epilogue `leave; ret` pivots rsp into your buffer.
- [ ] 3. The chain runs from there.
