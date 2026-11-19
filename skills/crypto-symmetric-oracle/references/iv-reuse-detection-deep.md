# IV/nonce reuse detection — the cheap check — deep

Before any IV-dependent attack, confirm reuse exists. One grep or one pair of captures answers it.

## Mechanism internals

The attack surface is defined by which byte the service lets you reach and which bit of the response leaks. The three invariants that hold across every variant of this attack: (1) the distinguisher must be measurable before the loop starts, (2) each recovered byte is confirmed by an exact-match answer — never a probabilistic one, (3) the loop stops at the measured boundary (block edge, secret length, tag width), not where the bytes 'look done'.

## Boundary conditions

- If the response is compressed before encryption, alignment dies — check for gzip/deflate first.
- If the oracle answers 'ok' for structurally invalid input, the parser layer is the bug, not the crypto.
- Rate limits convert a 40k-request loop into days — measure throughput and bound --max-requests.
- Nonce reuse at the block level is different from per-message reuse — align by absolute counter.
- A MAC checked before decryption closes every malleability route in this file.
- When the same tool flag is documented differently in two modules, tools/<name>.py --help is authoritative.

## Falsifier

Falsifier — every captured nonce is distinct AND the space is large enough to never collide at the sample size you can reach: reuse does not occur.

## Highest-cost traps

- Nonce reuse in CTR is per-BLOCK-counter — two messages with different nonce headers can still share keystream blocks.
- A 'random' 32-bit nonce collides at ~77k captures — within reach of fast collection.
- Source-level 'IV = os.urandom(8)' is a 64-bit nonce — birthdays at ~4 billion; not reachable.

## Commands

```bash
python3 tools/crypto_attack.py list
```

## Cross-references

`ctr-nonce-reuse.md` · `gcm-nonce-reuse.md`
