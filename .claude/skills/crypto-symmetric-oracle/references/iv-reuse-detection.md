# IV/nonce reuse detection — the cheap check

Before any IV-dependent attack, confirm reuse exists. One grep or one pair of captures answers it.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| Same nonce in two different responses | reuse confirmed | gcm/ctr attack |
| IV is all-zero or a constant in source | static IV | cbc or ctr attack |
| Nonce = incrementing counter | predictable not reused | watch for wrap |

## Steps

1. Collect all captured nonces; sort and diff — reuse is immediate.
2. If source is available, grep for the IV/nonce initialization.
3. For a counter, check its width and starting point — a 32-bit counter wraps at 4G messages.
4. For random nonces, check width: <96 bits collides by birthday after a few thousand captures.

## Falsifier

Falsifier — every captured nonce is distinct AND the space is large enough to never collide at the sample size you can reach: reuse does not occur.

## Traps

- Nonce reuse in CTR is per-BLOCK-counter — two messages with different nonce headers can still share keystream blocks.
- A 'random' 32-bit nonce collides at ~77k captures — within reach of fast collection.
- Source-level 'IV = os.urandom(8)' is a 64-bit nonce — birthdays at ~4 billion; not reachable.

## Commands

```bash
python3 tools/crypto_attack.py list
```

## Cross-references

`ctr-nonce-reuse.md` · `gcm-nonce-reuse.md`
