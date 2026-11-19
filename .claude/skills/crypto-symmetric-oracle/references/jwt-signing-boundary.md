# Signed-token boundary — JWT, itsdangerous, Django

Signed tokens live at this class's boundary: the 'MAC' is HS256, but the
attack is usually algorithm confusion or a weak secret — not an oracle loop.

## Triage

| Token shape | Construction | Route |
|---|---|---|
| `header.payload.sig` JWT | HS256/RS256 | alg confusion or weak secret |
| `a.b.c` with itsdangerous style | salted HMAC | secret leak → resign |
| `session=` Django cookie | sha1/sha256 HMAC | SECRET_KEY leak → resign |
| Encrypted JWT (JWE) | AES-GCM-wrapped | authenticated boundary |

## The real attacks (outside this class)

- **alg confusion**: RS256 public key used as HS256 secret. Try once.
- **weak secret**: `hashcat -m 16500` / wordlist the HS256 key — a cracking
  problem, not an oracle.
- **none alg**: strip the signature block; a sloppy verifier accepts.
- **SECRET_KEY leak**: any source disclosure → resign locally.

## When it IS this class

- A custom `mac = sha256(secret || payload)` (not HMAC): `length-extension.md`.
- A truncated or compare-timed verify endpoint: `verify-oracle.md`.

## Falsifier

The token uses real HMAC with a strong secret and verifies full-length in
constant time: closed — the flag isn't behind the token's crypto.
