# Finding the canary in a %p dump — checklist

Companion to `the-canary-in-dump.md`.

## Checklist

- [ ] 1. Dump %p; look for a word whose low byte is 0.
- [ ] 2. Canaries: random, high-entropy, low byte 0x00.
- [ ] 3. Verify: the same N shows the canary each call (if forking, same value).
- [ ] 4. Use it to preserve the canary in a smash.
