# Per-falsifier — every parser-differential falsifier, exhaustively

The falsifier map — a condition that kills the differential.

---

## 1. A proxy that doesn't strip its own header — the hop-by-hop trap

```text
a proxy that doesn't strip its own header → the hop-by-hop bypass fails
→ the proxy's header stays → a different class.
```

## 2. A proxy that strips the client header — the client-supplied trap

```text
a proxy that strips a client-supplied proxy header → the client-supplied
header doesn't reach the app → the client-supplied bypass fails → the
hop-by-hop bypass is the vector.
```

## 3. A proxy that verifies — the client-supplied trap

```text
a proxy that verifies the header it added → a client-supplied header is
rejected → the client-supplied bypass fails → the hop-by-hop bypass is
the vector.
```

## 4. A non-header check — the check's input

```text
a trust check that reads a different input (a session, a token, a
signature) → the header isn't the check's input → a different class.
```

## 5. The same parse — the normalization trap

```text
a path the proxy and the app normalize the same way → no confusion →
a different class.
```

## 6. A stored copy — the cache-poisoning trap

```text
a stored copy that serves YOUR input → a cache-poisoning (a store) →
not a parser-differential (a parse).
```

## 7. A desync — the request-smuggling trap

```text
a front-end and a back-end that parse the request boundary differently
→ a request-smuggling (a desync) → not a parser-differential (a parse).
```

## 8. A session check — the auth-session trap

```text
a trust check that reads a session / a token → an auth-session → not
a parser-differential.
```

## 9. A host check — the host-header trap

```text
a trust check that reads a Host header → a host-header → not a parser-
differential.
```

## 10. A fetch — the ssrf trap

```text
a server-side fetch — the app fetches a URL the request controls →
an ssrf → not a parser-differential.
```

## 11. A read — the cors trap

```text
a cross-origin fetch — the app's bytes read → a cors → not a parser-
differential.
```

## 12. A false positive — the 200 on a non-gated route

```text
a 200 on a route that wasn't gated → a false positive → a different
class.
```

## 13. A non-proxy app — a different surface

```text
an app that doesn't sit behind a proxy → no proxy header → a different
class.
```

## 14. A keyed header — a proxy that keys on the header

```text
a proxy that keys on the header → a client-supplied header changes the
key → the client's own entry → a self-read → a different class.
```

## 15. A non-forwarded header — a proxy that doesn't forward

```text
a proxy that doesn't forward the header → the app's check reads a
different header → a different class.
```

## 16. A multi-proxy chain — a chained normalization

```text
a multi-proxy chain — a header each strips differently — a chained
normalization boundary — a per-layer differential.
```

## 17. An origin-only proxy — a single-hop chain

```text
an origin-only proxy — a single-hop chain — the proxy's header is the
only one — the app's check reads it → a single-hop differential.
```

## 18. An edge-only proxy — a single-hop chain

```text
an edge-only proxy — a single-hop chain — the proxy's header is the
only one — the app's check reads it → a single-hop differential.
```

## 19. A proxy that keys on the header — a keyed entry

```text
a proxy that keys on the header → a client-supplied header changes the
key → the client's own entry → a self-read → a different class.
```

## 20. A proxy that doesn't forward the header — a non-forwarded

```text
a proxy that doesn't forward the header → the app's check reads a
different header → a different class.
```

## 21. A proxy that normalizes differently — a path-rewrite

```text
a proxy that normalizes a path differently → the app's route reads a
different path → a normalization differential → a route-confusion.
```

## 22. A proxy that rewrites the path — a rewrite

```text
a proxy that rewrites the path → the app's route reads a different path
→ a rewrite → a route-confusion.
```

## 23. A proxy that preserves the host — a host-forward

```text
a proxy that preserves the host → the app's check reads the original
Host → a host-forward → a host-header.
```

## 24. A proxy that rewrites the host — a host-rewrite

```text
a proxy that rewrites the host → the app's check reads the rewritten
Host → a host-rewrite → a host-header.
```

## 25. A proxy that adds a scheme — a scheme-forward

```text
a proxy that adds a scheme → the app's check reads the forwarded scheme
→ a scheme-forward → a scheme-check.
```

## 26. A proxy that rewrites the scheme — a scheme-rewrite

```text
a proxy that rewrites the scheme → the app's check reads the rewritten
scheme → a scheme-rewrite → a scheme-check.
```

## 27. A proxy that adds a proto — a proto-forward

```text
a proxy that adds a proto → the app's check reads the forwarded proto
→ a proto-forward → a proto-check.
```

## 28. A proxy that rewrites the proto — a proto-rewrite

```text
a proxy that rewrites the proto → the app's check reads the rewritten
proto → a proto-rewrite → a proto-check.
```

## 29. A proxy that adds a user — a user-forward

```text
a proxy that adds a user → the app's check reads the forwarded user →
a user-forward → a user-check.
```

## 30. A proxy that rewrites the user — a user-rewrite

```text
a proxy that rewrites the user → the app's check reads the rewritten
user → a user-rewrite → a user-check.
```
