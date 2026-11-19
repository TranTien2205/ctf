# Verified chains — the parser-differential case, end to end

The one verified card's mechanics, grounded.

---

## The HTB NovaCore card — the hop-by-hop cache-overflow DOM-clobber polyglot-RCE

### The setup — the chain's surface

```text
a Flask app behind a Traefik proxy — a token_required check on an
authenticated-only route — a custom cache daemon with a fixed-size
buffer — a CSP nonce + a DOM-clobber + a prototype-pollution + a
polyglot exfil. the chain: a hop-by-hop bypass → a cache-overflow →
a DOM-clobber prototype-pollution → a polyglot exfil → the flag.
```

### The card's signals — the classification vocabulary

```text
'traefik', 'x-real-ip', 'hop-by-hop', 'connection header',
'token_required', 'strcpy', 'csp', 'nonce', 'dom clobbering',
'prototype pollution', 'eval', 'exiftool', 'polyglot', 'plugin' —
the classifier's vocabulary for this shape.
```

### The first probe — the card's own

```bash
# the card's first_confirming_probe — the hop-by-hop bypass
curl "$BASE/api/restricted"   # the normal request — the proxy's X-Real-IP present
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Real-IP'   # the proxy strips X-Real-IP
#   the second request reaches the app without X-Real-IP → a 200 vs a 401
```

```text
the card's probe: 'send the same authenticated-only request twice,
once normally and once with the proxy header named in the Connection
header'.
falsifier: 'both forms are rejected, so the trust check does not
depend on that header'.
```

### The mechanism — the hop-by-hop bypass

```text
the Connection header is a hop-by-hop control — Traefik strips the
headers it names before forwarding — naming X-Real-IP in Connection
strips it → the app sees a request without X-Real-IP → the app treats
a missing-header request as local → the token_required check skipped.
```

### The chain — the differential + the downstream

```text
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

### The preconditions — the card's reach

```text
the card's preconditions:
- 'a reverse proxy adds a header the application trusts' — the
  X-Real-IP trust
- 'a missing header is treated as a local request' — the fallback
- 'a custom daemon copies request data into a fixed-size buffer' —
  the cache-overflow surface
- 'the recorded solver needs a trade_id that already exists: POST
  /api/copy_signal_trade with a uuid from GET /api/active_signals
  mints one and answers {"message":"Trade copied successfully",
  "trade_id":"<uuid>"}' — the trade_id the cache-overflow stage needs
```

### The blast radius — the card's trap note

```text
the card's blast_radius note — a shared instance — the differential's
reach is the gated route — the cache-overflow's write is a shared
record — use a disposable record.
```

### The falsifier — when the card doesn't apply

```text
the card's falsifier: 'both forms are rejected, so the trust check
does not depend on that header' — the header isn't the trust check's
input → a different class.
```

### The evidence — what the card required

```text
the card's evidence: the second request reaches the app without the
proxy's header — a 200 vs a 401 — the missing-header fallback treats
the request as local — the trust check bypassed.
```

### The per-step probe map — how to run the card

```text
step 1 — run the card's first_confirming_probe — the hop-by-hop bypass
step 2 — the restricted route — the token_required check bypassed
step 3 — the cache-overflow — the strcpy overflow
step 4 — the DOM-clobber prototype-pollution — the eval chain
step 5 — the polyglot exfil — the flag
```

### The per-step falsifier — when to move

```text
step 1 — a proxy that doesn't strip its own header → a different class
step 2 — a non-header check → a different class
step 3 — no cache-overflow surface → a different chain
step 4 — no DOM-clobber surface → a different chain
```

### The card's use — run the card's probe first

```text
a chain card match → run the card's first_confirming_probe first —
the card carries the traps that cost time the first time — the probe
is the cheapest confirm — a confirmed card is a solved challenge.
```
