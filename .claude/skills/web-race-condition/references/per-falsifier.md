# Per-falsifier — the defence that closes each window

The complete falsifier reference: for each check letter and each mechanism,
the exact defence that closes the window — and the grep that confirms it.

---

## The falsifier index

| The window | The falsifier | The grep |
|---|---|---|
| A uniqueness | `UNIQUE(email)`/`ON CONFLICT`/SERIALIZABLE | `UNIQUE.*email\|ON CONFLICT\|insert.*unique` |
| B balance | `UPDATE ... WHERE bal>=amt` + rowcount / `FOR UPDATE` | `WHERE.*balance.*>=\|FOR UPDATE\|select_for_update` |
| C single-use | `UPDATE ... WHERE used=0` + rowcount / `FOR UPDATE` | `WHERE.*used.*=\|FOR UPDATE` |
| D limit | `UNIQUE(u,t)` / `UPDATE ... WHERE count<max` + rowcount | `UNIQUE.*\|WHERE.*count.*<\|rate.*limit` |
| F file-create | `O_EXCL`/`UNIQUE(name)`/atomic open | `O_EXCL\|UNIQUE.*name\|open.*['\"]x['\"]` |
| G claim-once | `UPDATE ... WHERE claimed=0` + rowcount | `WHERE.*claimed.*=\|FOR UPDATE` |
| H inventory | `UPDATE ... WHERE stock>0` + rowcount / `UNIQUE(seat)` | `WHERE.*stock.*>\|UNIQUE.*seat` |
| L limit-counter | `UPDATE ... WHERE attempts<cap` + rowcount / token-bucket | `WHERE.*attempts.*<\|token_bucket\|leaky` |
| S session | `UNIQUE(user)`/atomic rotate txn | `UNIQUE.*user\|DELETE.*INSERT\|rotate` |
| V trusted-view | re-read inside the action txn / version | `version\|row_version\|lock_version` |
| the flow | recompute at the charged step / step lock | `recompute\|recalculate\|step_lock` |
| the worker claim | `FOR UPDATE SKIP LOCKED`/`INSERT ... ON CONFLICT` | `SKIP LOCKED\|ON CONFLICT.*DO NOTHING` |
| the idempotency key | `UNIQUE(key)`/`ON CONFLICT` | `Idempotency.*Key\|UNIQUE.*key` |
| the lock/semaphore | real lock scoped check→act | `pg_advisory\|GET_LOCK\|redlock\|mutex` |
| the version | the `UPDATE ... WHERE version` as the only write | `WHERE.*version.*=` |

## The per-falsifier detail

### `UPDATE ... WHERE <pred>` + rowcount — the atomic close

The single-statement close: the check *and* the write are one atomic
statement — `UPDATE accounts SET balance = balance - 100 WHERE id=1 AND
balance >= 100`. The `WHERE` runs *inside* the row lock; a second concurrent
`UPDATE` re-reads the *updated* balance. The rowcount is the `409` — a `0`
rowcount means the check failed.

```text
UPDATE ... WHERE balance >= amt  → rowcount=1: committed, rowcount=0: 409
```

**The grep** — `WHERE.*(balance|stock|used|claimed|attempts|count).*(>=|<=|<|>|=)`
on the UPDATE — and a `rowcount`/`affected`/`affected_rows` check.

**Not this** — `SELECT` → `if` → `UPDATE` (the check is a separate read) is
*not* the atomic close; the `WHERE` is absent.

### `SELECT ... FOR UPDATE` / `select_for_update` / `PESSIMISTIC` — the lock

The row lock held from read to commit — a second `SELECT ... FOR UPDATE` on
the same row blocks until the first commits. The window is closed for *same-row*
races; a *crossed-row* (write-skew) race may still be open at READ COMMITTED.

```text
SELECT ... FOR UPDATE → [work] → UPDATE → COMMIT
        [the lock is held from FOR UPDATE to COMMIT]
```

**The grep** — `FOR UPDATE`/`select_for_update`/`with_for_update`/`PESSIMISTIC`/
`FOR NO KEY UPDATE`/`FOR SHARE`.

**Not this** — a plain `SELECT` (no `FOR UPDATE`) in a transaction is *not*
the close.

### `UNIQUE`/`CHECK`/`PRIMARY KEY` — the constraint

The datastore-level close: the raced field carries a `UNIQUE`/`CHECK`/`PRIMARY
KEY` that the DB enforces on `INSERT`/`UPDATE`. The loser gets
`IntegrityError`/`duplicate key`/`23505`/`1062` — never a second commit.

```text
UNIQUE(users.email) → INSERT ×2 → the 2nd: IntegrityError (23505/1062)
```

**The grep** — `UNIQUE`/`PRIMARY KEY`/`CHECK`/`CREATE UNIQUE INDEX` on the
raced field/table.

