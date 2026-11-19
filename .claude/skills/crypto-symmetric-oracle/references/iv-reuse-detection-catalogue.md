# IV/nonce reuse detection — the cheap check — case catalogue

Before any IV-dependent attack, confirm reuse exists. One grep or one pair of captures answers it.

## Cases

| # | Shape | Distinguisher | Attack |
|---|---|---|---|
| 1 | Same nonce in two different responses | reuse confirmed | gcm/ctr attack |
| 2 | IV is all-zero or a constant in source | static IV | cbc or ctr attack |
| 3 | Nonce = incrementing counter | predictable not reused | watch for wrap |

## Falsifier

Falsifier — every captured nonce is distinct AND the space is large enough to never collide at the sample size you can reach: reuse does not occur.

## Coverage notes

- Nonce reuse in CTR is per-BLOCK-counter — two messages with different nonce headers can still share keystream blocks.
- A 'random' 32-bit nonce collides at ~77k captures — within reach of fast collection.
- Source-level 'IV = os.urandom(8)' is a 64-bit nonce — birthdays at ~4 billion; not reachable.

## Cross-references

`ctr-nonce-reuse.md` · `gcm-nonce-reuse.md`
