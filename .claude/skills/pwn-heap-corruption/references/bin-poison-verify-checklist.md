# Verifying a bin poison — the two-malloc test — checklist

Companion to `bin-poison-verify.md`.

## Checklist

- [ ] 1. Poisoned fd set: the bin's head → your target.
- [ ] 2. malloc once → returns the freed chunk (consumes the head).
- [ ] 3. malloc twice → SHOULD return target: read its address.
- [ ] 4. If the second malloc returns the target: aim confirmed — write.
- [ ] Crash in _int_malloc → the fd aim was rejected (safe-linking
- [ ] Wrong address → pos in the mangle was wrong; recompute.
- [ ] Legit-looking but wrong → off-by-one in the chain.
