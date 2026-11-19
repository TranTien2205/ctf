# tools/gcm_nonce.py — the forbidden attack driver — operational checklist

Recovers the GHASH subkey H from two nonce-reused records, then forges a tag for a chosen new ciphertext. Algebraic, deterministic — no oracle loop.

## Checklist

- [ ] python3 tools/gcm_nonce.py --selftest.
- [ ] Collect the two records under one nonce; extract ciphertext hex and tag hex.
- [ ] python3 tools/gcm_nonce.py --ct1 <h> --tag1 <h> --ct2 <h> --tag2 <h> [--aad1 --aad2].
- [ ] Try each returned H: python3 tools/gcm_nonce.py --h <H> --ct <chosen-ct> --new-ct <new-ct>.
- [ ] Submit the forged pair; an accepted tag is impact evidence.

## Abort conditions

- AAD changes the tag equation — always pass --aad1/--aad2 when present, even if identical.
- Multiple H candidates are normal — try each.
- Nonce reuse also lets you crib-drag the CTR stream: the same pair feeds tools/crypto_attack.py crib-drag too.

## Falsifier

Falsifier — no nonce reuse in the captures, or the algebra produces no valid H: the pair was under different nonces or different keys.

## Cross-references

`gcm-nonce-reuse.md` · `ctr-nonce-reuse.md`
