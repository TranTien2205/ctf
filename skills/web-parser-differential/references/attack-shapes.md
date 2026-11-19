# Attack shapes — the named parser-differential attacks, end to end

The named attacks — each with its setup, mechanism, probe, and falsifier.

---

## Attack 1 — the hop-by-hop bypass

```text
setup:   a proxy adds a trusted header — naming it in Connection strips it
mechanism: the app sees a request without the trusted header — a
         missing-header fallback → a local request → the trust check bypassed
probe:   a normal request (a 401) then a stripped request (a 200)
falsifier: the proxy doesn't strip its own header → a different class
```

## Attack 2 — the client-supplied bypass

```text
setup:   an app that trusts a proxy header — a client-supplied header
         IS trusted
mechanism: a forged local IP → a local request → the trust check bypassed
probe:   a client-supplied X-Real-IP: 127.0.0.1 → a 200 on the gated route
falsifier: the proxy strips the client-supplied header → the hop-by-hop
         bypass is the vector
```

## Attack 3 — the forwarded-host rewrite

```text
setup:   an app that builds absolute URLs from X-Forwarded-Host
mechanism: a client-supplied X-Forwarded-Host rewrites the app's links —
         the app's links/scripts point to attacker.com
probe:   X-Forwarded-Host: attacker.com → the links point to it
falsifier: the app doesn't use X-Forwarded-Host → a different surface
```

## Attack 4 — the forwarded-scheme downgrade

```text
setup:   an app that builds absolute URLs from X-Forwarded-Scheme
mechanism: a client-supplied X-Forwarded-Scheme downgrades the app's
         links — the links use http
probe:   X-Forwarded-Scheme: http → the links use http
falsifier: the app doesn't use X-Forwarded-Scheme → a different surface
```

## Attack 5 — the X-Original-URL rewrite

```text
setup:   an app that honors X-Original-URL
mechanism: a client-supplied X-Original-URL rewrites the path — the app
         serves a different route
probe:   X-Original-URL: /admin → the app serves /admin under /page
falsifier: the app doesn't honor X-Original-URL → a different surface
```

## Attack 6 — the internal-flag bypass

```text
setup:   an app that checks X-Internal for an internal-route check
mechanism: a client-supplied X-Internal: true → the check passes → an
         internal route reached
probe:   X-Internal: true → a 200 on the internal route
falsifier: the app doesn't check X-Internal → a different surface
```

## Attack 7 — the admin-flag bypass

```text
setup:   an app that checks X-Admin for an admin check
mechanism: a client-supplied X-Admin: true → the check passes → an admin
         route reached
probe:   X-Admin: true → a 200 on the admin route
falsifier: the app doesn't check X-Admin → a different surface
```

## Attack 8 — the forwarded-for spoof

```text
setup:   an app that reads X-Forwarded-For for a local-vs-remote check
mechanism: a client-supplied X-Forwarded-For: 127.0.0.1 → a local request
         → the trust check bypassed
probe:   X-Forwarded-For: 127.0.0.1 → a 200 on the gated route
falsifier: the proxy strips the client-supplied header → the hop-by-hop
         bypass is the vector
```

## Attack 9 — the path-normalization bypass

```text
setup:   a path the proxy and the app normalize differently
mechanism: a /static/../admin the proxy normalizes to /admin and the app
         routes to /admin — a normalization differential
probe:   /static/../admin → the app serves /admin
falsifier: the proxy and the app normalize the same way → no confusion
```

## Attack 10 — the method-override bypass

```text
setup:   an app that honors X-HTTP-Method-Override
mechanism: a client-supplied override changes the method — a DELETE-as-POST
probe:   X-HTTP-Method-Override: DELETE → the app treats it as DELETE
falsifier: the app doesn't honor the override → a different surface
```

## Attack 11 — the forwarded-proto downgrade

```text
setup:   an app that builds absolute URLs from X-Forwarded-Proto
mechanism: a client-supplied X-Forwarded-Proto downgrades the app's links
         — the links use http
probe:   X-Forwarded-Proto: http → the links use http
falsifier: the app doesn't use X-Forwarded-Proto → a different surface
```

## Attack 12 — the Forwarded header spoof

```text
setup:   an app that reads the RFC 7239 Forwarded header
mechanism: a client-supplied Forwarded: for=127.0.0.1 → a local request
         → the trust check bypassed
probe:   Forwarded: for=127.0.0.1 → a 200 on the gated route
falsifier: the app doesn't read Forwarded → a different surface
```

## Attack 13 — the multi-proxy differential

```text
setup:   a multi-proxy chain — an edge + an origin proxy
mechanism: a header each strips differently — a chained normalization
         boundary — a per-layer differential
probe:   a header the edge strips but the origin doesn't → a chained
         differential
falsifier: both proxies strip the same way → no chained differential
```

## Attack 14 — the X-Forwarded-User spoof

```text
setup:   an app that reads X-Forwarded-User for a user check
mechanism: a client-supplied X-Forwarded-User: admin → an admin user →
         a user bypass
probe:   X-Forwarded-User: admin → a 200 on the user route
falsifier: the app doesn't check X-Forwarded-User → a different surface
```

## Attack 15 — the multi-header bypass

```text
setup:   a multi-header bypass — a forged IP + a forged flag
mechanism: a combined injection — a local + an internal check → a
         privileged route
probe:   X-Real-IP: 127.0.0.1 + X-Internal: true → a 200 on the internal
         route
falsifier: the app checks a different input → a different class
```