**Not this** — a `SELECT` uniqueness-check in app code is *not* the
constraint; the DB must enforce it.

### `SERIALIZABLE` + retry — the isolation

The strongest close: `SERIALIZABLE` detects the serialization anomaly and
aborts the loser with `40001 could not serialize` — the loser retries on a
fresh snapshot.

```text
SERIALIZABLE → [interleave] → the loser: 40001 could not serialize → retry
```

**The grep** — `SERIALIZABLE`/`SERIALIZABLE ISOLATION`/`transaction.*serial`/
`SET TRANSACTION ISOLATION`.

**Not this** — `REPEATABLE READ` is *not* SERIALIZABLE — write-skew still
works under it. `READ COMMITTED` (the default) is *not* a close at all.

### `version`/`row_version`/`lock_version` — the optimistic lock

The version-column close: `UPDATE ... WHERE version = <read-v>` — the loser
gets `rowcount=0`/`OptimisticLockException`/stale and must retry on the fresh
version.

```text
SELECT version=7 → [work] → UPDATE ... WHERE version=7 → rowcount=0: stale
```

**The grep** — `version`/`row_version`/`lock_version`/`@Version`/
`concurrency`/`ETag`/`If-Match`.

**Not this** — a version column *read* but never used in a `WHERE` is not
the close; the `UPDATE ... WHERE version` must be the *only* write.

### Datastore-atomic — `findOneAndUpdate`/`updateMany`/`update_all`/`update_counters`/`F()`

The datastore's own atomic: `findOneAndUpdate({id, used:false}, {$set:{used:true}})`
is a single atomic find-modify — the loser gets `null` (the predicate no
longer matches).

```text
findOneAndUpdate({used:false}, ...) → the 2nd: null — the doc already used:true
```

**The grep** — `findOneAndUpdate`/`updateMany`/`update_all`/`update_counters`/
`F(`/`$inc`/`ConditionExpression`/`UpdateExpression`/`WATCH`/`MULTI`/`IF`/Lua.

**Not this** — `find` → `if` → `update` is *not* the datastore-atomic — the
find and the update are two ops.

### `pg_advisory`/`GET_LOCK`/redlock — the advisory lock

A lock taken and held across the whole check→act — `pg_advisory_lock(id)` →
read → write → `pg_advisory_unlock(id)`. A second holder blocks.

```text
pg_advisory_lock(id) → SELECT → UPDATE → pg_advisory_unlock(id)
        [the lock is held across the window]
```

**The grep** — `pg_advisory`/`GET_LOCK`/`redlock`/`distributed.*lock`/`mutex`/
`synchronize`/`@synchronized`/`sync.Mutex`.

**Not this** — an advisory lock scoped *only* to the write (not the read→write)
is not the close — the lock must span the whole window.

### `SKIP LOCKED`/`INSERT ... ON CONFLICT DO NOTHING` — the queue/dedup

The worker-claim close: `SELECT ... FOR UPDATE SKIP LOCKED` — the second
claimer skips the claimed row. The idempotency close: `INSERT ... ON CONFLICT
DO NOTHING` — the second insert is a no-op.

```text
SELECT ... FOR UPDATE SKIP LOCKED → claim → work → commit
        [the 2nd claimer skips the row — no double-execution]
```

**The grep** — `SKIP LOCKED`/`ON CONFLICT.*DO NOTHING`/`INSERT IGNORE`/
`ON DUPLICATE KEY`/`INSERT.*IF NOT EXISTS`/`WATCH.*MULTI`/`Idempotency`.

### Single worker + private DB — the architecture falsifier

A single threaded worker on a private per-instance DB can't overlap at the
HTTP layer — the requests serialize at the accept queue. The race is at the
DB/worker layer (two replicas, a claim, two queries interleaved at the DB).

**The test** — a slow endpoint's serial-vs-parallel delay: 2× = single worker;
~1× = real parallelism.

## The falsifier-verdict table

| The grep found | The verdict |
|---|---|
| `UPDATE ... WHERE` + rowcount | falsifier — record, next endpoint |
| `FOR UPDATE`/`PESSIMISTIC` | falsifier for same-row |
| `UNIQUE`/`CHECK`/PK | falsifier |
| `SERIALIZABLE` + retry | falsifier |
| `version` in `WHERE` | falsifier for same-row; write-skew may still be open |
| `findOneAndUpdate`/atomic | falsifier |
| `pg_advisory`/`GET_LOCK` scoped | falsifier |
| `SKIP LOCKED`/idempotent | falsifier for the queue |
| single worker + private DB | falsifier for the HTTP layer |
| a transaction alone | **not** a falsifier |
| `SELECT` (no `FOR UPDATE`) | **not** a falsifier |
| `REPEATABLE READ` | **not** a falsifier for write-skew |
