# Troubleshoot deep — every failure to run or to read, exhaustively

The full diagnostic tree. Symptom → the layers to check in order → the fix.

---

## 1. The mechanics layer — the requests never overlapped

### `max_in_flight` = 1, always

```text
check 1: is the server parallel?        → 2×slow-endpoint timing = 1 worker → race the DB layer
check 2: is the client multiplexing?    → one connection — use --concurrency (N conns)
check 3: is a per-conn lock serializing? → vary nothing; the lock is per-conn — 1 req/conn
```

### `max_in_flight` < requested

```text
check 1: barrier-timeout fired early    → raise --barrier-timeout
check 2: worker pool < concurrency      → set --concurrency = worker count
check 3: network couldn't prime all     → lower --concurrency, or a closer client
```

### The burst misses the window every time

```text
the window is narrower than the burst start-spread:
  → burst → interleave (last-byte stall, --url-b)
  → widen the check (pathological input)
  → single-packet delivery (the tool's barrier is this)
```

## 2. The throttle layer — the requests never reached the handler

### `429`/`403` dominant

```text
a rate limiter or a per-request gate rejects the flood:
  → race the limiter (it's a counter itself)
  → stay under the limit with a tighter interleave
  → a consumed CSRF/origin token → race the token-issuer, or a flow that accepts it
```

### `401`/`403` on the raced request only

```text
a per-request credential is stale/consumed by the burst:
  → the credential is single-use → race the issuer, or use a burst-valid token
```

## 3. The interpretation layer — the run ran but reads wrong

### Two `200`s, no doubled state

```text
a response cache / polite dedup — the second 200 is a replay:
  → GET the state — no doubled effect = falsifier (replay), not a win
```

### The "win" appears in baseline

```text
the signature is normal behavior:
  → recalibrate — the crossed STATE is the proof, not the status
```

### All-loser shape under real overlap

```text
the defence held:
  → 3 clean real-overlap runs, no cross → falsifier — record it
  → check for a lock/constraint you missed in source
```

### A `500`/`IntegrityError` on the loser

```text
a constraint firing — the defence working:
  → record as falsifier (the constraint caught the loser), not a crash
```

## 4. The state layer — the effect can't be read

### Can't see the doubled effect

```text
check 1: wrong endpoint for the state   → the balance is /api/account, not the redeem response
check 2: the effect is elsewhere        → the token-cross is in the MAILBOX, not the response
check 3: the effect is deferred         → a counter a periodic job reads — wait for the tick
```

### The effect is there but won't unlock the gate

```text
the primitive doesn't pay:
  → map primitive → gate → flag BEFORE racing — a race that buys nothing is no impact
  → a different primitive (money→buy, token→ATO, identity→deputy)
```

## 5. The target layer — the endpoint isn't what you think

### The endpoint is defended

```text
re-grep for the defence you missed:
  → FOR UPDATE / select_for_update / PESSIMISTIC
  → atomic UPDATE ... WHERE / updateMany / findOneAndUpdate / ConditionExpression
  → UNIQUE / CHECK / PRIMARY KEY
  → SERIALIZABLE + retry
```

### The endpoint isn't a race target

```text
a read-only GET, a blind insert, a per-request value:
  → no shared state / no check / no separated use → not a race — reclassify
```

### The race is on a shared instance

```text
a one-shot / consumable target already used:
  → the SSOS rule — consumed is unrecoverable; confirm freshness FIRST
```

## 6. The delivery layer — the tool can't do the mechanic

### The interleave needs a manual stall

```text
--url-b fires two complete requests; the cross needs A held mid-request:
  → raw-socket stall — withhold A's last body byte, complete B, release A
  → see delivery-mechanics.md §1
```

### HTTP/2 specifics

```text
the requests are frames — the last-DATA-frame order decides the commit:
  → withhold each stream's last DATA frame, flush all at once (the h2 stall)
  → race_probe's barrier does the single-packet form
```

## 7. The reset layer — re-rolls aren't clean

### Run N starts where N-1 ended

```text
no reset between rolls — the resource is already consumed:
  → --reset-url / --reset-body restores the starting S
  → a fresh code / reset balance per roll
```

## 8. The environment layer

### The client is too far / too slow

```text
network latency > window width:
  → a closer client (a box near the target)
  → widen the window (pathological input)
```

### The signature-mode reads nothing

```text
the difference isn't in status:
  → raw-body / normalized-body / regex / signature-header / signature-bytes
```

## 9. The decision tree

```text
raced run produced nothing?
├─ max_in_flight = 1          → §1 mechanics — fix delivery
├─ 429/403 dominant           → §2 throttle — race limiter or interleave
├─ 401/403 on raced only      → §2 credential — race issuer or valid token
├─ ran, but no doubled state  → §3 interpretation — state, not status
├─ effect there, gate won't   → §4 the primitive doesn't pay
├─ real overlap, all-loser    → §5 falsifier — record it
├─ IntegrityError on loser    → §5 constraint — falsifier
├─ endpoint read-only         → §5 not a race target — reclassify
├─ --url-b won't stall        → §6 raw-socket stall
├─ run N starts dirty         → §7 --reset-url
├─ client too far             → §8 closer box or widen
└─ signature reads nothing    → §8 signature-mode
```
