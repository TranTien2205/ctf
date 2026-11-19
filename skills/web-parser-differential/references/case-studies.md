# Case studies — the named parser-differential shapes

The named shapes with the mechanics that identify them.

---

## 1. The hop-by-hop bypass — the verified card's shape

```text
a Traefik proxy adds X-Real-IP — the app checks it for an
authenticated-only route — naming X-Real-IP in Connection strips it
→ the app treats the request as local → the token_required check
skipped → a restricted route reached.
the card's probe: send the same authenticated-only request twice —
once normally, once with the proxy header named in Connection.
```

## 2. The client-supplied header — a forged local IP

```text
an app that trusts a proxy header (X-Real-IP, X-Forwarded-For) for a
local-vs-remote check — a client-supplied header IS trusted — a
forged local IP → a local request → the trust check bypassed.
the probe: a client-supplied header → a 200 on the gated route.
```

## 3. The forwarded-host rewrite — a URL-rewrite

```text
an app that builds absolute URLs from X-Forwarded-Host — a client-
supplied X-Forwarded-Host rewrites the app's links — a URL-rewrite
surface — the app's links/scripts point to attacker.com.
the probe: X-Forwarded-Host: attacker.com → the links point to it.
```

## 4. The forwarded-scheme downgrade — a scheme confusion

```text
an app that builds absolute URLs from X-Forwarded-Scheme — a client-
supplied X-Forwarded-Scheme downgrades the app's links — the links
use http — a scheme confusion surface.
the probe: X-Forwarded-Scheme: http → the links use http.
```

## 5. The X-Original-URL rewrite — a path-rewrite

```text
an app that honors X-Original-URL — a client-supplied X-Original-URL
rewrites the path — the app serves a different route — a path-rewrite
surface.
the probe: X-Original-URL: /admin → the app serves /admin under /page.
```

## 6. The internal-flag bypass — a forged internal flag

```text
an app that checks X-Internal for an internal-route check — a client-
supplied X-Internal: true → the check passes → an internal route
reached — a flag bypass.
the probe: X-Internal: true → a 200 on the internal route.
```

## 7. The admin-flag bypass — a forged admin flag

```text
an app that checks X-Admin for an admin check — a client-supplied
X-Admin: true → the check passes → an admin route reached — a flag
bypass.
the probe: X-Admin: true → a 200 on the admin route.
```

## 8. The path-normalization bypass — a route confusion

```text
a path the proxy and the app normalize differently — a /static/../admin
the proxy normalizes to /admin and the app routes to /admin — a
normalization differential — the front-end's check reads a different
path than the app's.
the probe: /static/../admin → the app serves /admin.
```

## 9. The forwarded-for spoof — a forged client IP

```text
an app that reads X-Forwarded-For for a local-vs-remote check — a
client-supplied X-Forwarded-For: 127.0.0.1 → a local request → the
trust check bypassed.
the probe: X-Forwarded-For: 127.0.0.1 → a 200 on the gated route.
```

## 10. The forwarded-proto downgrade — a proto confusion

```text
an app that builds absolute URLs from X-Forwarded-Proto — a client-
supplied X-Forwarded-Proto downgrades the app's links — the links
use http — a proto confusion surface.
the probe: X-Forwarded-Proto: http → the links use http.
```

## 11. The internal-route bypass — a missing-header fallback

```text
an app that checks a proxy header for an internal-route check — a
stripped header (the hop-by-hop bypass) → a missing-header fallback
→ a local request → the internal route reached.
the probe: Connection: keep-alive, X-Internal → a 200 on the internal
route.
```

## 12. The authenticated-route bypass — a token_required bypass

```text
an app that checks a proxy header for a token_required check — a
stripped header → a missing-header fallback → a local request → the
authenticated route reached — the verified card's shape.
the probe: Connection: keep-alive, X-Real-IP → a 200 on the token route.
```

## 13. The method-override bypass — a forged method

```text
an app that honors X-HTTP-Method-Override — a client-supplied override
changes the method — a POST-as-GET or a DELETE-as-POST — a method-
override surface.
the probe: X-HTTP-Method-Override: DELETE → the app treats it as DELETE.
```

## 14. The multi-proxy differential — a chained normalization

```text
a multi-proxy chain — an edge + an origin proxy — a header each
strips differently — a chained normalization boundary — a per-layer
differential.
the probe: a header the edge strips but the origin doesn't — a
chained differential.
```

## 15. The Forwarded header — an RFC 7239 spoof

```text
an app that reads the RFC 7239 Forwarded header — a client-supplied
Forwarded: for=127.0.0.1 → a local request → the trust check bypassed.
the probe: Forwarded: for=127.0.0.1 → a 200 on the gated route.
```
