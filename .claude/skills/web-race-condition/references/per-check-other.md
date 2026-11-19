# Per-check other — the less common check windows

The check-then-act windows that don't fit the money/token/registration/OTP/vote/
inventory mould: rate limits, idempotency keys, locks and semaphores, version
checks, quota/boundary checks, and role/permission reads.

---

## Rate limiter — the counter that lies

The limiter is itself a counter check-then-act — `if attempts < cap` → `++`.
Race the limiter to pass more than `cap` requests through it.

```text
GET rate.attempts → if <cap → ++rate.attempts
                    [window: check → ++]
```

```bash
python3 tools/web/race_probe.py --url "$BASE/api/<limited-ep>" \
  --method POST --body '<b>' -H 'Cookie: <s>' \
  --concurrency <cap+3> --count <cap+3> --baseline-count 3 \
  --signature-mode status --write-ack --challenge <name>
```

**Crossed state** — `<cap+1>` successful responses where serial produces
`<cap>`; the counter reads `> cap`.

**Close** — an atomic `UPDATE rate SET attempts = attempts + 1 WHERE attempts < cap`,
a real token-bucket, or a limiter that runs *before* the handler under one lock.

## Idempotency key — the dedup record itself is the window

A `key` dedup record checked `if exists(key)` → `insert(key)` — the insert and
the check are two statements.

```text
POST /api/op  Idempotency-Key: abc → if !exists(key) → do_op → insert(key)
                                        [window: exists → insert]
```

```bash
python3 tools/web/race_probe.py --url "$BASE/api/op" \
  --method POST --body '{"amount":10}' -H 'Cookie: <s>' -H 'Idempotency-Key: samekey' \
  --concurrency 5 --count 5 --baseline-count 3 \
  --signature-mode normalized-body --write-ack --challenge <name>
```

**Crossed state** — the op executes twice on one key: the ledger shows two rows
keyed `samekey`. The dedup record was a check-then-act, not a unique constraint.

**Close** — `INSERT ... ON CONFLICT (key) DO NOTHING` + `if rowcount: op`, or a
`UNIQUE(key)` constraint.

## Lock / semaphore — the held-flag check

A cooperative lock checked `if !lock.held` → `lock.held = 1` → `act` — the
acquire is itself a check-then-act, so two actors both hold.

```text
POST /api/lock → if !held → held=1 → do the locked thing
                 [window: check-held → set-held]
```

```bash
python3 tools/web/race_probe.py --url "$BASE/api/lock" \
  --method POST -H 'Cookie: <s>' \
  --concurrency 5 --count 5 --baseline-count 3 \
  --signature-mode normalized-body --write-ack --challenge <name>
```

**Crossed state** — two actors report `held`; the "locked" operation runs twice
concurrently. The lock is a record, not a primitive.

**Close** — a real lock (a kernel/mutex/DB-lock/`pg_advisory`), a lock scoped to
the whole check→act, or a `UNIQUE`/atomic-acquire flag.

## Version / optimistic lock — the read-then-act-on-version

An optimistic-lock column `v` checked `if v == read_v` → `update where v` —
the check and the write are still two statements if the `WHERE` is separate.

```text
SELECT version=7 → [work] → UPDATE ... WHERE version=7
                          [window: SELECT → UPDATE — the WHERE still separates]
```

```bash
python3 tools/web/race_probe.py --url "$BASE/api/row/1" \
  --method POST --body '{"amount":50}' -H 'Cookie: <s>' \
  --concurrency 5 --count 5 --baseline-count 3 \
  --signature-mode normalized-body --write-ack --challenge <name>
```

**Crossed state** — a lost update: two transactions both read `v=7`, both write
a different value `WHERE v=7`, and one wins — the loser's write is silently
dropped. The version column caught the *check* but not the *lost-update* if the
`UPDATE ... WHERE` isn't the single atomic statement.

**Close** — the `UPDATE ... WHERE version=7` as the *only* write (the rowcount
check turns the lost update into a retry), or a real `FOR UPDATE`.

## Quota / boundary — a check against a limit that lies at the boundary

A `if usage < quota` → `++usage` race — the boundary check is a check-then-act
on a derived value.

```text
GET /api/stats → if usage<quota → ++usage → act
                  [window: stats → ++]
```

```bash
python3 tools/web/race_probe.py --url "$BASE/api/use" \
  --method POST -H 'Cookie: <s>' \
  --concurrency <quota+2> --count <quota+2> --baseline-count 3 \
  --signature-mode status --write-ack --challenge <name>
```

**Crossed state** — `usage = quota + 1` — a value impossible under serial
enforcement.

**Close** — `UPDATE stats SET usage = usage + 1 WHERE usage < quota` + rowcount,
or a real semaphore.

## Role / permission — a read of `me.role` then an action on the read

A `SELECT role → if role == 'admin' → act` where the role is re-read per request
but the *action* uses the earlier read — race a role-change to downgrade or
upgrade the acting role.

```text
SELECT role='admin' → [work: another request revokes admin] → act as 'admin'
```

```bash
# the actor's own flow: a read of role → the action — interleave the role-change
python3 tools/web/race_probe.py \
  --url "$BASE/api/admin/act" --method POST -H 'Cookie: <admin-s>' \
  --url-b "$BASE/api/admin/demote" --method-b POST --body-b '{"id":1}' \
  --concurrency 2 --count 10 --baseline-count 4 \
  --signature-mode normalized-body --write-ack --challenge <name>
```

**Crossed state** — the action executes *after* the role was revoked but *as*
the old role — the actor acts on a stale permission.

**Close** — the permission check re-read inside the same transaction as the
action, or a role-version.

## The "other" rule

Any `if <predicate> → <act>` where the predicate's truth can change between the
check and the act is a candidate — name the predicate, name the window, name
the crossed state. The table is the index, not a menu; a check you can't name
isn't a check you've identified.
