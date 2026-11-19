# tools/gcm_nonce.py — the forbidden attack driver — deep

Recovers the GHASH subkey H from two nonce-reused records, then forges a tag for a chosen new ciphertext. Algebraic, deterministic — no oracle loop.

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

Falsifier — no nonce reuse in the captures, or the algebra produces no valid H: the pair was under different nonces or different keys.

## Highest-cost traps

- AAD changes the tag equation — always pass --aad1/--aad2 when present, even if identical.
- Multiple H candidates are normal — try each.
- Nonce reuse also lets you crib-drag the CTR stream: the same pair feeds tools/crypto_attack.py crib-drag too.

## Commands

```bash
python3 tools/gcm_nonce.py --selftest
python3 tools/gcm_nonce.py --ct1 <h> --tag1 <h> --ct2 <h> --tag2 <h>
```

## Cross-references

`gcm-nonce-reuse.md` · `ctr-nonce-reuse.md`
