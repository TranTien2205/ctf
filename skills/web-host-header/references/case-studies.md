# Case studies — the host-header attack patterns

The canonical published patterns — each with its setup, mechanism, probe, and falsifier.

---

## Case A — the canonical-URL poisoning — a stored injection

```text
setup:   an app that builds absolute URLs from the Host header
mechanism: a reflected Host poisons the app's links — the links/scripts
         point to attacker.com — a stored injection
probe:   Host: canary.example → the canonical URLs point to canary.example
falsifier: a proxy that validates the Host against a server list → a 400
```

## Case B — the password-reset poisoning — an account takeover

```text
setup:   an app that builds reset links from a forwarded header
mechanism: a reflected forwarded header poisons the reset link — the link
         points to attacker.com — the victim's reset token stolen — an
         account takeover
probe:   X-Forwarded-Host: canary.example → the reset link points to
         canary.example
falsifier: a proxy that strips the forwarded header → the header doesn't
         reach the app
```

## Case C — the X-Original-URL bypass — an ACL bypass

```text
setup:   a middleware that honors X-Original-URL
mechanism: a client-supplied X-Original-URL rewrites the path — the app
         serves a different route — an ACL bypass
probe:   X-Original-URL: /admin → the app serves /admin under /page
falsifier: a proxy that strips the rewrite header → the header doesn't
         reach the app
```

## Case D — the X-Rewrite-URL bypass — an ACL bypass

```text
setup:   a middleware that honors X-Rewrite-URL
mechanism: a client-supplied X-Rewrite-URL rewrites the path — the app
         serves a different route — an ACL bypass
probe:   X-Rewrite-URL: /admin → the app serves /admin under /page
falsifier: a proxy that strips the rewrite header → the header doesn't
         reach the app
```

## Case E — the Location poisoning — an open redirect

```text
setup:   an app that builds redirects from the Host header
mechanism: a reflected Host poisons the redirect — the Location points
         to attacker.com — an open redirect
probe:   Host: canary.example → the Location points to canary.example
falsifier: a proxy that validates the Host against a server list → a 400
```

## Case F — the Set-Cookie poisoning — a session fixation

```text
setup:   an app that binds cookies to the Host header
mechanism: a reflected Host poisons the cookie domain — the cookie binds
         to attacker.com — a session fixation
probe:   Host: canary.example → the Set-Cookie domain binds to
         canary.example
falsifier: a proxy that validates the Host against a server list → a 400
```

## Case G — the cache-key poisoning — a cache-poisoning feed

```text
setup:   a cache that stores pages under the Host header
mechanism: a reflected Host poisons the cache key — the cache stores
         the page under attacker.com — a cache-poisoning feed
probe:   Host: canary.example → the cache stores the page under
         canary.example
falsifier: a proxy that validates the Host against a server list → a 400
```

## Case H — the duplicated Host bypass — a parsing differential

```text
setup:   a proxy and an app that parse a duplicated Host differently
mechanism: a duplicated Host — the proxy reads the first; the app reads
         the second → a differential
probe:   Host: good.example + Host: evil.example → a differential
falsifier: the proxy and the app parse the same way → no confusion
```

## Case I — the malformed Host bypass — a parsing edge

```text
setup:   a proxy and an app that parse a malformed Host differently
mechanism: a malformed Host — a trailing dot, a double-dot, an @-
         separator, a #-separator, a ?-separator, an empty host, a
         forged port → a differential
probe:   Host: evil.example:80 / Host: evil.example. / Host: . → a
         differential
falsifier: the proxy and the app parse the same way → no confusion
```

## Case J — the absolute-URI bypass — a request-line differential

```text
setup:   a proxy and an app that parse an absolute-URI differently
mechanism: an absolute-URI Host — the proxy reads the Host header; the
         app reads the absolute-URI → a differential
probe:   --request-target 'http://evil.example/' → a differential
falsifier: the proxy and the app parse the same way → no confusion
```

## Case K — the forwarded-header bypass — a stored injection

```text
setup:   an app that builds absolute URLs from a forwarded header
mechanism: a reflected forwarded header poisons the app's links — the
         links/scripts point to attacker.com — a stored injection
probe:   X-Forwarded-Host: canary.example → the links point to
         canary.example
falsifier: a proxy that strips the forwarded header → the header doesn't
         reach the app
```

## Case L — the RFC 7239 bypass — a stored injection

```text
setup:   an app that builds absolute URLs from a Forwarded header
mechanism: a reflected Forwarded header poisons the app's links — the
         links/scripts point to attacker.com — a stored injection
probe:   Forwarded: host=canary.example → the links point to
         canary.example
falsifier: a proxy that strips the forwarded header → the header doesn't
         reach the app
```

## Case M — the multi-header bypass — a combined injection

```text
setup:   a multi-header bypass — a forged host + a forged flag
mechanism: a combined injection — a host + an internal check → a
         privileged route reached
probe:   Host: evil.example + X-Internal: true → a 200 on the internal
         route
falsifier: the app checks a different input → a different class
```

## Case N — the multi-proxy bypass — a chained normalization

```text
setup:   a multi-proxy chain — a header each strips differently
mechanism: a chained normalization boundary — a per-layer differential
probe:   X-Forwarded-Host: attacker.com → the edge strips it; the origin
         doesn't → a chained differential
falsifier: both proxies strip the same way → no chained differential
```

## Case O — the forwarded-for spoof — a local-IP forgery

```text
setup:   an app that reads X-Forwarded-For for a local-vs-remote check
mechanism: a client-supplied X-Forwarded-For: 127.0.0.1 → a local
         request → the trust check bypassed
probe:   X-Forwarded-For: 127.0.0.1 → a 200 on the gated route
falsifier: the proxy strips the forwarded header → the header doesn't
         reach the app
```
