# Oracle shapes — the four you can hold — summary

An oracle is any endpoint that answers a question about a ciphertext, a plaintext, or a tag. Before any exploit loop, name exactly which one you hold — encrypt, decrypt, padding-check, or verify — because the attack inventory differs completely per shape.

## Signal → route

- You submit bytes, service returns ciphertext → alignment and mode fingerprinting first
- Service decrypts and returns plaintext or a decode error → usually trivial — request the flag's decryption
- Service decrypts and only reports validity → padding-oracle decryption loop
- Service checks a tag you submit → tag-forgery or length-extension test
- You see ciphertext AND a tag AND a nonce → nonce reuse or tag-truncation, not padding

## Falsifier

Falsifier — the service authenticates before decrypting (GCM tag, or HMAC verified first). A tampered ciphertext is rejected identically for every corruption; no oracle exists to query. Reclassify toward nonce reuse or key-material leaks instead.
