# IV/nonce reuse detection — the cheap check — operational checklist

Before any IV-dependent attack, confirm reuse exists. One grep or one pair of captures answers it.

## Checklist

- [ ] Collect all captured nonces; sort and diff — reuse is immediate.
- [ ] If source is available, grep for the IV/nonce initialization.
- [ ] For a counter, check its width and starting point — a 32-bit counter wraps at 4G messages.
- [ ] For random nonces, check width: <96 bits collides by birthday after a few thousand captures.

## Abort conditions

- Nonce reuse in CTR is per-BLOCK-counter — two messages with different nonce headers can still share keystream blocks.
- A 'random' 32-bit nonce collides at ~77k captures — within reach of fast collection.
- Source-level 'IV = os.urandom(8)' is a 64-bit nonce — birthdays at ~4 billion; not reachable.

## Falsifier

Falsifier — every captured nonce is distinct AND the space is large enough to never collide at the sample size you can reach: reuse does not occur.

## Cross-references

`ctr-nonce-reuse.md` · `gcm-nonce-reuse.md`
