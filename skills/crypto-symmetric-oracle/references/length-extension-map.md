# Length extension — hash(secret||msg) forgery — signal map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| MAC = raw SHA-1/SHA-256/MD5 of secret||data | length-extension applies | tools/crypto_attack.py length-extension |
| You know the message and the secret LENGTH (or can brute a small range) | extension possible | forge digest |
| MAC = HMAC (keyed envelope) | NOT vulnerable | reclassify — see mac-forgery |
| Sponge hash: SHA-3, Keccak, BLAKE2 | NOT vulnerable | reclassify |

## Falsifier

Falsifier — the forged MAC is rejected under every secret length tried: the MAC is HMAC, a keyed PRF, or a sponge hash, or the server appends after your data (suffix MACs don't extend forward).
