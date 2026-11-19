# Crib-dragging — reading P1 XOR P2 — summary

With P1 XOR P2 in hand (from a reused keystream), a guessed word in one message reveals the corresponding bytes of the other. Slide the crib across offsets; each hit grows the recovered region.

## Signal → route

- P1 XOR P2 contains printable-on-both-sides at some offset → extend left and right
- Crib produces gibberish everywhere → try common protocol words
- Both messages partially known → iterate the loop

## Falsifier

Falsifier — every offset under every reasonable crib is non-printable in at least one direction: the keystreams were not the same (nonces differ) or the underlying data is binary/compressed.
