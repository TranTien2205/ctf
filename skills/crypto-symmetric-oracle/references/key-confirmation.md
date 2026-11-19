# Key confirmation and weak keys

Sometimes the 'oracle' answer is 'the key worked' — a key-confirmation
protocol. Brute-forcing a small key space through it is a valid attack.

## Shapes

| Surface | Signal | Attack |
|---|---|---|
| 'decrypt with key X' endpoint | ok/invalid | brute the key space |
| Handshake that confirms a shared key | success/fail | offline dictionary |
| Key = 4-byte PIN / 16-bit space | tiny | enumerate directly |
| Key derived from timestamp | ~seconds of space | seed-search |

## DES weak keys (rare but named)

DES has 4 weak and 12 semi-weak keys where encryption = decryption under
paired keys. A service that 'decrypts' with a weak key returns the plaintext
under ENC. Check if the handout screams DES.

## Enumeration discipline

- Bound the space first: a 32-bit keyspace is 4G — too big. A 16-bit is
  65k — fine.
- The distinguisher is 'key correct' — one answer, not a per-byte oracle.
- Precompute offline where possible: an offline dictionary beats an online
  loop.

## Boundary

A brute-force against a full 128-bit key is never the intended attack —
find the weakness (seed, KDF, leak) instead.
