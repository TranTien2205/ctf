# CTR / stream nonce reuse — keystream recovery — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| Two ciphertexts share a nonce/IV/counter | keystream reused | crib-drag |
| Fixed IV in source, or nonce = message counter that wraps | reuse guaranteed | collect pairs |
| Known plaintext anywhere in one message | keystream segment recovered directly | XOR onto the other ciphertext |

## Falsifier

Falsifier — every pair uses a distinct nonce and no known plaintext exists: no two-message keystream is ever produced. Reclassify toward PRNG weaknesses in the keystream source instead.
