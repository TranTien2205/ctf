# Class boundary deep — parser-differential vs the neighbors, exhaustively

The boundary map — when it's this class, when it's a neighbor.

---

## 1. The boundary — a front-end/back-end parse-mismatch

```text
a parser-differential is a front-end/back-end PARSE mismatch — a byte
or a structure the front-end and the back-end interpret differently —
the disagreement is the vulnerability.
```

## 2. vs request-smuggling — a desync vs a parse

```text
a parser-differential   → a front-end and a back-end parse differently —
                        a header's trust, a path's normalization, a
                        client-supplied header.
a request-smuggling     → a front-end and a back-end parse the request
                        BOUNDARY differently — a content-length vs a
                        transfer-encoding — a desync.
the boundary            → a parse-vs-desync split — a parser-differential
                        is a parse; a request-smuggling is a desync.
```

## 3. vs cache-poisoning — a parse vs a store

```text
a parser-differential   → a front-end and a back-end parse differently —
                        a header's trust, a path's normalization, a
                        client-supplied header.
a cache-poisoning       → a stored copy that serves YOUR input — a
                        key-mismatch — a store.
the boundary            → a parse-vs-store split — a parser-differential
                        is a parse; a cache-poisoning is a store.
```

## 4. vs auth-session — a header check vs a session check

```text
a parser-differential   → a trust check reads a proxy header — a
                        client-supplied or a missing header's fallback.
an auth-session         → a trust check reads a session / a token — a
                        cookie, a JWT, a signature.
the boundary            → a header-vs-session split — a parser-differential
                        reads a proxy header; an auth-session reads a
                        session token.
```

## 5. vs host-header — a proxy-header vs a host-header

```text
a parser-differential   → a proxy-header trust — a client-supplied or
                        a missing proxy header's fallback.
a host-header           → a Host-header injection — a forged host → a
                        route-confusion, a password-reset link, an
                        absolute-URL rewrite.
the boundary            → a proxy-vs-host split — a parser-differential
                        is a proxy-header; a host-header is the Host.
```

## 6. vs ssrf — a trust check vs a fetch

```text
a parser-differential   → a trust check reads a proxy header — a
                        client-supplied or a missing header's fallback.
an ssrf                 → a server-side fetch — the app fetches a URL
                        the request controls.
the boundary            → a check-vs-fetch split — a parser-differential
                        is a trust check; an ssrf is a fetch.
```

## 7. vs cors — a parse vs a read

```text
a parser-differential   → a front-end and a back-end parse differently —
                        a header's trust, a path's normalization, a
                        client-supplied header.
a cors                  → a cross-origin fetch — the app's bytes read —
                        a real read.
the boundary            → a parse-vs-read split — a parser-differential
                        is a parse; a cors is a real read.
```

## 8. vs cache-poisoning — the confusable sibling

```text
a parser-differential   → a front-end and a back-end parse differently —
                        a header's trust, a path's normalization, a
                        client-supplied header.
a cache-poisoning       → a stored copy that serves YOUR input — a
                        key-mismatch — a store.
the boundary            → a parse-vs-store split — the verified card's
                        own chain pairs a hop-by-hop bypass (a parse)
                        with a cache-overflow (a store) — the two are
                        the sibling pair.
```

## 9. The boundary's falsifier — when it's not this class

```text
a non-header check → a different class
a proxy that doesn't strip its own header → the hop-by-hop bypass fails
a proxy that strips a client-supplied header → the client-supplied
  bypass fails → the hop-by-hop bypass is the vector
a stored copy → a cache-poisoning
a desync → a request-smuggling
a session check → an auth-session
a host check → a host-header
a fetch → an ssrf
a read → a cors
```

## 10. The boundary's scope — which checks are bypassed

```text
the differential bypasses a check the proxy's header gates — an
authenticated-only route, an internal route, a restricted endpoint —
the app's trust check reads the missing or client-supplied header's
effect.
```
