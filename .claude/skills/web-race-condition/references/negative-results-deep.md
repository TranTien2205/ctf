# Negative results deep — the exhaustive kill-map for a closed window

Every falsifier shape, the measurement that proves it, and the precondition
that reopens it. Write each one — the kill map is the deliverable.

---

## 1. The negative taxonomy

A **recorded negative** is a proven-closed layer. Three shapes:

| Shape | What it is |
|---|---|
| static falsifier | a defence visible in source (lock/constraint/atomic) |
| empirical falsifier | a real-overlap run where the defence held |
| structural falsifier | the layer can't overlap (single worker + private DB) |

None is `inconclusive` — an inconclusive run proved nothing and records
nothing.

## 2. Static falsifiers — visible in source

### 2a. Atomic statement

```text
endpoint:   POST /api/withdraw
falsifier:  UPDATE a SET bal=bal-? WHERE id=? AND bal>=? + rowcount gate  (a.py:88)
measure:    source read — the predicate is inside the UPDATE
reopen-if:  the predicate moves to app code, or the rowcount check is dropped
```

### 2b. Row lock

```text
endpoint:   POST /api/book
falsifier:  SELECT ... FOR UPDATE on the seat row  (book.py:55)
measure:    loser latency +180ms (blocked), one booking only
reopen-if:  the FOR UPDATE is removed or the lock scope shrinks to after-write
```

### 2c. Constraint

```text
endpoint:   POST /api/register
falsifier:  UNIQUE(email) — second INSERT raises IntegrityError  (schema.sql:12)
measure:    raced → [201, 500(constraint)×N] — the 500s are the constraint
reopen-if:  the index is dropped
```

### 2d. SERIALIZABLE + retry

```text
endpoint:   POST /api/transfer
falsifier:  SERIALIZABLE + app retry — loser gets 40001, retries, declines correctly
measure:    serialization failure on the loser + correct retry
reopen-if:  the retry is removed (then it's a 500-DoS, still not a bypass)
```

### 2e. Datastore-atomic

```text
endpoint:   POST /api/claim
falsifier:  db.codes.updateOne({code,used:false},{used:true}) — matchedCount=0 for loser
measure:    one claim only
reopen-if:  the predicate leaves the filter
```

### 2f. Optimistic version

```text
endpoint:   POST /api/profile
falsifier:  UPDATE ... WHERE version=? — loser's update affects 0 rows (model.py:31)
measure:    OptimisticLockException / stale-object on the loser
reopen-if:  the version check is dropped
```

## 3. Empirical falsifiers — the defence held under real overlap

```text
endpoint:   POST /api/vote
falsifier:  no visible lock, but 3 real-overlap runs → clean losers, no cross
measure:    concurrency 20, max_in_flight 20 → [200, 4xx×19] ×3 — a defence held
reopen-if:  the hidden index/lock is removed, or the check moves to app code
```

The empirical falsifier is the *recorded negative* — you didn't see the
defence but it held under real overlap.

## 4. Structural falsifiers — the layer can't overlap

### 4a. Single worker + private DB

```text
scope:      whole HTTP layer
falsifier:  gunicorn workers=1, sqlite file-lock — no parallel handlers
measure:    slow endpoint takes 2× delay serially
reopen-if:  the worker count rises, or a second replica shares the DB
```

The caveat: this closes the *HTTP* layer only. A shared-DB or background-
worker layer may still be open — record which layer.

### 4b. Queue-serialized

```text
scope:      the job layer
falsifier:  SELECT ... FOR UPDATE SKIP LOCKED — each job claimed once
measure:    jobs run serially; a second trigger deduplicated
reopen-if:  SKIP LOCKED dropped, or a second consumer added without it
```

## 5. What is NOT a negative

- **`max_in_flight` = 1** → inconclusive — fix delivery, re-roll.
- **a timeout/reset on a slot** → unknown — discard, re-roll.
- **a `429`-throttled burst** → the limiter blocked delivery, not the window —
  race the limiter.
- **a `401`/`403` credential** → the credential is consumed — race the issuer.
- **endpoint not found** → not tested at all.

## 6. The negative → next-action table

| Negative | Next action |
|---|---|
| one endpoint falsified | another endpoint in the inventory |
| all writable endpoints falsified | another boundary — DB layer, worker, flow |
| all boundaries falsified | the class is exhausted — reclassify |
| the HTTP layer closed | the DB/worker layer may still be open |
| a layer closed, another open | the open layer is the new hypothesis |

## 7. Where the record goes

```bash
# the ledger — the mechanism-level negative
python3 tools/state.py <name> --note "redeem: atomic UPDATE rowcount, raced 3×, falsifier"

# the challenge kill-map — for a worked-but-unsolved challenge
#   → knowledge/attempts/<name>.json — layer + measurement + reopen-if
```

`knowledge/attempts/` is the kill map: every layer measured dead, with the
measurement and the reopen precondition — the next attempt starts from the
kill map, not zero.

## 8. The discipline rule

**A negative you didn't record is a budget you'll spend twice.** Every
falsifier, every clean real-overlap no-cross, every closed layer goes to the
ledger — the next run starts from the kill map, not from zero.

## 9. The kill-map entry shape

```json
{
  "endpoint": "POST /api/redeem",
  "window": "SELECT used → grant → UPDATE used=1",
  "falsifier": "UPDATE codes SET used=1 WHERE code=? AND used=0 (atomic, rowcount-gated)",
  "measurement": "raced 3× at concurrency 20, max_in_flight 20 → [200,409×19], one grant",
  "reopen_if": "the rowcount gate or the used=0 predicate is removed",
  "verified_at": "run 3, baseline [200,409,409,409]"
}
```
