# Real-world cases — where parser differentials appear in actual challenges

The named shapes with the mechanics that identify them.

---

## 1. The hop-by-hop bypass — the proxy-strips-its-own-header shape

```text
a Traefik/nginx/Apache proxy adds a trusted header — naming it in
Connection strips it → the app treats a missing-header request as
local → the trust check bypassed. the verified card's shape — the
most common CTF parser-differential.
```

## 2. The client-supplied-header abuse — a forged proxy header

```text
an app that trusts a proxy header — a client-supplied header IS
trusted — a forged local IP → a local request → the trust check
bypassed — a client-supplied proxy-header surface.
```

## 3. The forwarded-host rewrite — a URL-rewrite surface

```text
an app that builds absolute URLs from X-Forwarded-Host — a client-
supplied X-Forwarded-Host rewrites the app's links — a URL-rewrite
surface — the app's links/scripts point to attacker.com.
```

## 4. The forwarded-scheme downgrade — a scheme-confusion surface

```text
an app that builds absolute URLs from X-Forwarded-Scheme — a client-
supplied X-Forwarded-Scheme downgrades the app's links — the links
use http — a scheme-confusion surface.
```

## 5. The X-Original-URL rewrite — a path-rewrite surface

```text
an app that honors X-Original-URL — a client-supplied X-Original-URL
rewrites the path — the app serves a different route — a path-rewrite
surface.
```

## 6. The internal-flag bypass — a forged internal flag

```text
an app that checks X-Internal for an internal-route check — a client-
supplied X-Internal: true → the check passes → an internal route
reached — a flag bypass.
```

## 7. The admin-flag bypass — a forged admin flag

```text
an app that checks X-Admin for an admin check — a client-supplied
X-Admin: true → the check passes → an admin route reached — a flag
bypass.
```

## 8. The forwarded-for spoof — a forged client IP

```text
an app that reads X-Forwarded-For for a local-vs-remote check — a
client-supplied X-Forwarded-For: 127.0.0.1 → a local request → the
trust check bypassed.
```

## 9. The path-normalization bypass — a route-confusion surface

```text
a path the proxy and the app normalize differently — a /static/../admin
the proxy normalizes to /admin and the app routes to /admin — a
normalization differential — the front-end's check reads a different
path than the app's.
```

## 10. The internal-route bypass — a missing-header fallback

```text
an app that checks a proxy header for an internal-route check — a
stripped header (the hop-by-hop bypass) → a missing-header fallback
→ a local request → the internal route reached.
```

## 11. The authenticated-route bypass — a token_required bypass

```text
an app that checks a proxy header for a token_required check — a
stripped header → a missing-header fallback → a local request → the
authenticated route reached — the verified card's shape.
```

## 12. The method-override bypass — a forged method

```text
an app that honors X-HTTP-Method-Override — a client-supplied override
changes the method — a POST-as-GET or a DELETE-as-POST — a method-
override surface.
```

## 13. The multi-proxy differential — a chained normalization

```text
a multi-proxy chain — an edge + an origin proxy — a header each
strips differently — a chained normalization boundary — a per-layer
differential.
```

## 14. The Forwarded header — an RFC 7239 spoof

```text
an app that reads the RFC 7239 Forwarded header — a client-supplied
Forwarded: for=127.0.0.1 → a local request → the trust check bypassed.
```

## 15. The per-case vector-selection — which vector for which surface

```text
a local-vs-remote check     → a spoofed-IP header (X-Real-IP, X-Forwarded-For)
an internal-route check     → a spoofed-internal header (X-Internal)
an admin check              → a spoofed-admin header (X-Admin)
a host check                → a spoofed-host header (X-Forwarded-Host, X-Host)
a scheme check              → a spoofed-scheme header (X-Forwarded-Scheme)
a path check                → a spoofed-path header (X-Original-URL, X-Rewrite-URL)
a method check              → a spoofed-method header (X-HTTP-Method-Override)
a multi-proxy chain         → a chained normalization (a per-layer differential)
```
