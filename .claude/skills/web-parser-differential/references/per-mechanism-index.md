# Per-mechanism index — every mechanism, indexed

The mechanism index — a header the app reads, a check the header gates.

---

## 1. The hop-by-hop bypass — the verified card's mechanism

```text
a proxy strips the headers it names in Connection — naming the proxy's
own header in Connection strips it — the app sees a request without
the trusted header — a missing-header fallback treats it as local —
the trust check bypassed.
```

## 2. The client-supplied bypass — a forged proxy-header

```text
a client-supplied proxy header → the app trusts it → the app doesn't
verify the proxy added it → the client-supplied header IS trusted →
a forged local IP → a local request → the trust check bypassed.
```

## 3. The forwarded-host rewrite — a stored injection

```text
a client-supplied X-Forwarded-Host → the app's links point to
attacker.com → the stored page's links fetch attacker.com → a stored-
injection reach.
```

## 4. The forwarded-scheme downgrade — a scheme confusion

```text
a client-supplied X-Forwarded-Scheme → the app's links use http → a
downgrade surface → a mixed-content or a downgrade → the downstream.
```

## 5. The X-Original-URL rewrite — a path-rewrite

```text
a client-supplied X-Original-URL → the app's route rewritten → a
route-confusion.
```

## 6. The internal-flag bypass — a flag-forgery

```text
a client-supplied X-Internal → the internal-route check passes → the
internal route reached.
```

## 7. The admin-flag bypass — a flag-forgery

```text
a client-supplied X-Admin → the admin check passes → the admin route
reached.
```

## 8. The forwarded-for spoof — a local-IP forgery

```text
a client-supplied X-Forwarded-For → the local-vs-remote check passes →
a local request → the trust check bypassed.
```

## 9. The Forwarded-header spoof — an RFC 7239 forgery

```text
a client-supplied Forwarded header → the local-vs-remote check passes →
a local request → the trust check bypassed.
```

## 10. The path-normalization bypass — a normalization differential

```text
a path the proxy and the app normalize differently → the proxy's check
reads a different path than the app's → a route-confusion reach → a
gated route → the downstream.
```

## 11. The method-override bypass — a method forgery

```text
a client-supplied X-HTTP-Method-Override → the method rewritten → a
method-override.
```

## 12. The X-Forwarded-User spoof — a user forgery

```text
a client-supplied X-Forwarded-User → the user check passes → a forged
admin user.
```

## 13. The multi-proxy differential — a chained normalization

```text
a multi-proxy chain → a header each strips differently → a chained
normalization boundary → a per-layer differential → a gated route →
the downstream.
```

## 14. The multi-header bypass — a combined forgery

```text
a combined injection — a forged IP + a forged flag — a local + an
internal check → a privileged route reached.
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
