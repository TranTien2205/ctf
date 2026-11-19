# Authenticated modes — where the class closes — case catalogue

GCM, ChaCha20-Poly1305, and encrypt-then-MAC kill every malleability oracle. The honest skill boundary: recognize when NOTHING here applies and route out early.

## Cases

| # | Shape | Distinguisher | Attack |
|---|---|---|---|
| 1 | Tag verified before any decryption | oracles closed | nonce reuse or key-path only |
| 2 | Tampering uniformly rejected | no distinguisher | reclassify |
| 3 | Nonce/IV visible and reused across records | authenticated but misused | gcm-nonce-reuse or ctr reuse |
| 4 | Key/seed/IV leaked in source or params | not a crypto attack — read the flag | direct decryption |

## Falsifier

Falsifier — corrupt ciphertext is rejected identically for every offset tested: the class is closed. Continuing to probe malleability is budget waste.

## Coverage notes

- Constant-time compare makes TIMING identical too — do not confuse 'no timing signal' with 'bug present'.
- A 96-bit GCM nonce with random generation collides after ~2^32 messages — rarely reachable in CTF scale.
- Some CTF handouts label the mode 'AES-256' without the mode — check ciphertext length vs plaintext length and tag presence.

## Cross-references

`oracle-shapes.md` · `gcm-nonce-reuse.md` · `class-boundary.md`
