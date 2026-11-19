# tools/gcm_nonce.py — the forbidden attack driver — case catalogue

Recovers the GHASH subkey H from two nonce-reused records, then forges a tag for a chosen new ciphertext. Algebraic, deterministic — no oracle loop.

## Cases

| # | Shape | Distinguisher | Attack |
|---|---|---|---|
| 1 | --ct1 --tag1 --ct2 --tag2 = the reused pair | input pair | must share a nonce |
| 2 | --aad1 --aad2 when AAD differs | auth-data included | omitting it changes the algebra |
| 3 | --h + --ct/--new-ct = forgery mode | H to forged tag | test each H candidate |
| 4 | --selftest proves the algebra | local check | run first |

## Falsifier

Falsifier — no nonce reuse in the captures, or the algebra produces no valid H: the pair was under different nonces or different keys.

## Coverage notes

- AAD changes the tag equation — always pass --aad1/--aad2 when present, even if identical.
- Multiple H candidates are normal — try each.
- Nonce reuse also lets you crib-drag the CTR stream: the same pair feeds tools/crypto_attack.py crib-drag too.

## Cross-references

`gcm-nonce-reuse.md` · `ctr-nonce-reuse.md`
