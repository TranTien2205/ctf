# Evidence rules — what a parser-differential proof requires

The complete evidence standard — the differential confirm.

---

## 1. The proof standard — the differential confirm

```text
the differential confirm requires:
1. the front-end reads one value (the proxy's check)
2. the back-end reads another (the app's check)
3. the differential reaches a route the front-end's check gates
a two-request check — the proxy strips its own header → the app's
check reads the missing header's fallback.
```

## 2. The stored-vs-parse boundary — the class distinction

```text
a parser-differential is a PARSE difference — a front-end and a
back-end parse differently. a cache-poisoning is a STORE — a stored
copy serves YOUR input — no parse, a stored key-mismatch.
```

## 3. The hop-by-hop confirm — the proxy-strip serve

```bash
# the two-request check — the proxy strips its own header
curl "$BASE/api/restricted"   # the normal request — the proxy's header present
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Real-IP'   # the proxy strips X-Real-IP
#   the second request reaches the app without X-Real-IP → a 200 vs a 401
```

```text
the confirm: the second request reaches the app's missing-header
fallback — a local request — the trust check bypassed.
```

## 4. The client-supplied confirm — the forged-header check

```bash
# does the app trust a client-supplied proxy header
curl "$BASE/api/restricted" -H 'X-Real-IP: 127.0.0.1'   # a client-supplied X-Real-IP
#   a 200 → the app trusts the client-supplied header → the check's input
```

## 5. The reach confirm — the gated route

```bash
# the differential reaches a route the proxy's header gates
curl "$BASE/api/admin" -H 'Connection: keep-alive, X-Real-IP'   # the proxy strips X-Real-IP
#   a 200 on the gated route → the differential reached it
```

## 6. The MISS-vs-HIT distinction — a reflection vs a parse

```text
a proxy-differential is a PARSE — the app's check reads a different
value — a live difference, not a stored copy.
a cache-poisoning is a STORE — a stored copy serves YOUR input — a
shared store, not a parse.
```

## 7. The falsifier — when the surface is dead

```text
the card's falsifier: 'both forms are rejected, so the trust check
does not depend on that header' — the header isn't the trust check's
input → a different class.
a proxy that strips a client-supplied header → the client-supplied
bypass fails → the hop-by-hop bypass is the remaining vector.
a proxy that doesn't strip its own header → the hop-by-hop bypass
fails → a different class.
```

## 8. The evidence's ledger — what to record

```bash
python3 tools/state.py <c> --hypothesis \
  "parser-diff-evidence: header=<proxy-header> — fallback=<missing-header> — reach=<gated-route>"
```

## 9. The evidence's falsifier — a non-header check

```text
a trust check that reads a different input (a session, a token, a
signature) → the header isn't the check's input → a different class.
```

## 10. The evidence's edge — a verified header

```text
a proxy that verifies the header it added → a client-supplied header
is rejected → the client-supplied bypass fails → the hop-by-hop
bypass is the remaining vector.
```
