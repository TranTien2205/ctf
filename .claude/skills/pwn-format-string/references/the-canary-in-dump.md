# Finding the canary in a %p dump


The canary is a word whose low byte is 0x00 — in a %p dump it looks like
0x<15 hex digits>0 or similar; on x64 it's typically at a mid-depth.

## Steps

1. Dump %p; look for a word whose low byte is 0.
2. Canaries: random, high-entropy, low byte 0x00.
3. Verify: the same N shows the canary each call (if forking, same value).
4. Use it to preserve the canary in a smash.

## Falsifier

No 00-low-byte word in the dump at the canary's expected depth: either no
canary (check triage) or it's at another N. The TLS canary is copied into
each frame — it IS on the stack, position varies.
