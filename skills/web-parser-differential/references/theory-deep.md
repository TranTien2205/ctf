# Theory deep — why parser differentials exist, and why they work

The mechanism — the front-end/back-end parse-mismatch model, exhaustively.

---

## 1. The model — two parsers that disagree

```text
a front-end (a proxy, a gateway, a WAF) parses the request one way;
a back-end (the app) parses it another — the same bytes, two different
interpretations — the disagreement is the vulnerability.
```

## 2. The parse-mismatch — the differential

```text
the parse-mismatch = a byte or a structure the front-end and the
back-end interpret differently:
- a header name (case, whitespace, a hop-by-hop control)
- a path normalization (encoding, traversal, a case difference)
- a content-length vs a transfer-encoding (a smuggling boundary)
- a structured field (a Host, a Forwarded, a Connection)
every difference is a differential — the app's check reads a
different value than the proxy's.
```

## 3. The hop-by-hop mechanics — the Connection-header strip

```text
the Connection header is a hop-by-hop control — a proxy strips the
headers it names before forwarding — a client-supplied Connection:
keep-alive, X-Real-IP strips the proxy's own X-Real-IP — the app
sees a request without the trusted header — a missing-header fallback.
```

## 4. The proxy-trust mechanics — the trusted header

```text
the app trusts the proxy's header — a missing header hits a fallback
— a client-supplied header is trusted — the app doesn't verify the
proxy actually added it — the trust check's input is the header's
value.
```

## 5. The normalization mechanics — a path the two parse differently

```text
a path the front-end normalizes one way and the back-end another —
a /static/../admin the proxy normalizes to /admin and the app routes
to /admin — a normalization differential — the front-end's check
reads a different path than the app's.
```

## 6. The trust-check's fallback — the missing-header case

```text
a missing proxy header → the app treats the request as local or
skips the trust check → a local request bypasses the authentication
or the restriction.
```

## 7. The trust-check's input — the client-supplied header

```text
a client-supplied proxy header → the app trusts it → the app doesn't
verify the proxy added it → the client-supplied header IS trusted.
```

## 8. The differential's scope — which checks are bypassed

```text
the differential bypasses a check the proxy's header gates — an
authenticated-only route, an internal route, a restricted endpoint —
the app's trust check reads the missing or client-supplied header's
effect.
```

## 9. The differential's falsifier — the boundary

```text
the attack fails if:
- the header isn't the trust check's input → a different class
- the proxy strips a client-supplied header → the client-supplied
  bypass fails → the hop-by-hop bypass is the remaining vector
- the proxy verifies the header it added → the client-supplied bypass
  fails → the hop-by-hop bypass is the remaining vector
- the proxy doesn't strip its own header → the hop-by-hop bypass fails
  → a different class
```

## 10. The class boundary — a parse-vs-store split

```text
a parser-differential is a PARSE difference — a front-end and a
back-end parse differently. a cache-poisoning is a STORE — a stored
copy serves YOUR input — no parse, a stored key-mismatch.
```

## 11. The proof — the differential confirm

```text
the differential confirm:
1. the front-end reads one value (the proxy's check)
2. the back-end reads another (the app's check)
3. the differential reaches a route the front-end's check gates
a two-request check — the proxy strips its own header → the app's
check reads the missing header's fallback.
```

## 12. The differential's class — the parse-vs-serve split

```text
a front-end that parses differently → a parser-differential (a parse).
a stored copy that serves YOUR input → a cache-poisoning (a store).
a fetch that reads bytes → web-cors (a real read).
a desync → a request-smuggling (a desync).
```
