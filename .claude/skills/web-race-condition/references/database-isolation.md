# Database isolation — which level leaves the window open

The isolation level decides whether the race is even possible. Read the app's
configured level before spending the write budget — the wrong level is the
falsifier.

---

## 1. The four levels, by what two transactions can do

| Level | Both can read pre-state | Both can write | Window |
|---|---|---|---|
| READ UNCOMMITTED | yes (even uncommitted) | yes | widest — also dirty reads |
| READ COMMITTED | yes | yes | **default in Postgres, most ORMs — open** |
| REPEATABLE READ | yes (snapshot) | yes — write-write conflict errors one | wider snapshot, but second write may fail |
| SERIALIZABLE | yes | one aborts | **closed** — the loser must retry |

The subtlety: **a transaction does not close the window by itself.** READ
COMMITTED and REPEATABLE READ both let two transactions read the same pre-state
and both proceed to write. Only a lock, an atomic statement, or SERIALIZABLE
closes it.

## 2. The default is the vulnerability

Almost every stack defaults to READ COMMITTED or REPEATABLE READ:

| Stack | Default isolation | Consequence |
|---|---|---|
| PostgreSQL | READ COMMITTED | the window is open unless the code locks |
| MySQL/InnoDB | REPEATABLE READ | snapshot reads — the gap is wider, second UPDATE on same row may deadlock |
| SQLite | SERIALIZABLE per file lock | the DB serializes writers — the HTTP layer is the only race surface |
| SQL Server | READ COMMITTED | open |
| Oracle | READ COMMITTED | open |
| MongoDB | single-document atomicity | a read-then-write is *not* atomic; a `findOneAndUpdate` is |
| DynamoDB | per-item | `ConditionExpression` or nothing — no transaction by default |

So "the app uses transactions" is not a defence — it usually means the app is
at READ COMMITTED, where the window lives.

## 3. Which defence actually closes the window, per DB

### PostgreSQL

```sql
-- atomic single statement — the clean close
UPDATE accounts SET balance = balance - 5 WHERE id = 1 AND balance >= 5;
SELECT 1 FROM accounts WHERE id = 1 FOR UPDATE;          -- row lock to commit
SELECT 1 FROM accounts WHERE id = 1 FOR NO KEY UPDATE;    -- weaker lock, still closes
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;             -- DB aborts the loser
-- advisory lock across app code — closes the window for non-row logic
SELECT pg_advisory_xact_lock(hashtext('redeem:' || code));
```

### MySQL / InnoDB

```sql
UPDATE accounts SET balance = balance - 5 WHERE id = 1 AND balance >= 5;
SELECT balance FROM accounts WHERE id = 1 FOR UPDATE;     -- row lock
SELECT balance FROM accounts WHERE id = 1 LOCK IN SHARE MODE;  -- shared read lock
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
GET_LOCK('redeem_code', 10);                              -- named advisory lock
```

### SQLite

```sql
UPDATE codes SET used=1 WHERE code=? AND used=0;          -- atomic — rowcount decides
BEGIN IMMEDIATE;                                          -- takes the write lock at BEGIN
-- the whole file serializes on write; the HTTP layer is the remaining surface
```

### MongoDB

```js
// read-then-write is NOT atomic — two finds both see used:false
db.codes.updateOne({code: c, used: false}, {$set: {used: true}})   // atomic — check matchedCount
db.codes.findOneAndUpdate({code: c, used: false}, {$set:{used:1}}) // atomic + returns doc
```

### DynamoDB

```js
// PutItem/UpdateItem with a condition — the only atomic primitive
await db.update({Key, UpdateExpression: 'SET used = :t',
                 ConditionExpression: 'used = :f'})   // ConditionalCheckFailed = the loser
```

## 4. The lock tells in source

```bash
grep -rnE '(FOR UPDATE|FOR NO KEY|LOCK IN SHARE|SKIP LOCKED|NOWAIT|pg_advisory|GET_LOCK|select_for_update|PESSIMISTIC|LockModeType|with_for_update|SERIALIZABLE|REPEATABLE|isolation_level|ConditionExpression|findOneAndUpdate)' "$SRC"
```

