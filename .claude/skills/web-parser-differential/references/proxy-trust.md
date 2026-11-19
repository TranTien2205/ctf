# Proxy trust — the proxy-added-header trust model, exhaustively

The proxy-trust model — what the app trusts the proxy to set.

---

## 1. The model — a proxy that adds a trusted header

```text
a reverse proxy sits in front of the app — it adds a header the app
trusts — an X-Real-IP, an X-Forwarded-For, an X-Internal, an
X-Admin — the app uses it to decide whether the request is local,
authenticated, or privileged.
```

## 2. The trust check — the app's input

```text
the app's trust check reads the proxy's header — a missing header
hits a fallback — a present header is trusted — the app doesn't
verify the proxy actually added it.
```

## 3. The trust-check's fallback — the missing-header case

```text
a missing proxy header → the app treats the request as local or
skips the trust check → a local request bypasses the authentication
or the restriction.
```

## 4. The proxy-header abuse — a client-supplied header

```bash
# a client-supplied proxy header — the app trusts it
curl "$BASE/api/restricted" -H 'X-Real-IP: 127.0.0.1'   # a client-supplied X-Real-IP
#   the app trusts the header → a local request → the trust check bypassed
```

```text
a client-supplied proxy header — the app doesn't verify the proxy
added it — a client-supplied header IS trusted.
```

## 5. The hop-by-hop bypass — the proxy strips its own header

```bash
# naming the proxy's own header in Connection — the proxy strips it
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Real-IP'
#   the proxy strips X-Real-IP → the app sees a request without it → a
#   missing-header fallback → a local request → the trust check bypassed
```

## 6. The proxy-trust's vectors — which headers the app trusts

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
```

## 7. The proxy-trust's scope — which routes are reachable

```text
the trust check gates a route — an authenticated-only route, an
internal route, a restricted endpoint — the app's trust check reads
the missing or client-supplied header's effect.
```

## 8. The proxy-trust's check — the client-supplied header

```bash
# the client-supplied check — does the app trust a client-supplied header
curl "$BASE/api/restricted" -H 'X-Real-IP: 127.0.0.1'   # a client-supplied X-Real-IP
#   a 200 → the app trusts the client-supplied header → the check's input
```

## 9. The proxy-trust's falsifier — a proxy that strips a client header

```text
a proxy that strips a client-supplied proxy header → the client-
supplied header doesn't reach the app → the client-supplied bypass
fails → the hop-by-hop bypass is the remaining vector.
```

## 10. The proxy-trust's falsifier — a verified header

```text
a proxy that verifies the header it added → a client-supplied header
is rejected → the client-supplied bypass fails → the hop-by-hop
bypass is the remaining vector.
```

## 11. The proxy-trust's falsifier — a non-header check

```text
the card's falsifier: 'both forms are rejected, so the trust check
does not depend on that header' — the header isn't the trust check's
input → a different class.
```

## 12. The proxy-trust's per-stack map — which proxies add which header

```text
nginx     → X-Real-IP, X-Forwarded-For, X-Forwarded-Host, X-Forwarded-Proto
Traefik   → X-Real-IP, X-Forwarded-For, X-Forwarded-Host, X-Forwarded-Proto
Apache    → X-Forwarded-For, X-Forwarded-Host, X-Forwarded-Proto
HAProxy   → X-Forwarded-For, X-Forwarded-Host, X-Forwarded-Proto
Cloudflare→ CF-Connecting-IP, CF-Ray, CF-Visitor
Akamai    → True-Client-IP, Akamai-Origin-Hop
```
