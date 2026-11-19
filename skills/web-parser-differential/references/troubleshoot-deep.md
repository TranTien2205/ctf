# Troubleshoot deep — the parser-differential failures, exhaustively

The failures — what went wrong, and the fix.

---

## 1. The hop-by-hop bypass failed — the proxy doesn't strip its own header

```text
symptom:   a Connection: keep-alive, X-Real-IP returns the same 401
cause:     the proxy doesn't strip its own header — the proxy's header
           stays → a different class
fix:       a client-supplied bypass (a forged X-Real-IP) is the
           remaining vector — or a different class
```

## 2. The client-supplied bypass failed — the proxy strips the client header

```text
symptom:   a client-supplied X-Real-IP returns the same 401
cause:     the proxy strips the client-supplied header — the header
           doesn't reach the app
fix:       the hop-by-hop bypass is the vector — or a different class
```

## 3. The client-supplied bypass failed — the proxy verifies

```text
symptom:   a client-supplied X-Real-IP returns the same 401
cause:     the proxy verifies the header it added — the client-supplied
           header is rejected
fix:       the hop-by-hop bypass is the vector — or a different class
```

## 4. The check isn't the header — a non-header check

```text
symptom:   a client-supplied X-Real-IP returns the same 401
cause:     the trust check reads a different input — a session, a token,
           a signature — the header isn't the check's input
fix:       a different class
```

## 5. The normalization failed — the same parse

```text
symptom:   a /static/../admin returns the same 404
cause:     the proxy and the app normalize the same way — no confusion
fix:       a different class
```

## 6. The 200 on a non-gated route — a false positive

```text
symptom:   a 200 on a route that wasn't gated
cause:     the route wasn't gated — a false positive
fix:       a different class
```

## 7. The 200 on a gated route — the bypass's reach

```text
symptom:   a 200 on a gated route
cause:     the check bypassed — the route reached
fix:       the bypass's evidence — the downstream's read
```

## 8. The proxy doesn't strip its own header — the verified card's trap

```text
the verified card's trap — the proxy strips its own header — a proxy
that doesn't → the hop-by-hop bypass fails → a different class.
```

## 9. The proxy strips the client header — the client-supplied's trap

```text
the client-supplied's trap — a proxy that strips a client-supplied
proxy header → the client-supplied header doesn't reach the app →
the client-supplied bypass fails → the hop-by-hop bypass is the vector.
```

## 10. The proxy verifies — the client-supplied's trap

```text
the client-supplied's trap — a proxy that verifies the header it added
→ a client-supplied header is rejected → the client-supplied bypass
fails → the hop-by-hop bypass is the vector.
```

## 11. The non-header check — the check's input

```text
the check's input — a trust check that reads a different input (a
session, a token, a signature) → the header isn't the check's input →
a different class.
```

## 12. The same parse — the normalization's trap

```text
the normalization's trap — a path the proxy and the app normalize the
same way → no confusion → a different class.
```

## 13. The stored copy — the cache-poisoning trap

```text
the cache-poisoning trap — a stored copy that serves YOUR input → a
cache-poisoning (a store) → not a parser-differential (a parse).
```

## 14. The desync — the request-smuggling trap

```text
the request-smuggling trap — a front-end and a back-end that parse the
request boundary differently → a request-smuggling (a desync) → not a
parser-differential (a parse).
```

## 15. The budget — the probe limits

```text
5 probes or 15 minutes per mechanism class; 25 probes or 45 minutes
for the challenge. a spent budget → escalate: chain_match → reclassify
→ writeup_search → novel_plan → fanout_sweep → solver_handoff.
```
