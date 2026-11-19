# GCM nonce reuse — the forbidden attack — playbook

GCM reusing a nonce leaks the GHASH authentication subkey H: two tagged ciphertexts under one nonce let you forge tags for arbitrary new ciphertexts. tools/gcm_nonce.py runs the algebra.

## Ordered playbook

1. Collect (ct1, tag1) and (ct2, tag2) under the same nonce; AAD if any.
2. python3 tools/gcm_nonce.py --ct1 <h> --tag1 <h> --ct2 <h> --tag2 <h> --aad1 <h> --aad2 <h> — recovers the GHASH key candidates.
3. With H: python3 tools/gcm_nonce.py --ct <new-ct> --tag '' --h <H> --new-ct <h> forges a valid tag for your chosen ciphertext.
4. Submit the forged pair; a valid-tag answer confirms recovery (post it via post-probe).
5. The flag is usually inside the service's decryptable region once forgery succeeds.

## Falsifier

Falsifier — no nonce ever repeats (checked across all captured records) or the tag check precedes every decrypt attempt uniformly: the forbidden attack has no input. Reclassify toward tag truncation or a different class.

## Commands

```bash
python3 tools/gcm_nonce.py --ct1 <h> --tag1 <h> --ct2 <h> --tag2 <h>
python3 tools/gcm_nonce.py --selftest
```
