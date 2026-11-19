# tools/gcm_nonce.py — the forbidden attack driver

Recovers the GHASH subkey H from two nonce-reused records, then forges a tag for a chosen new ciphertext. Algebraic, deterministic — no oracle loop.

## Signals

| Observation | Meaning | Route |
|---|---|---|
| --ct1 --tag1 --ct2 --tag2 = the reused pair | input pair | must share a nonce |
| --aad1 --aad2 when AAD differs | auth-data included | omitting it changes the algebra |
| --h + --ct/--new-ct = forgery mode | H to forged tag | test each H candidate |
| --selftest proves the algebra | local check | run first |

## Steps

1. python3 tools/gcm_nonce.py --selftest.
2. Collect the two records under one nonce; extract ciphertext hex and tag hex.
3. python3 tools/gcm_nonce.py --ct1 <h> --tag1 <h> --ct2 <h> --tag2 <h> [--aad1 --aad2].
4. Try each returned H: python3 tools/gcm_nonce.py --h <H> --ct <chosen-ct> --new-ct <new-ct>.
5. Submit the forged pair; an accepted tag is impact evidence.

## Falsifier

Falsifier — no nonce reuse in the captures, or the algebra produces no valid H: the pair was under different nonces or different keys.

## Traps

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
