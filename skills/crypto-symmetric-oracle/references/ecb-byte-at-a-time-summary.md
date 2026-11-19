# Byte-at-a-time ECB decryption — summary

ECB + attacker-controlled prefix = an encryption oracle you can read secrets out of, one byte per position. The classic recipe: keep the secret's first unknown byte at the end of a controlled block, brute that byte through all 256 guesses, advance.

## Signal → route

- You control a prefix position before a hidden secret in the same plaintext → alignment then the guess loop
- Appended secret length measurable by growing input → boundary measurement
- Random prefix before your input → find the fixed suffix or give up ECB

## Falsifier

Falsifier — the recovered plaintext stops being printable/structured partway through, or no candidate ever matches: the mode is not ECB or the 'secret' is encrypted separately (different key or different transform).
