# The one-shot write — when you get exactly one call — checklist

Companion to `fmtstr-one-shot-write.md`.

## Checklist

- [ ] 1. Leak AND write in one call: %N$p specifiers read first, then the
- [ ] 2. The pointer must already be an arg (can't use a leaked addr to plant).
- [ ] 3. Target only deterministic addresses — non-PIE GOT, fixed hooks.
- [ ] 4. A win function needs no leak at all — pure write.
