# Signed-token boundary — JWT, itsdangerous, Django — checklist

Signed tokens live at this class's boundary: the 'MAC' is HS256, but the
attack is usually algorithm confusion or a weak secret — not an oracle loop.

## Checklist

- [ ] **alg confusion**: RS256 public key used as HS256 secret. Try once.
- [ ] **weak secret**: `hashcat -m 16500` / wordlist the HS256 key — a cracking

## Falsifier

Stop when the module's abort conditions fire — recorded as a negative, not retried as a variant.
