# Sequence and time — the ordering-assumption mechanisms

`mechanism-alphabet.md` lists sequence and time among the 13. This
module is their shared internals — both are ordering assumptions the
server failed to enforce.

## Sequence — the monotonicity assumption

Code assumes IDs/nonces/versions only move forward:

```js
// vulnerable — accepts any nonce
if (req.body.nonce) apply(req.body.nonce);
// safe — tracked strictly-increasing
if (nonce <= lastSeen[user]) return 409;
lastSeen[user] = nonce;
```

### The probes

| Probe | Tests |
|---|---|
| `nonce=<last-1>` | stale accepted? |
| `nonce=<last>` | replay accepted? |
| `nonce=<last+100>` | gap accepted — and does it lock the middle? |
| `id=0`, `id=-1`, `id=MAX` | boundary forms — the zeroth record, the wrap |
| `version=<older>` | state rewind — restore a previous object's version |
| `sequence` out of order | batch/parallel acceptance |

### The evidence

A stale value accepted into a new state: `{"sequence":1}` applied where
`lastSeen` was `5` — the verbatim pair `applied:true` + the known-stale
value. Or an older `version` restoring a previous object's state —
`{"version":3}` overwriting `version:5`'s changes.

### The rewind variant

Versioned objects: `POST /doc {"version":3, "content":"x"}` — the
server applies the older version's change over `version:5`'s state —
a last-write-wins where the clock is client-supplied. The "stale write"
shape is the sequence mechanism on document state.

## Time — the chronology assumption

Code trusts client-reachable time fields, or compares time wrong:

```js
// vulnerable — client-supplied expiry
if (req.body.expiry > Date.now()) grant(...);
// vulnerable — clock compared on the wrong side
if (token.expiry < Date.now()) grant(...);   // inverted
// safe — server minted, server checked
if (token.expiry > serverTime()) ...
```

### The probes

| Probe | Tests |
|---|---|
| `expiry=<now-1>` | expired accepted |
| `expiry=<now>` | inclusive vs exclusive boundary |
| `expiry=<now+100y>` | unbounded future |
| `notBefore=<now-1>` | token valid before window |
| `createdAt=<epoch>` | age computed negative |
| `timestamp=4294967296` | uint32 epoch wrap → 1970 |
| `expiry=2038-01-20` | signed-int32 post-2038 wrap |
| `expiry="NaN"` / `"Infinity"` | comparison-false propagation |

### The evidence

An expired/stale value accepted: `{"expiry":"2020-01-01","valid":true}` —
the impossible pair (past date + valid) is the verbatim class evidence.

### The timezone/locale variants

`expiry` parsed in a different timezone than it's compared — `Z` vs
local-time interpretation. DST gaps where a wall time doesn't exist —
the parser rejecting, shifting, or crashing. `expiry` in seconds vs
milliseconds (`1699999999` vs `1699999999000`) — a unit confusion on
time.

## The shared falsifier

- Sequence: `409`/`400` on stale/replayed values — ordering enforced.
- Time: `400` on past/future values — server-side time validation.

The falsifier per FIELD: `expiry` validated says nothing about
`notBefore`, `createdAt`, `version` — each is its own layer.

## The composition

Sequence + replay: a stale `nonce` on a replayed `redeem` — two edges,
one request. Time + trust: an `expiry` the client mints — the
carried-value mechanism with a time payload. The alphabets stack the
same way the chains do.
