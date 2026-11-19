# Detection surface — where the parser-differential surface lives, exhaustively

The complete map of where the proxy-trust surface lives.

---

## 1. The proxy — the front-end layer

```bash
# the proxy's headers — a proxy in the path
curl -sI "$BASE/" | grep -iE 'x-forwarded|x-real|via:|x-served|server|x-backend|x-upstream|cf-|x-varnish|traefik'
#   a Via / an X-Forwarded-* / a Server header → a proxy in the path
```

## 2. The trust check — the app's proxy-header input

```bash
# the app's proxy-header input — a header the app reads
grep -rnoiE 'X-Real-IP|X-Forwarded|X-Internal|X-Admin|X-Original|X-Rewrite|client_ip|remote_addr|request.headers|request\.META|request\.env|header' <src> | head -20
```

## 3. The missing-header fallback — the local-request check

```bash
# the missing-header fallback — the app's local-request check
grep -rnoiE '127.0.0.1|localhost|local|internal|trust|fallback|missing|getattr|header\.get|request.headers.get|remote_addr|is_local' <src> | head -15
```

## 4. The gated route — the restricted endpoint

```bash
# the gated route — an authenticated-only, an internal, a restricted
grep -rnoiE 'restricted|internal|admin|auth|token_required|required|login_required|@auth|@admin|private|api|debug|preview' <src> | head -15
```

## 5. The hop-by-hop surface — the Connection-strip

```bash
# the proxy's strip — a Connection-header control
grep -rnoiE 'Connection|hop-by-hop|strip|header|proxy' <src> | head -10
```

## 6. The normalization surface — a path difference

```bash
# the normalization boundary — a path the proxy and the app normalize differently
grep -rnoiE 'normalize|redirect|rewrite|path|decode|urldecode|canonical|route|parse' <src> | head -10
```

## 7. The client-supplied surface — a forged header

```bash
# the app's trust — a header the app reads without verification
grep -rnoiE 'request.headers|request\.META|request\.env|header\.get|getattr' <src> | head -10
```

## 8. The per-surface signal map — which signals name which surface

```text
a 'Via|X-Forwarded|X-Real|x-served'      → a proxy in the path
a 'X-Real-IP|X-Forwarded|X-Internal'      → a proxy-header surface
a '127.0.0.1|localhost|local|internal'    → a missing-header fallback
a 'restricted|internal|admin|auth'        → a gated route
a 'normalize|redirect|rewrite|path'       → a normalization boundary
a 'proxy_pass|proxy_set_header'           → an nginx proxy
a 'traefik'                               → a Traefik proxy
```

## 9. The per-proxy header-map — which headers each proxy adds

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

## 10. The per-vector check — which vector for which surface

```bash
# the local-vs-remote check — a spoofed-IP header
curl "$BASE/api/admin" -H 'X-Real-IP: 127.0.0.1'
# the internal-route check — a spoofed-internal header
curl "$BASE/internal" -H 'X-Internal: true'
# the admin check — a spoofed-admin header
curl "$BASE/admin" -H 'X-Admin: true'
# the host check — a spoofed-host header
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'
# the hop-by-hop check — a Connection-strip
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Real-IP'
```

## 11. The detection's falsifier — when the surface is dead

```text
the card's falsifier: 'both forms are rejected, so the trust check
does not depend on that header' — the header isn't the trust check's
input → a different class.
```
