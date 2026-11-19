# Common mistakes — the parser-differential traps that cost time

The mistakes that look like a bypass but aren't.

---

## 1. The reflection mistake — a client-supplied header that isn't trusted

```text
a client-supplied header reflected in the response but not trusted —
the app echoes it but doesn't use it for the trust check — a
reflection, not a trust bypass.
```

## 2. The MISS mistake — a reflection, not a parse

```text
a client-supplied header reflected on a MISS — the response came
from the origin — a REFLECTION, not a parse differential — a different
class.
```

## 3. The keyed-header mistake — a proxy that strips a client header

```text
a proxy that strips a client-supplied proxy header → the client-
supplied header doesn't reach the app → the client-supplied bypass
fails → the hop-by-hop bypass is the remaining vector.
```

## 4. The verified-header mistake — a proxy that verifies

```text
a proxy that verifies the header it added → a client-supplied header
is rejected → the client-supplied bypass fails → the hop-by-hop
bypass is the remaining vector.
```

## 5. The non-header mistake — a trust check that reads a different input

```text
the card's falsifier: 'both forms are rejected, so the trust check
does not depend on that header' — the header isn't the trust check's
input → a different class.
```

## 6. The no-proxy mistake — no front-end in the path

```text
no reverse proxy in the path → no proxy header to abuse → a different
class.
```

## 7. The no-fallback mistake — no missing-header fallback

```text
an app that requires the proxy header → a missing header → a 400/401
→ no missing-header fallback → the hop-by-hop bypass fails → a
different class.
```

## 8. The no-strip mistake — a proxy that doesn't strip

```text
a proxy that doesn't honor Connection's strip → the header passes
through → the app's check reads it → the hop-by-hop bypass fails →
a different class.
```

## 9. The cache-confusion mistake — a stored copy, not a parse

```text
a stored copy that serves YOUR input → a cache-poisoning (a store),
not a parser-differential (a parse).
```

## 10. The smuggling-confusion mistake — a desync, not a parse

```text
a desync front-end/back-end → a request-smuggling (a desync), not a
parser-differential (a parse).
```

## 11. The host-confusion mistake — a Host rewrite, not a trust check

```text
a client-supplied Host → a Host rewrite (a URL-rewrite), not a trust
check — a different surface.
```

## 12. The per-vector mistake — a wrong-vector probe

```text
a local-vs-remote check probed with a host header → a wrong-vector
probe → a different input needed.
```

## 13. The reach mistake — a bypass without reach

```text
a differential that doesn't reach a gated route → a wrong-context
case → the bypass's reach is the gated route.
```

## 14. The per-mistake map — which mistake for which surface

```text
a client-supplied header not trusted → a reflection, not a trust bypass
a stored copy                      → a cache-poisoning, not a parse
a desync                          → a request-smuggling, not a parse
a keyed header                    → a proxy strips a client header →
                                    the hop-by-hop bypass is the vector
a verified header                 → a proxy verifies → the hop-by-hop
                                    bypass is the vector
a non-header check                → a different class
no proxy                          → no proxy header → a different class
no fallback                       → no missing-header fallback → a
                                    different class
a proxy that doesn't strip        → a different class
```
