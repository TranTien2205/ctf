# GCM nonce reuse — the forbidden attack — case catalogue

GCM reusing a nonce leaks the GHASH authentication subkey H: two tagged ciphertexts under one nonce let you forge tags for arbitrary new ciphertexts. tools/gcm_nonce.py runs the algebra.

## Cases

| # | Shape | Distinguisher | Attack |
|---|---|---|---|
| 1 | Two records, same nonce, same key, different AAD/CT | H recoverable | tools/gcm_nonce.py |
| 2 | You can submit (ct, tag) pairs for verification | forgery oracle available | forge after H recovered |
| 3 | 96-bit nonce built from a counter that wraps or a fixed field | reuse inevitable | collect the pair |

## Falsifier

Falsifier — no nonce ever repeats (checked across all captured records) or the tag check precedes every decrypt attempt uniformly: the forbidden attack has no input. Reclassify toward tag truncation or a different class.

## Coverage notes

- The recovered H is one of a few algebraic candidates — test each against a third record.
- AAD differences change the tag equation; include --aad1/--aad2 whenever present.
- Nonce reuse also XORs the CTR keystream — the plaintext recovery part is crib-drag territory (ctr-nonce-reuse.md).

## Cross-references

`tools-gcm-nonce.md` · `ctr-nonce-reuse.md` · `mac-forgery.md`
