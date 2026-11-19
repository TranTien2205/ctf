# Class boundary — host-header vs the neighbors, exhaustively

The boundary map — when it's this class, when it's a neighbor.

---

## 1. The boundary — a host the app trusts

```text
a host-header is a HOST-header injection — a forged host → a canonical-
URL rewrite, a reset-link poisoning, a Location redirect, a Set-Cookie
domain, a cache key, a middleware rewrite — the app's trust check reads
the host's value.
```

## 2. vs parser-differential — a host vs a proxy header

```text
a host-header           → a HOST-header injection — a forged host → a
                        canonical-URL rewrite, a reset-link poisoning,
                        a Location redirect, a Set-Cookie domain, a
                        cache key.
a parser-differential   → a PROXY-header trust — a client-supplied or
                        a missing proxy header's fallback → a trust
                        check bypassed.
the boundary            → a host-vs-proxy split — a host-header is the
                        Host; a parser-differential is a proxy header.
```

## 3. vs cache-poisoning — a host vs a store

```text
a host-header           → a HOST-header injection — a forged host → a
                        canonical-URL rewrite, a reset-link poisoning,
                        a Location redirect, a Set-Cookie domain, a
                        cache key.
a cache-poisoning       → a STORE — a stored copy that serves YOUR
                        input — a key-mismatch — a store.
the boundary            → a host-vs-store split — a host-header is a
                        host; a cache-poisoning is a store.
```

## 4. vs auth-session — a host vs a session

```text
a host-header           → a HOST-header injection — a forged host → a
                        canonical-URL rewrite, a reset-link poisoning,
                        a Location redirect, a Set-Cookie domain, a
                        cache key.
an auth-session         → a SESSION check — a trust check reads a
                        session / a token — a cookie, a JWT, a signature.
the boundary            → a host-vs-session split — a host-header is a
                        host; an auth-session is a session.
```

## 5. vs open-redirect — a host vs a redirect

```text
a host-header           → a HOST-header injection — a forged host → a
                        canonical-URL rewrite, a reset-link poisoning,
                        a Location redirect, a Set-Cookie domain, a
                        cache key.
an open-redirect        → a REDIRECT — the app redirects to a URL the
                        request controls.
the boundary            → a host-vs-redirect split — a host-header is a
                        host; an open-redirect is a redirect.
```

## 6. vs ssrf — a host vs a fetch

```text
a host-header           → a HOST-header injection — a forged host → a
                        canonical-URL rewrite, a reset-link poisoning,
                        a Location redirect, a Set-Cookie domain, a
                        cache key.
an ssrf                 → a FETCH — the app fetches a URL the request
                        controls.
the boundary            → a host-vs-fetch split — a host-header is a
                        host; an ssrf is a fetch.
```

## 7. vs cors — a host vs a read

```text
a host-header           → a HOST-header injection — a forged host → a
                        canonical-URL rewrite, a reset-link poisoning,
                        a Location redirect, a Set-Cookie domain, a
                        cache key.
a cors                  → a READ — a cross-origin fetch — the app's
                        bytes read.
the boundary            → a host-vs-read split — a host-header is a
                        host; a cors is a read.
```

## 8. vs request-smuggling — a host vs a desync

```text
a host-header           → a HOST-header injection — a forged host → a
                        canonical-URL rewrite, a reset-link poisoning,
                        a Location redirect, a Set-Cookie domain, a
                        cache key.
a request-smuggling     → a DESYNC — a front-end and a back-end parse
                        the request boundary differently.
the boundary            → a host-vs-desync split — a host-header is a
                        host; a request-smuggling is a desync.
```

## 9. The boundary's falsifier — when it's not this class

```text
a proxy that validates the Host against a server list → a 400 on a bad
host → a negative result, not a retry signal.
a proxy that strips the client-supplied forwarded header → the header
doesn't reach the app → the bypass fails → a different class.
a proxy that verifies the forwarded header it added → a client-supplied
header is rejected → the bypass fails → a different class.
a trust check that reads a different input → a different class.
a session check → an auth-session
a redirect → an open-redirect
a fetch → an ssrf
a read → a cors
a desync → a request-smuggling
a store → a cache-poisoning
a proxy header → a parser-differential
```

## 10. The boundary's scope — which checks are bypassed

```text
the host-header bypasses a check the Host header gates — a canonical
URL, a reset link, a Location redirect, a Set-Cookie domain, a cache
key, a middleware rewrite — the app's trust check reads the Host's
value.
```

## 11. The boundary's reach — the downstream

```text
the boundary's reach is the downstream — a canonical URL the app's
links rewrite — a reset link the victim clicks — a cache key the cache
stores — a Location the proxy redirects — a Set-Cookie the app binds —
a middleware rewrite the app's route reads.
```

## 12. The boundary's budget — the probe limits

```text
5 probes or 15 minutes per mechanism class; 25 probes or 45 minutes
for the challenge. a spent budget → escalate: chain_match → reclassify
→ writeup_search → novel_plan → fanout_sweep → solver_handoff.
```
