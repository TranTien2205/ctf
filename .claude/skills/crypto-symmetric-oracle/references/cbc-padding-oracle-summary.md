# CBC padding oracle — Vaudenay decryption — summary

A service that answers 'padding valid' vs 'padding invalid' decrypts arbitrary ciphertext for you, one byte per ~256 requests. The error channel IS the exploit.

## Signal → route

- Corrupt ciphertext yields two distinct error responses → drive pad_oracle loop
- Same ciphertext replayed gives same validity answer → full decryption feasible
- All tampering returns one generic error → reclassify

## Falsifier

Falsifier — every corruption returns byte-identical responses (status, body, AND timing within noise): no oracle exists. An HMAC checked before decryption produces exactly this signature.
