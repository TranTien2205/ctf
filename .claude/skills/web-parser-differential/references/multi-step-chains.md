# Multi-step chains — the parser-differential chains, end to end

The chained attacks — a differential + a downstream.

---

## 1. The hop-by-hop + token_required chain — the verified card's shape

```text
a hop-by-hop bypass → the proxy strips its own header → the app treats
the request as local → the token_required check skipped → a restricted
route reached → the downstream (a cache-overflow, a DOM-clobber, a
polyglot exfil).
```

## 2. The client-supplied + gated-route chain — a forged-header reach

```text
a client-supplied proxy header → the app trusts it → a local request →
the trust check bypassed → a gated route reached → the downstream.
```

## 3. The forwarded-host + XSS chain — a stored-injection reach

```text
a client-supplied X-Forwarded-Host → the app's links point to
attacker.com → the stored page's links fetch attacker.com → a stored-
XSS-like reach → the downstream.
```

## 4. The forwarded-scheme + downgrade chain — a scheme-confusion reach

```text
a client-supplied X-Forwarded-Scheme → the app's links use http → a
downgrade surface → a mixed-content or a downgrade → the downstream.
```

## 5. The path-normalization + route-confusion chain — a normalization reach

```text
a path the proxy and the app normalize differently → the proxy's check
reads a different path than the app's → a route-confusion reach → a
gated route → the downstream.
```

## 6. The internal-flag + privileged-route chain — a flag-bypass reach

```text
a client-supplied X-Internal: true → the internal-route check passes →
an internal route reached → the downstream.
```

## 7. The admin-flag + admin-route chain — a flag-bypass reach

```text
a client-supplied X-Admin: true → the admin check passes → an admin
route reached → the downstream.
```

## 8. The multi-proxy + chained-differential chain — a per-layer reach

```text
a multi-proxy chain → a header each strips differently → a chained
normalization boundary → a per-layer differential → a gated route →
the downstream.
```

## 9. The hop-by-hop + cache-overflow + DOM-clobber chain — the verified card

```text
the verified card's chain:
step 1 — the hop-by-hop bypass: the proxy strips its own header → the
         app treats the request as local → the token_required check
         bypassed → a restricted route reached
step 2 — a cache-overflow: the custom cache daemon's strcpy overflows
         a fixed-size value → the write lands in the next entry's key
         → another user's record addressed
step 3 — a DOM-clobber prototype-pollution: the site's own script's
         DOM lookups clobbered → the fetch redirected → the prototype
         polluted → the eval's value attacker-controlled
step 4 — a polyglot exfil: the admin's cookie exfiltrated through the
         same-site store → the flag
```

## 10. The per-chain falsifier — when the chain breaks

```text
a proxy that doesn't strip its own header → the hop-by-hop bypass fails
→ a different class.
a proxy that strips a client-supplied header → the client-supplied
bypass fails → the hop-by-hop bypass is the vector.
a non-header check → a different class.
```

## 11. The per-chain probe map — which chain for which surface

```text
a local-vs-remote check     → the hop-by-hop bypass / the client-supplied
an internal-route check     → a spoofed-internal header / a hop-by-hop
an admin check              → a spoofed-admin header / a hop-by-hop
a host check                → a spoofed-host header
a scheme check              → a spoofed-scheme header
a path check                → a spoofed-path header / a normalization
a multi-proxy chain         → a chained normalization
```

## 12. The chain's budget — the probe limits

```text
5 probes or 15 minutes per mechanism class; 25 probes or 45 minutes
for the challenge. a spent budget → escalate: chain_match → reclassify
→ writeup_search → novel_plan → fanout_sweep → solver_handoff.
```
