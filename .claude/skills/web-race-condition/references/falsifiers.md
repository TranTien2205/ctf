# Falsifiers — the observations that close this class

A falsifier is evidence the window is *closed* for that endpoint. Record it,
stop, and move on — do not retry harder against a proven defence.

---

## 1. The atomic-statement falsifier

The check and the write are one statement. There is no gap.

```sql
UPDATE accounts SET balance = balance - 5 WHERE id = ? AND balance >= 5;
UPDATE codes SET used = 1 WHERE code = ? AND used = 0;
INSERT INTO votes ... ON CONFLICT DO NOTHING;   -- or the constraint rejects it
```

- **In source**: a single `UPDATE ... WHERE` / `INSERT ... ON CONFLICT` with
  the predicate in the `WHERE` clause, then `RowsAffected`/rowcount decides.
- **Probe signature**: the loser returns a clean `4xx`, the winner a `2xx`,
  and the post-state is never crossed — *under real overlap* (`max_in_flight`
  ≥ 2).
- **ORM forms**: `update().where(balance>=amt)`, `updateMany({balance:{gte}})`,
  `findOneAndUpdate`, `update_counters`, `update_all` with a `WHERE`.

## 2. The row-lock falsifier

The read takes a lock held to commit. The second request blocks until the
first commits, then sees the *new* state.

```sql
SELECT ... FOR UPDATE;           -- Postgres, MySQL
SELECT ... FOR NO KEY UPDATE;    -- weaker Postgres lock — still closes
SELECT ... LOCK IN SHARE MODE;   -- shared read lock
SELECT ... FOR UPDATE SKIP LOCKED; -- workers skip held rows — queue-safe
```

- **In source**: `FOR UPDATE`, `with_for_update()`, `select_for_update()`,
  `@Lock(PESSIMISTIC_WRITE)`, `Account.lock.find`.
- **Probe signature**: the loser's latency is measurably higher (it blocked);
  no crossed state ever.

## 3. The constraint falsifier

A DB constraint makes the losing write fail — no timing can win it.

| Constraint | Closes |
|---|---|
| `UNIQUE(email)` | registration/uniqueness race |
| `UNIQUE(user_id, target_id)` | double-vote |
| `UNIQUE(code)` on a redemption table | single-use redeem |
| `UNIQUE(name)` | file/namespace claim |
| `CHECK (balance >= 0)` | negative balance |
| `PRIMARY KEY` collision | any same-key insert |
| foreign-key + the parent check | a dependent-insert race |

- **Probe signature**: the loser gets a constraint-violation error
  (`23505`/`1062`/`IntegrityError`), never a second success.

## 4. The SERIALIZABLE falsifier

The DB aborts one of the conflicting transactions. The loser must retry — and
a retry sees the committed state.

- **In source**: `SET TRANSACTION ISOLATION LEVEL SERIALIZABLE`,
  `defaultIsolationLevel`, `connection.setTransactionIsolation`.
- **Probe signature**: one request gets a serialization failure
  (`40001`/`could not serialize`) — *and the app retries it*. If it doesn't
  retry, it's a 500-DoS, not a bypass — but still not a crossed state.
- **Caveat**: SERIALIZABLE without app retry is not a clean falsifier for the
  *class* — it just turns the win into a crash. Check the retry.

## 5. The optimistic-lock falsifier

A version column makes the loser's update a no-op.

```sql
UPDATE accounts SET balance = ?, version = version + 1 WHERE id = ? AND version = 7;
```

- **In source**: a `@Version`/`version`/`row_version` column in the entity.
- **Probe signature**: the loser's update affects `0` rows; the app sees a
  `OptimisticLockException`/stale-object error.

## 6. The datastore-atomic falsifier

NoSQL/serverless — the only close is the datastore's own conditional write.

| Store | Atomic close |
|---|---|
| MongoDB | `findOneAndUpdate`/`updateOne` with the predicate in the filter |
| DynamoDB | `UpdateItem`/`PutItem` with `ConditionExpression` |
| Redis | `WATCH`/`MULTI`/`EXEC`, or a Lua script (atomic) |
| Cassandra | `IF` lightweight transaction (`IF NOT EXISTS`, `IF col = x`) |

- **Probe signature**: `ConditionalCheckFailed`/`matchedCount=0` for the
  loser — no second effect.

## 7. The held-lock-across-code falsifier

A lock or semaphore that genuinely spans the read→write — a DB advisory lock,
a distributed lock *that is actually acquired*.

```sql
SELECT pg_advisory_xact_lock(hashtext('redeem:' || code));
GET_LOCK('redeem_code', timeout);
```

- **In source**: `pg_advisory_xact_lock`, `GET_LOCK`, `redlock`/a shared
  Redis lock — *acquired before the read, released after the commit*.
- **The trap**: a lock acquired *after* the read, or released *before* the
  write, doesn't close the window. Check the lock's scope, not its presence.
- **Probe signature**: the loser's latency spikes (it waited); no crossed
  state.

## 8. The queue-serialization falsifier

The work itself is serialized — a single worker, a `SKIP LOCKED` claim, an
idempotent handler.

- **In source**: `SELECT ... FOR UPDATE SKIP LOCKED`, a single consumer, or
  `idempotency_key` dedup on the handler.
- **Probe signature**: jobs run one at a time; a second trigger is deduplicated.

## 9. The single-worker falsifier (for the HTTP layer)

The server runs one worker — HTTP requests serialize at the accept queue.

- **Probe**: two requests to a deliberately-slow endpoint take `2×` the delay
  serially → one worker.
- **The caveat**: this closes the *HTTP* race only — the DB layer (two
  replicas, a background worker) may still be open. A single-worker app on a
  shared DB still races at the query boundary.

## 10. The "defence held under real overlap" falsifier

The empirical one: the raced run produced real overlap (`max_in_flight` ≥ 2),
the serial-loser shape on every loser, and no crossed state — across 3 clean
re-rolls at sane concurrency.

```text
baseline:  [200, 409, 409, 409]
raced:     concurrency 20, max_in_flight 20 → [200, 409×19]
state:     balance still 100, no double-effect
verdict:   falsifier — the defence held under real overlap
```

This is the *recorded negative* — write it to `knowledge/attempts/` or the
ledger so the next attempt doesn't re-walk the same endpoint.

## 11. Falsifier ≠ inconclusive

| Verdict | Meaning |
|---|---|
| **falsifier** | the defence is proven — `max_in_flight` ≥ 2, clean losers, no cross | stop, record |
| **inconclusive** | the mechanics failed — `max_in_flight` = 1, no overlap | fix delivery, re-roll |
| **negative (recorded)** | you tested and the window held | a falsifier |

An `inconclusive` run never closes the class — only a proven defence or a
clean real-overlap negative does.

## 12. The falsifier → decision table

| Falsifier found | Action |
|---|---|
| atomic `UPDATE ... WHERE` + rowcount | close endpoint, move on |
| `FOR UPDATE` / `select_for_update` / `PESSIMISTIC_WRITE` | close endpoint |
| `UNIQUE`/`CHECK`/`PRIMARY KEY` on the raced field | close endpoint |
| SERIALIZABLE + retry | close endpoint |
| optimistic `version` column | close endpoint |
| `findOneAndUpdate`/`ConditionExpression`/`WATCH`/Lua | close endpoint |
| real advisory/distributed lock scoped read→commit | close endpoint |
| `SKIP LOCKED` / idempotent worker / single consumer | close the job race |
| single worker + shared DB | HTTP closed, DB layer still open |
| 3 clean real-overlap runs, no cross | recorded negative — move on |
