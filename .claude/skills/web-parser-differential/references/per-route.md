# Per-route — every gated route, exhaustively

The route map — a header the app reads, a route the header gates.

---

## 1. The authenticated-only route — a token_required check

```bash
# an authenticated-only route — a token_required check
curl "$BASE/api/copy_signal_trade" -d 'data'   # a 401 — token required
curl "$BASE/api/copy_signal_trade" -d 'data' -H 'Connection: keep-alive, X-Real-IP'   # a 200 — the strip worked
curl "$BASE/api/active_signals" -d 'data'   # a 401 — token required
curl "$BASE/api/active_signals" -d 'data' -H 'Connection: keep-alive, X-Real-IP'   # a 200 — the strip worked
curl "$BASE/api/user" -d 'data'   # a 401 — token required
curl "$BASE/api/user" -d 'data' -H 'Connection: keep-alive, X-Real-IP'   # a 200 — the strip worked
```

## 2. The internal route — an internal check

```bash
# an internal route — an internal check
curl "$BASE/internal"   # a 403 — internal check
curl "$BASE/internal" -H 'X-Internal: true'   # a 200 — the check bypassed
curl "$BASE/internal" -H 'Connection: keep-alive, X-Internal'   # the strip
curl "$BASE/internal" -H 'Connection: keep-alive, X-Real-IP'   # the strip
```

## 3. The admin route — an admin check

```bash
# an admin route — an admin check
curl "$BASE/admin"   # a 403 — admin check
curl "$BASE/admin" -H 'X-Admin: true'   # a 200 — the check bypassed
curl "$BASE/admin" -H 'Connection: keep-alive, X-Admin'   # the strip
curl "$BASE/admin" -H 'Connection: keep-alive, X-Real-IP'   # the strip
```

## 4. The debug route — a debug check

```bash
# a debug route — a debug check
curl "$BASE/api/debug"   # a 403 — debug check
curl "$BASE/api/debug" -H 'X-Debug: true'   # a 200 — the check bypassed
curl "$BASE/api/debug" -H 'Connection: keep-alive, X-Debug'   # the strip
curl "$BASE/api/debug" -H 'Connection: keep-alive, X-Real-IP'   # the strip
```

## 5. The restricted route — a restricted check

```bash
# a restricted route — a restricted check
curl "$BASE/api/restricted"   # a 403 — restricted check
curl "$BASE/api/restricted" -H 'X-Internal: true'   # a 200 — the check bypassed
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Real-IP'   # the strip
```

## 6. The private route — a private check

```bash
# a private route — a private check
curl "$BASE/private"   # a 403 — private check
curl "$BASE/private" -H 'X-Internal: true'   # a 200 — the check bypassed
curl "$BASE/private" -H 'Connection: keep-alive, X-Real-IP'   # the strip
```

## 7. The preview route — a preview check

```bash
# a preview route — a preview check
curl "$BASE/preview"   # a 403 — preview check
curl "$BASE/preview" -H 'X-Internal: true'   # a 200 — the check bypassed
curl "$BASE/preview" -H 'Connection: keep-alive, X-Real-IP'   # the strip
```

## 8. The api route — an api check

```bash
# an api route — an api check
curl "$BASE/api"   # a 403 — api check
curl "$BASE/api" -H 'X-Internal: true'   # a 200 — the check bypassed
curl "$BASE/api" -H 'Connection: keep-alive, X-Real-IP'   # the strip
```

## 9. The auth route — an auth check

```bash
# an auth route — an auth check
curl "$BASE/auth"   # a 403 — auth check
curl "$BASE/auth" -H 'X-Internal: true'   # a 200 — the check bypassed
curl "$BASE/auth" -H 'Connection: keep-alive, X-Real-IP'   # the strip
```

## 10. The user route — a user check

```bash
# a user route — a user check
curl "$BASE/user"   # a 403 — user check
curl "$BASE/user" -H 'X-Forwarded-User: admin'   # a 200 — the check bypassed
curl "$BASE/user" -H 'Connection: keep-alive, X-Forwarded-User'   # the strip
```

## 11. The admin-only route — an admin check

```bash
# an admin-only route — an admin check
curl "$BASE/api/admin"   # a 403 — admin check
curl "$BASE/api/admin" -H 'X-Admin: true'   # a 200 — the check bypassed
curl "$BASE/api/admin" -H 'Connection: keep-alive, X-Admin'   # the strip
```

## 12. The internal-only route — an internal check

```bash
# an internal-only route — an internal check
curl "$BASE/api/internal"   # a 403 — internal check
curl "$BASE/api/internal" -H 'X-Internal: true'   # a 200 — the check bypassed
curl "$BASE/api/internal" -H 'Connection: keep-alive, X-Internal'   # the strip
```

## 13. The multi-route check — a chained differential

```bash
# a multi-route check — a chained differential
curl "$BASE/api/admin" -H 'X-Real-IP: 127.0.0.1' -H 'X-Admin: true'   # a local + an admin
curl "$BASE/api/internal" -H 'X-Real-IP: 127.0.0.1' -H 'X-Internal: true'   # a local + an internal
curl "$BASE/api/user" -H 'X-Real-IP: 127.0.0.1' -H 'X-Forwarded-User: admin'   # a local + a user
curl "$BASE/api/debug" -H 'X-Real-IP: 127.0.0.1' -H 'X-Debug: true'   # a local + a debug
```

## 14. The per-route signal map — which signals name which route

```text
a 'token_required|@login_required|@auth'      → an authenticated-only route
a 'internal|private|restricted'                → an internal route
a 'admin|@admin'                               → an admin route
a 'debug|preview'                              → a debug route
a 'api|user'                                   → an api route
a 'X-Real-IP|X-Forwarded|X-Internal|X-Admin'   → a proxy-header surface
a '127.0.0.1|localhost|local|internal'         → a missing-header fallback
a 'normalize|redirect|rewrite|path'            → a normalization boundary
```

## 15. The per-route falsifier — when the route is dead

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
