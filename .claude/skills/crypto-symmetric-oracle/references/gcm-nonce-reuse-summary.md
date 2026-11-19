# GCM nonce reuse — the forbidden attack — summary

GCM reusing a nonce leaks the GHASH authentication subkey H: two tagged ciphertexts under one nonce let you forge tags for arbitrary new ciphertexts. tools/gcm_nonce.py runs the algebra.

## Signal → route

- Two records, same nonce, same key, different AAD/CT → tools/gcm_nonce.py
- You can submit (ct, tag) pairs for verification → forge after H recovered
- 96-bit nonce built from a counter that wraps or a fixed field → collect the pair

## Falsifier

Falsifier — no nonce ever repeats (checked across all captured records) or the tag check precedes every decrypt attempt uniformly: the forbidden attack has no input. Reclassify toward tag truncation or a different class.
