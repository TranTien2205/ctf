# Length extension — hash(secret||msg) forgery — summary

A MAC built as sha1/sha256/md5 of secret||message is forgeable: the hash's internal state after the message is the digest itself — continue it with your appended data.

## Signal → route

- MAC = raw SHA-1/SHA-256/MD5 of secret||data → tools/crypto_attack.py length-extension
- You know the message and the secret LENGTH (or can brute a small range) → forge digest
- MAC = HMAC (keyed envelope) → reclassify — see mac-forgery
- Sponge hash: SHA-3, Keccak, BLAKE2 → reclassify

## Falsifier

Falsifier — the forged MAC is rejected under every secret length tried: the MAC is HMAC, a keyed PRF, or a sponge hash, or the server appends after your data (suffix MACs don't extend forward).
