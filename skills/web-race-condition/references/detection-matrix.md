# Detection matrix — the signal → mechanism → probe table

The row-per-signal matrix: what you observe, what mechanism it points to, and
the probe that confirms it.

---

## Source signals → mechanism → probe

| Source signal | Mechanism | First probe |
|---|---|---|
| `obj = M.query.get(id); ...; db.session.commit()` | ORM unit-of-work RMW | burst on the endpoint |
| `await findOne(...)` → `await update(...)` | async-yield RMW | burst |
| `db.QueryRow(...)` → `db.Exec(...)` | two-statement gap | burst |
| `M.find(id)` → `M.update!` outside `transaction` | Rails find-save | burst |
| `$db->query("SELECT")` → `if` → `$db->query("UPDATE")` | PHP autocommit | burst |
| `em.find` → `a.setX` → dirty-flush | JPA dirty-check | burst |
| `sendEmail`/`fetch`/`render` between read and re-read | external-call gap | interleave/stall |
| `SELECT` on table A → `INSERT`/`UPDATE` on table B | multi-table validate | burst |
| `exists(path)` → `open(path)` | fs TOCTOU | rename/symlink loop |
| `SELECT pending` → `UPDATE running` (no SKIP LOCKED) | worker claim | 2 triggers |
| `SELECT attempts` → `if <cap` → `UPDATE +1` | counter race | burst > cap |
| `invalidate` → `mint` → `store` (token) | rotation gap | interleave |
| `cache.get` → `db.write` → `cache.delete` | cache-invalidate | `--url-b` GET+POST |
| a `session`/`cart`/`order` record across steps | flow record | `--url-b` step-N + step-M |
| `SELECT version` → `update where version` | optimistic version | check if actually used |
| `if not exists(x): insert` + no UNIQUE | structural — always open | burst |

## Response signals → mechanism → probe

| Response signal | Mechanism | First probe |
|---|---|---|
| `{"error":"already used"}` on 2nd serial | a `used` check exists | burst the redeem |
| `409 Conflict` / `insufficient` | a check ran — atomic or separate? | baseline then race |
| `"remaining": N` in the body | a count is read and returned | race the N→N+1 boundary |
| `Set-Cookie` fresh session on every login | a session-count check (or none) | burst `/login`, count cookies |
| `Location` redirect on success vs error | success is distinguishable | `--signature-mode status` |
| identical 200s to a replay | a response cache — not a race | read the state |
| `40001`/`could not serialize` | SERIALIZABLE — falsifier | check for retry |
| `IntegrityError`/`duplicate key` on loser | a constraint — falsifier | record it |
| `OptimisticLockException`/stale | a version column — falsifier | record it |
| `ConditionalCheckFailed` | DynamoDB condition — falsifier | record it |

## Behavioral signals → mechanism → probe

| Behavioral signal | Mechanism | Probe |
|---|---|---|
| a normal vs pathological input timing delta | a slow check — widen | `timing-oracle` |
| 2× delay on a slow endpoint | single worker | race the DB layer |
| ~1× delay on a slow endpoint | real parallelism | race the HTTP layer |
| `429`s on the burst | a limiter before the handler | race the limiter |
| `403`/`invalid_token` on raced only | a consumed credential | race the issuer |
| a bot/job/seeder in the source | an actor race | startup hammer |
| a multi-step wizard/flow | a shared flow record | `--url-b` steps |
| an idempotency-key header | a dedup window | 2 same-key reqs |

## The signal → falsifier fast-path

| If you see | It's probably closed — check |
|---|---|
| `UPDATE ... WHERE <pred>` + `RowsAffected` | atomic — falsifier |
| `FOR UPDATE` / `select_for_update` / `PESSIMISTIC` | lock — falsifier |
| `UNIQUE`/`CHECK`/`PRIMARY KEY` on the raced field | constraint — falsifier |
| `SERIALIZABLE` + retry | isolation — falsifier |
| `version`/`row_version`/`lock_version` | optimistic — same-row falsifier |
| `findOneAndUpdate`/`updateMany`/`update_all`/`update_counters` | datastore-atomic — falsifier |
| `ConditionExpression`/`WATCH`/`MULTI`/`IF` | datastore-atomic — falsifier |
| `pg_advisory`/`GET_LOCK`/redlock scoped read→commit | lock — falsifier |
| `SKIP LOCKED` / `INSERT ... ON CONFLICT DO NOTHING` | queue/dedup — falsifier |
| `Idempotency-Key` enforced server-side | dedup — falsifier |

## The signal → mechanism fast-path

| If you see | It's probably open — the mechanism |
|---|---|
| a read and a write on the same record, no lock | RMW |
| `if` on a predicate + a separate write | CTA |
| a consumable (`code`,`balance`,`seat`,`vote`) | double-spend |
| `exists`/`check` → `open`/`use` on a path | path TOCTOU |
| token claims validated then acted on | identity TOCTOU |
| a callback/signal/interrupt mid-handler | interrupt race |
| `READ UNCOMMITTED`/`nolock` | dirty-read |
| a joint invariant across rows | write-skew |
| `c = c + 1` computed in app code | lost-update |
| a range/count query gating an act | phantom-read |
| a per-item read→write in a batch loop | batch race |
