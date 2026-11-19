# Theory — why host-header attacks exist, and why they work

The mechanism — the host-header trust model, exhaustively.

---

## 1. The model — a host the app trusts

```text
the app reads the Host header for its canonical URLs — a reflected or
a rewritten Host poisons the app's links — the links/scripts point to
attacker.com — a stored injection, a cache-poisoning feed, a password-
reset poisoning.
```

## 2. The host-header's sinks — where it poisons

```text
a canonical URL      → the app's links/scripts point to attacker.com
a password-reset link → the reset link points to attacker.com — an
                      account takeover
a Location redirect  → an open redirect, an SSO flow poisoning
a Set-Cookie domain  → a session fixation surface
a cache key          → a cache-poisoning feed — poison once, the cache
                     serves your host to everyone
```

## 3. The host-header's trust — the app's check

```text
the app's trust check reads the Host header's value — a reflected or
a rewritten Host poisons the app's links — the app's check reads the
header's value.
```

## 4. The forwarded-header's trust — the app's check

```text
the app's trust check reads a forwarded header's value — a reflected
or a rewritten forwarded header poisons the app's links — the app's
check reads the header's value.
```

## 5. The rewrite-header's trust — the middleware's check

```text
the middleware's trust check reads a rewrite header's value — a
rewritten path reaches a gated route — an ACL bypass, a route-confusion,
an internal route reached.
```

## 6. The duplicated Host — a parsing differential

```text
a duplicated Host — the proxy and the app parse differently — the
proxy reads the first; the app reads the second → a differential.
```

## 7. The malformed Host — a parsing edge

```text
a malformed Host — a parsing edge — a trailing dot, a double-dot, an
@-separator, a #-separator, a ?-separator, an empty host, a forged
port — the proxy and the app parse differently → a differential.
```

## 8. The absolute-URI Host — a request-line differential

```text
an absolute-URI Host — a request-line differential — the proxy reads
the Host header; the app reads the absolute-URI → a differential.
```

## 9. The host-header's falsifier — a proxy that validates

```text
a proxy that validates the Host against a server list → a 400 on a bad
host → a negative result, not a retry signal.
```

## 10. The host-header's falsifier — a proxy that strips

```text
a proxy that strips the client-supplied forwarded header → the header
doesn't reach the app → the bypass fails → a different class.
```

## 11. The host-header's falsifier — a proxy that verifies

```text
a proxy that verifies the forwarded header it added → a client-supplied
header is rejected → the bypass fails → a different class.
```

## 12. The host-header's falsifier — a non-header check

```text
a trust check that reads a different input (a session, a token, a
signature) → the header isn't the check's input → a different class.
```

## 13. The host-header's scope — which checks are bypassed

```text
the host-header bypasses a check the Host header gates — a canonical
URL, a password-reset link, a Location redirect, a Set-Cookie domain,
a cache key — the app's trust check reads the Host's value.
```

## 14. The host-header's reach — the downstream

```text
the host-header's reach is the downstream — a canonical URL the app's
links rewrite — a reset link the victim clicks — a cache key the cache
stores — a Location the proxy redirects — a Set-Cookie the app binds.
```

## 15. The class boundary — a host-vs-proxy split

```text
a host-header is a HOST-header injection — a forged host → a canonical-
URL rewrite, a reset-link poisoning, a Location redirect, a Set-Cookie
domain, a cache key. a parser-differential is a PROXY-header trust — a
client-supplied or a missing proxy header's fallback → a trust check
bypassed.
```

## 16. The class boundary — a host-vs-cache split

```text
a host-header is a HOST-header injection — a forged host → a canonical-
URL rewrite, a reset-link poisoning, a Location redirect, a Set-Cookie
domain, a cache key. a cache-poisoning is a STORE — a stored copy that
serves YOUR input — a key-mismatch — a store.
```
