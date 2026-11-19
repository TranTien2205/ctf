# CBC bit-flipping — targeted plaintext edits — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| You need 'user' → 'admin' or a number changed in a CBC token | bit-flip applies | locate offset, flip bytes |
| The token's IV is prepended and attacker-controlled | first block is fully controllable | edit P_1 via IV |
| Scrambled block must stay parseable | needs structure tolerant to garbage | use IV or a don't-care block |

## Falsifier

Falsifier — the token is authenticated and any modification is rejected, or the parser rejects the inevitable garbage block: bit-flip survives neither.
