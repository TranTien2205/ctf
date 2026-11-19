# Detection matrix — the per-surface signals, exhaustively

The complete signal map — which signals name which surface.

---

## 1. The proxy-presence signals — a proxy exists

```text
a 'Via|X-Forwarded|X-Real|x-served|x-backend|x-upstream|cf-|x-varnish|traefik'
  → a proxy in the path
a 'Via:' header → a proxy chain
an 'X-Forwarded-*' → a proxy's forwarded headers
an 'X-Real-IP' → a proxy's client-IP header
an 'X-Served-By' / an 'X-Varnish' → a Fastly/Varnish proxy
a 'CF-*' / an 'X-Amzn-*' → a Cloudflare/CloudFront edge
a 'Server: traefik' → a Traefik proxy
```

## 2. The trust-check signals — the app's proxy-header input

```text
a 'X-Real-IP|X-Forwarded|X-Internal|X-Admin|X-Original|X-Rewrite|client_ip|remote_addr|request.headers|request\.META|request\.env|header'
  → the app's proxy-header input
a 'request.headers' → the app reads a header
a 'request.META' → the app reads a META header
a 'request.env' → the app reads an env header
a 'header.get' / 'getattr' → the app reads a header with a fallback
```

## 3. The missing-header fallback signals — the local-request check

```text
a '127.0.0.1|localhost|local|internal|trust|fallback|missing|getattr|header\.get|request.headers.get|remote_addr|is_local'
  → the missing-header fallback
a '127.0.0.1' / 'localhost' → a local-vs-remote check
a 'local' / 'internal' → an internal-route check
a 'trust' / 'fallback' / 'missing' → a fallback check
a 'is_local' / 'is_internal' → a local-request check
```

## 4. The gated-route signals — the restricted endpoint

```text
a 'restricted|internal|admin|auth|token_required|required|login_required|@auth|@admin|private|api|debug|preview'
  → a gated route
a 'token_required' / 'login_required' → an authenticated-only route
a '@auth' / '@admin' → an admin route
a 'internal' / 'private' → an internal route
a 'restricted' / 'debug' / 'preview' → a restricted route
```

## 5. The hop-by-hop surface signals — the Connection-strip

```text
a 'Connection|hop-by-hop|strip|header|proxy'
  → the hop-by-hop surface
a 'Connection' header → a hop-by-hop control
a 'strip' → a proxy strip
a 'hop-by-hop' → a hop-by-hop boundary
```

## 6. The normalization surface signals — a path difference

```text
a 'normalize|redirect|rewrite|path|decode|urldecode|canonical|route|parse'
  → the normalization surface
a 'normalize' / 'canonical' → a path normalization
a 'redirect' / 'rewrite' → a path rewrite
a 'decode' / 'urldecode' → a path decode
a 'route' / 'parse' → a route parse
```

## 7. The client-supplied surface signals — a forged header

```text
a 'request.headers|request\.META|request\.env|header\.get|getattr'
  → the client-supplied surface
a 'request.headers' → the app reads a header
a 'request.META' → the app reads a META header
a 'request.env' → the app reads an env header
a 'header.get' / 'getattr' → the app reads a header with a fallback
```

## 8. The per-proxy header-map — which headers each proxy adds

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

## 9. The per-surface check-map — which check for which surface

```text
a local-vs-remote check     → a spoofed-IP header / a hop-by-hop strip
an internal-route check     → a spoofed-internal header / a hop-by-hop strip
an admin check              → a spoofed-admin header / a hop-by-hop strip
a host check                → a spoofed-host header
a scheme check              → a spoofed-scheme header
a path check                → a spoofed-path header / a normalization
a method check              → a spoofed-method header
a user check                → a spoofed-user header
a multi-proxy chain         → a chained normalization
```

## 10. The per-surface falsifier — when the surface is dead

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

## 11. The matrix's budget — the probe limits

```text
5 probes or 15 minutes per mechanism class; 25 probes or 45 minutes
for the challenge. a spent budget → escalate: chain_match → reclassify
→ writeup_search → novel_plan → fanout_sweep → solver_handoff.
```

## 12. The matrix's proof — the differential confirm

```text
the differential confirm:
1. the front-end reads one value (the proxy's check)
2. the back-end reads another (the app's check)
3. the differential reaches a route the front-end's check gates
a two-request check — the proxy strips its own header → the app's
check reads the missing header's fallback.
```
