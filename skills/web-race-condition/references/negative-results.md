# Negative results — recording the closed window so the next run doesn't re-walk it

A recorded negative is a deliverable: it names the endpoint, the defence that
held, and the precondition that would reopen it. Write it; don't silently
drop it.

---

## 1. What counts as a negative

A **negative** is a real-overlap run where the defence held — `max_in_flight`
≥ 2, clean losers, no crossed state. It is *not* a failed-to-overlap run (that
is `inconclusive` and means nothing).

| Verdict | Criteria |
|---|---|
| confirms | serial-impossible state, attributed |
| negative / falsifier | real overlap, defence held, no cross — repeatable |
| inconclusive | `max_in_flight` = 1, or a timeout — never a result |

## 2. The negative record template

```text
endpoint:    POST /api/redeem
window:      SELECT used → grant → UPDATE used=1     (app.py:210)
falsifier:   UPDATE codes SET used=1 WHERE code=? AND used=0 — rowcount gate (app.py:214)
baseline:    [200, 409, 409, 409]
raced:       concurrency 20, max_in_flight 20 → [200, 409×19] — no cross, 3 clean rolls
state:       one grant only
verdict:     falsifier — atomic update closes the window
reopen-if:   the rowcount check is removed, or the predicate is moved out of the WHERE
```

The `reopen-if` is the kill-map line — the condition under which the negative
stops being a negative.

## 3. The negative categories

### 3a. Atomic statement — the code already closes it

```text
POST /api/withdraw
falsifier: UPDATE a SET bal=bal-? WHERE id=? AND bal>=? — rowcount decides (a.py:88)
raced: max_in_flight 15 → [200, 409×14]; balance never negative
```

### 3b. Row lock — `FOR UPDATE`

```text
POST /api/book
falsifier: SELECT ... FOR UPDATE on the seat row (book.py:55)
raced: loser latency +180ms (blocked); one booking only
```

### 3c. Constraint — the DB rejects the loser

```text
POST /api/register
falsifier: UNIQUE(email) — the second INSERT raises IntegrityError (schema.sql:12)
raced: [201, 500(constraint)×N] — the 500s are the constraint firing, not a win
```

The `500`/`IntegrityError` on the loser is the constraint doing its job —
record it as a falsifier, not a crash.

### 3d. SERIALIZABLE + retry — the DB aborts the loser

```text
POST /api/transfer
falsifier: SERIALIZABLE + retry — the loser gets 40001, retries, sees committed state
raced: one transfer committed; loser's retry declined correctly
```

### 3e. Datastore-atomic — Mongo/Dynamo/Redis conditional

```text
POST /api/claim
falsifier: db.codes.updateOne({code,used:false},{used:true}) — matchedCount=0 for the loser
raced: one claim only
```

### 3f. Single worker + private DB — truly no parallel surface

```text
whole app
falsifier: gunicorn workers=1, sqlite file-lock — no parallel HTTP, and the DB serializes
probe: slow endpoint takes 2× delay serially
```

Note the caveat: this closes HTTP races. A shared-DB or background-worker
layer might still be open — record which layer you closed.

### 3g. Defence held under real overlap — the empirical negative

```text
POST /api/vote
falsifier: no visible lock, but 3 real-overlap runs → clean losers, no cross
raced: max_in_flight 20, [200, 4xx×19] ×3 — a defence (likely a unique index) held
reopen-if: the index is dropped or the check moves into app code
```

## 4. What is NOT a negative

- **`max_in_flight` = 1** → inconclusive — fix delivery and re-roll.
- **a timeout / reset on a slot** → unknown — discard and re-roll.
- **the burst was throttled (429s)** → the limiter blocked delivery, not the
  window — race the limiter or interleave.
- **you didn't find the endpoint** → not tested at all.

An inconclusive run recorded as a negative is a false closure — the next agent
trusts it and skips a winnable endpoint.

## 5. Where the record goes

```bash
# the ledger — the mechanism-level negative
python3 tools/state.py <name> --note "redeem: atomic UPDATE rowcount, raced 3×, falsifier" 
# the challenge kill-map — for a worked-but-unsolved challenge
#   → knowledge/attempts/<name>.json — the layer + measurement + reopen-if
```

`knowledge/attempts/` is the kill map: every layer measured dead, with the
measurement and the precondition that reopens it — so the next attempt
doesn't re-walk a closed layer.

## 6. The negative → next-action table

| Negative recorded | Next |
|---|---|
| one endpoint falsified | another endpoint in the inventory |
| all writable endpoints falsified | another boundary (DB layer, worker, flow) |
| all boundaries falsified | the class is exhausted — reclassify |
| a layer closed but another open | the open layer is the new hypothesis |

## 7. The discipline rule

**A negative you didn't record is a budget you'll spend twice.** Every
falsifier, every clean real-overlap no-cross, every closed layer gets written
to the ledger — the next run starts from the kill map, not from zero.
