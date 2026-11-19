# Signed-token boundary — JWT, itsdangerous, Django — map

| Token shape | Construction | Route |
|---|---|---|
| `header.payload.sig` JWT | HS256/RS256 | alg confusion or weak secret |
| `a.b.c` with itsdangerous style | salted HMAC | secret leak → resign |
| `session=` Django cookie | sha1/sha256 HMAC | SECRET_KEY leak → resign |
| Encrypted JWT (JWE) | AES-GCM-wrapped | authenticated boundary |

Expanded rows and abort conditions: `jwt-signing-boundary.md` and `jwt-signing-boundary-deep.md`.
