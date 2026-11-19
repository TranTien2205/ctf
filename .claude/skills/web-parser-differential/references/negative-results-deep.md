# Negative results deep — the dead paths, exhaustively

The dead paths — a probe that produced nothing, recorded.

---

## 1. The proxy doesn't strip its own header — the hop-by-hop trap

```text
a proxy that doesn't strip its own header → the hop-by-hop bypass fails
→ the proxy's header stays → a different class.
```

## 2. The proxy strips the client header — the client-supplied trap

```text
a proxy that strips a client-supplied proxy header → the client-supplied
header doesn't reach the app → the client-supplied bypass fails → the
hop-by-hop bypass is the vector.
```

## 3. The proxy verifies — the client-supplied trap

```text
a proxy that verifies the header it added → a client-supplied header is
rejected → the client-supplied bypass fails → the hop-by-hop bypass is
the vector.
```

## 4. The non-header check — the check's input

```text
a trust check that reads a different input (a session, a token, a
signature) → the header isn't the check's input → a different class.
```

## 5. The same parse — the normalization trap

```text
a path the proxy and the app normalize the same way → no confusion →
a different class.
```

## 6. The stored copy — the cache-poisoning trap

```text
a stored copy that serves YOUR input → a cache-poisoning (a store) →
not a parser-differential (a parse).
```

## 7. The desync — the request-smuggling trap

```text
a front-end and a back-end that parse the request boundary differently
→ a request-smuggling (a desync) → not a parser-differential (a parse).
```

## 8. The session check — the auth-session trap

```text
a trust check that reads a session / a token → an auth-session → not
a parser-differential.
```

## 9. The host check — the host-header trap

```text
a trust check that reads a Host header → a host-header → not a parser-
differential.
```

## 10. The fetch — the ssrf trap

```text
a server-side fetch — the app fetches a URL the request controls →
an ssrf → not a parser-differential.
```

## 11. The read — the cors trap

```text
a cross-origin fetch — the app's bytes read → a cors → not a parser-
differential.
```

## 12. The false positive — the 200 on a non-gated route

```text
a 200 on a route that wasn't gated → a false positive → a different
class.
```

## 13. The non-proxy app — a different surface

```text
an app that doesn't sit behind a proxy → no proxy header → a different
class.
```

## 14. The keyed header — a proxy that keys on the header

```text
a proxy that keys on the header → a client-supplied header changes the
key → the client's own entry → a self-read → a different class.
```

## 15. The non-forwarded header — a proxy that doesn't forward

```text
a proxy that doesn't forward the header → the app's check reads a
different header → a different class.
```

## 16. The verified card's trap — the hop-by-hop's boundary

```text
the verified card's trap — the proxy strips its own header — a proxy
that doesn't → the hop-by-hop bypass fails → a different class.
```

## 17. The client-supplied's trap — the proxy strips the client header

```text
the client-supplied's trap — a proxy that strips a client-supplied
proxy header → the client-supplied header doesn't reach the app →
the client-supplied bypass fails → the hop-by-hop bypass is the vector.
```

## 18. The client-supplied's trap — the proxy verifies

```text
the client-supplied's trap — a proxy that verifies the header it added
→ a client-supplied header is rejected → the client-supplied bypass
fails → the hop-by-hop bypass is the vector.
```

## 19. The non-header check — the check's input

```text
the check's input — a trust check that reads a different input (a
session, a token, a signature) → the header isn't the check's input →
a different class.
```

## 20. The same parse — the normalization's trap

```text
the normalization's trap — a path the proxy and the app normalize the
same way → no confusion → a different class.
```

## 21. The stored copy — the cache-poisoning trap

```text
the cache-poisoning trap — a stored copy that serves YOUR input → a
cache-poisoning (a store) → not a parser-differential (a parse).
```

## 22. The desync — the request-smuggling trap

```text
the request-smuggling trap — a front-end and a back-end that parse the
request boundary differently → a request-smuggling (a desync) → not a
parser-differential (a parse).
```

## 23. The session check — the auth-session trap

```text
the auth-session trap — a trust check that reads a session / a token →
an auth-session → not a parser-differential.
```

## 24. The host check — the host-header trap

```text
the host-header trap — a trust check that reads a Host header → a
host-header → not a parser-differential.
```

## 25. The fetch — the ssrf trap

```text
the ssrf trap — a server-side fetch — the app fetches a URL the request
controls → an ssrf → not a parser-differential.
```

## 26. The read — the cors trap

```text
the cors trap — a cross-origin fetch — the app's bytes read → a cors →
not a parser-differential.
```

## 27. The false positive — the 200 on a non-gated route

```text
the false-positive trap — a 200 on a route that wasn't gated → a false
positive → a different class.
```

## 28. The non-proxy app — a different surface

```text
the non-proxy trap — an app that doesn't sit behind a proxy → no proxy
header → a different class.
```

## 29. The keyed header — a proxy that keys on the header

```text
the keyed-header trap — a proxy that keys on the header → a client-
supplied header changes the key → the client's own entry → a self-read
→ a different class.
```

## 30. The non-forwarded header — a proxy that doesn't forward

```text
the non-forwarded trap — a proxy that doesn't forward the header → the
app's check reads a different header → a different class.
```
