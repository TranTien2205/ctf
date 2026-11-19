# Detection — finding the parser-differential surface

The signals that name the class — and the first probe.

---

## 1. The proxy signals — a reverse proxy in the path

```bash
# the proxy's headers — a proxy in the path
curl -sI "$BASE/" | grep -iE 'x-forwarded|x-real|via:|x-served|server|x-backend|x-upstream|cf-|x-varnish'
#   a Via / an X-Forwarded-* / a Server header → a proxy in the path
```

## 2. The trust-check signals — the app's proxy-header input

```bash
# the app's proxy-header input — a header the app reads
grep -rnoiE 'X-Real-IP|X-Forwarded|X-Internal|X-Admin|X-Original|X-Rewrite|client_ip|remote_addr|request.headers|request\.META|request\.env|header' <src> | head -20
```

## 3. The trust-check's fallback — the missing-header case

```bash
# the missing-header fallback — the app's local-request check
grep -rnoiE '127.0.0.1|localhost|local|internal|trust|fallback|missing|getattr|header\.get|request.headers.get' <src> | head -15
```

## 4. The hop-by-hop probe — the Connection-header bypass

```bash
# the two-request check — does the proxy strip its own header
curl "$BASE/api/restricted"   # the normal request
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Real-IP'   # the proxy strips X-Real-IP
#   the second request reaches the app without X-Real-IP → a 200 vs a 401
```

## 5. The client-supplied probe — a client-supplied proxy header

```bash
# the client-supplied check — does the app trust a client-supplied header
curl "$BASE/api/restricted" -H 'X-Real-IP: 127.0.0.1'   # a client-supplied X-Real-IP
#   a 200 → the app trusts the client-supplied header → the check's input
```

## 6. The restricted-route signals — the gated route

```bash
# the gated route — an authenticated-only, an internal, a restricted
grep -rnoiE 'restricted|internal|admin|auth|token_required|required|login_required|@auth|@admin|private|api' <src> | head -15
```

## 7. The proxy-header signals — which headers the proxy adds

```text
X-Real-IP          → the client IP
X-Forwarded-For    → the client IP
X-Forwarded-Host   → the app's host
X-Forwarded-Scheme → the app's scheme
X-Forwarded-Proto  → the app's proto
X-Internal         → an internal flag
X-Admin            → an admin flag
X-Original-URL     → a rewritten path
X-Rewrite-URL      → a rewritten path
```

## 8. The parser signals — a front-end/back-end parse difference

```bash
# the parser difference — a front-end and a back-end parse differently
grep -rnoiE 'normalize|redirect|rewrite|path|decode|urldecode|canonical|route|parse' <src> | head -10
```

## 9. The per-surface signal map — which signals name which surface

```text
a 'Via|X-Forwarded|X-Real|x-served'      → a proxy in the path
a 'X-Real-IP|X-Forwarded|X-Internal'      → a proxy-header surface
a '127.0.0.1|localhost|local|internal'    → a missing-header fallback
a 'restricted|internal|admin|auth'        → a gated route
a 'normalize|redirect|rewrite|path'       → a normalization boundary
```

## 10. The detection's falsifier — when the surface is dead

```text
the card's falsifier: 'both forms are rejected, so the trust check
does not depend on that header' — the header isn't the trust check's
input → a different class.
```
