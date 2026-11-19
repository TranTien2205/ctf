# Troubleshoot — why the parser-differential probe returned nothing

The failure modes and the re-probe for each.

---

## 1. The non-header mistake — a trust check that reads a different input

```text
the trust check doesn't read the proxy header — a session, a token,
a signature — the header isn't the check's input → a different class.
re-probe: the app's actual check — a session, a token.
```

## 2. The keyed-header mistake — a proxy that strips a client header

```text
a proxy that strips a client-supplied proxy header → the client-
supplied header doesn't reach the app → the client-supplied bypass
fails.
re-probe: the hop-by-hop bypass — naming the proxy's own header in
Connection.
```

## 3. The verified-header mistake — a proxy that verifies

```text
a proxy that verifies the header it added → a client-supplied header
is rejected → the client-supplied bypass fails.
re-probe: the hop-by-hop bypass — the proxy strips its own header.
```

## 4. The no-strip mistake — a proxy that doesn't strip

```text
a proxy that doesn't honor Connection's strip → the header passes
through → the app's check reads it → the hop-by-hop bypass fails.
re-probe: a different unkeyed input, or a different class.
```

## 5. The no-fallback mistake — no missing-header fallback

```text
an app that requires the proxy header → a missing header → a 400/401
→ no missing-header fallback → the hop-by-hop bypass fails.
re-probe: a different header, or a client-supplied bypass.
```

## 6. The no-proxy mistake — no front-end in the path

```text
no reverse proxy in the path → no proxy header to abuse → a different
class.
re-probe: the app's actual check — a session, a token.
```

## 7. The reflection mistake — a client-supplied header that isn't trusted

```text
a client-supplied header reflected but not trusted — the app echoes
it but doesn't use it for the trust check → a reflection, not a
trust bypass.
re-probe: the trust check's actual input — a different header.
```

## 8. The reach mistake — a bypass without reach

```text
a differential that doesn't reach a gated route → a wrong-context
case → the bypass's reach is the gated route.
re-probe: a different gated route, or a different vector.
```

## 9. The cache-confusion mistake — a stored copy, not a parse

```text
a stored copy that serves YOUR input → a cache-poisoning (a store),
not a parser-differential (a parse).
re-probe: the cache-poisoning class — a stored-copy probe.
```

## 10. The smuggling-confusion mistake — a desync, not a parse

```text
a desync front-end/back-end → a request-smuggling (a desync), not a
parser-differential (a parse).
re-probe: the request-smuggling class — a CL/TE probe.
```

## 11. The per-vector mistake — a wrong-vector probe

```text
a local-vs-remote check probed with a host header → a wrong-vector
probe → a different input needed.
re-probe: a spoofed-IP header (X-Real-IP, X-Forwarded-For).
```

## 12. The falsifier check — is the surface dead

```text
the card's falsifier: 'both forms are rejected, so the trust check
does not depend on that header' — the header isn't the trust check's
input → a different class.
a proxy that strips a client-supplied header → the client-supplied
bypass fails → the hop-by-hop bypass is the remaining vector.
a proxy that doesn't strip its own header → the hop-by-hop bypass
fails → a different class.
```
