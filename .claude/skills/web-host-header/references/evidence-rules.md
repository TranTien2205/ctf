# Evidence rules — the host-header proof standard

The evidence discipline — a reflected host is a lead, not a finding.

---

## 1. The lead — a reflected host

```text
a reflected host in the response is only a lead — the finding needs
the host reaching a decision — a link the victim clicks, a path the
middleware applies, a domain a cookie binds to.
```

## 2. The finding — a host reaching a decision

```text
a host reaching a decision — a link the victim clicks (a reset link,
a canonical URL, a Location redirect) — a path the middleware applies
(an ACL bypass, a route-confusion) — a domain a cookie binds to (a
session fixation surface) — a cache key the cache stores (a cache-
poisoning feed).
```

## 3. The canonical-URL evidence — the app's links rewritten

```bash
# the canonical-URL evidence — the app's links rewritten
curl -s -D - -H 'Host: canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
#   the canonical URLs point to canary.example → a stored injection
curl -s -H 'Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
#   the page's links/scripts point to canary.example → a stored injection
```

## 4. The reset-link evidence — the reset link rewritten

```bash
# the reset-link evidence — the reset link rewritten
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
#   the reset link points to canary.example → an account takeover
```

## 5. The Location evidence — the redirect rewritten

```bash
# the Location evidence — the redirect rewritten
curl -s -D - -H 'Host: canary.example' "$BASE/redirect" | grep -i 'location'
#   the Location points to canary.example → an open redirect
```

## 6. The Set-Cookie evidence — the cookie domain rewritten

```bash
# the Set-Cookie evidence — the cookie domain rewritten
curl -s -D - -H 'Host: canary.example' "$BASE/login" | grep -i 'set-cookie'
#   the Set-Cookie domain binds to canary.example → a session fixation
```

## 7. The cache-key evidence — the cache key poisoned

```bash
# the cache-key evidence — the cache key poisoned
curl -s -D - -H 'Host: canary.example' "$BASE/page" | grep -i 'x-cache\|x-served\|age'
#   the cache stores the page under canary.example → a cache-poisoning feed
```

## 8. The rewrite evidence — the middleware rewrite

```bash
# the rewrite evidence — the middleware rewrite
curl -i "$BASE/admin"                        # expect 403
curl -i -H 'X-Original-URL: /admin' "$BASE/" # 200 with the admin body = finding
#   a 200 on the gated route → the middleware rewrites the path → an ACL bypass
```

## 9. The forwarded evidence — the forwarded header

```bash
# the forwarded evidence — the forwarded header
curl -s -H 'Forwarded: host=canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
#   the page's links point to canary.example → a stored injection
```

## 10. The duplicated Host evidence — the parsing differential

```bash
# the duplicated Host evidence — the parsing differential
curl -s -D - -H 'Host: good.example' -H 'Host: evil.example' "$BASE/"
#   the proxy reads the first; the app reads the second → a differential
curl -s -D - -H 'Host: evil.example' -H 'Host: good.example' "$BASE/"
#   the proxy reads the first; the app reads the second → a differential
```

## 11. The malformed Host evidence — the parsing edge

```bash
# the malformed Host evidence — the parsing edge
curl -s -D - -H 'Host: evil.example:80' "$BASE/"   # a forged port
curl -s -D - -H 'Host: evil.example.' "$BASE/"   # a trailing dot
curl -s -D - -H 'Host: evil.example..target.com' "$BASE/"   # a double-dot
curl -s -D - -H 'Host: ' "$BASE/"   # an empty host
curl -s -D - -H 'Host: evil.example@target.com' "$BASE/"   # an @-separator
```

## 12. The absolute-URI evidence — the request-line differential

```bash
# the absolute-URI evidence — the request-line differential
curl -s -D - "$BASE/" --request-target 'http://evil.example/'   # an absolute-URI
curl -s -D - "http://evil.example/" --resolve 'evil.example:443:127.0.0.1'   # an absolute-URI
```

## 13. The evidence's falsifier — when the surface is dead

```text
a proxy that validates the Host against a server list → a 400 on a bad
host → a negative result, not a retry signal.
a proxy that strips the client-supplied forwarded header → the header
doesn't reach the app → the bypass fails → a different class.
a proxy that verifies the forwarded header it added → a client-supplied
header is rejected → the bypass fails → a different class.
a trust check that reads a different input → a different class.
```

## 14. The evidence's budget — the probe limits

```text
5 probes or 15 minutes per mechanism class; 25 probes or 45 minutes
for the challenge. a spent budget → escalate: chain_match → reclassify
→ writeup_search → novel_plan → fanout_sweep → solver_handoff.
```