- **`FOR UPDATE` present and used on the raced read** → falsifier for that
  endpoint.
- **`with_for_update()` / `select_for_update()` / `@Lock`** → falsifier.
- **None of these, but a transaction wraps the pair** → the window is still
  open at READ COMMITTED — race it.

## 5. The ORM atomic-form tells

The atomic `UPDATE` in each ORM — its presence is the falsifier:

| ORM | Atomic close |
|---|---|
| SQLAlchemy | `update().where(..., balance >= amt).values(balance=balance-amt)` |
| Django ORM | `Account.objects.filter(id=i, balance__gte=amt).update(balance=F('balance')-amt)` |
| Sequelize | `Model.update({...}, {where: {id, balance: {[Op.gte]: amt}}})` then check `[0]` affected |
| ActiveRecord | `Account.where(id: i).where('balance >= ?', amt).update_all('balance = balance - ?', amt)` |
| JPA | bulk `UPDATE ... WHERE balance >= :amt` JPQL |
| Mongo driver | `findOneAndUpdate`/`updateOne` with the predicate in the filter |
| Prisma | `updateMany({where: {balance: {gte: amt}}, data: {balance: {decrement: amt}}})` |

When the code uses the `Model.find → modify → save` form instead of the atomic
form, the window is open — the ORM loaded a snapshot.

## 6. Multi-table and multi-row windows

The hardest races cross tables: read table A to validate, write table B.

```text
SELECT balance FROM accounts WHERE id=?     -- table A read
UPDATE ledger SET ...                        -- table B write
UPDATE accounts SET balance=...              -- table A write
```

`FOR UPDATE` only locks the row actually selected — a validation read of a
*different* table is not locked, so two transactions both validate against the
same A row and both write B. This is why "the balance update is atomic" is not
the whole answer — the *validation read* still needs to be locked or in the
same statement.

## 7. Queue patterns — `SKIP LOCKED` and the job race

```sql
-- the worker-claim pattern that is SAFE
SELECT job FROM queue WHERE status='pending' ORDER BY id FOR UPDATE SKIP LOCKED LIMIT 1;
UPDATE queue SET status='running' WHERE id=?;
```

Without `SKIP LOCKED`/`FOR UPDATE`, two workers `SELECT` the same pending job
and both mark it running — the double-execute race. In source, a job-claim
that does plain `SELECT` then `UPDATE` is the window.

## 8. Snapshot-vs-lock — the REPEATABLE READ subtlety

At REPEATABLE READ a transaction reads a consistent snapshot — so a second
transaction that read `balance=100` still sees `100` even after the first
committed `balance=50`. Its `UPDATE` then blocks on the row lock and, once
acquired, may apply the decrement to the *new* value or abort depending on
the DB. The read being "frozen" makes the race *easier*, not harder — the
losers act on stale state. Only the write-write conflict saves it, and only if
the code checks `RowsAffected`/affected count.

## 9. The read-only-race — a TOCTOU on a view

Not every race is write-vs-write. A *read* racing a *write* produces a stale
read that the app then trusts:

```text
request A: begins, reads account.verified = true, proceeds to privileged act
request B: concurrently sets verified = false
```

A's act rode in on the pre-revocation state. Detect by racing the revoking
request against the gated one (`--url-b`). This is the `V` alphabet row —
verification pending.

## 10. The decision table

| Config observed | Race viable? |
|---|---|
| no transaction, autocommit statements | yes — widest |
| transaction at READ COMMITTED, non-locking read | yes |
| transaction, `FOR UPDATE` on the read | no — falsifier |
| SERIALIZABLE with retry | no — falsifier |
| SERIALIZABLE without retry | not a bypass; maybe a 500-DoS |
| atomic `UPDATE ... WHERE` + rowcount check | no — falsifier |
| multi-table validate-then-write | yes — the validation read is unlocked |
| Mongo `find` + `update` | yes |
| Mongo `findOneAndUpdate` | no — falsifier |
| DynamoDB `ConditionExpression` | no — falsifier |
| SQLite, whole-file lock | race the HTTP layer only |
