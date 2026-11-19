# Before the chain — the offset and the canary


The chain sits after the offset: the cyclic-measured distance to the
saved rip, plus the canary slot if present.

## The pre-chain requirements

- The offset: pwn_cyclic measured.
- The canary: leaked and placed (if present).
- The chain start: the saved-rip slot.

## Falsifier

The offset isn't verified: the chain lands in the wrong place —
measure first.
