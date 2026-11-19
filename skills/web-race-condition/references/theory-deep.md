# Theory deep — the full concurrency model behind the window

Why the race works at every layer — the memory model, the scheduling model,
the transaction model, and the distributed-systems model.

---

## 1. The atomicity hierarchy — what "atomic" means at each layer

```text
instruction   — a single CPU op (atomic on one core; torn across cores for wide types)
statement     — one SQL statement (atomic at the row level; not at the multi-row level)
transaction   — a BEGIN..COMMIT block (atomic as a unit ONLY at its isolation level)
request       — an HTTP request (NOT atomic — it spans statements and transactions)
flow          — a multi-request flow (never atomic — state lives between requests)
service       — a cross-service operation (no shared atomicity — only compensation)
```

The bug is almost always a level confusion: the app treats a `request` or a
`flow` as atomic when only a `statement` is.

## 2. The happens-before model

Two requests A and B racing on record R. The bug exists when there's no
happens-before edge between A's write and B's read:

```text
A: read R → decide → write R
                        ↘ (no edge)
B:            read R → decide → write R
                          ↗ B read the pre-A state
```

A lock, a single statement, or SERIALIZABLE creates the edge: B's read is
ordered after A's commit. Without it, B reads the pre-state and both pass.

## 3. The scheduler model — where the interleave happens

| Runtime | The schedule point | The window |
|---|---|---|
| cooperative (Node, asyncio) | each `await`/yield | between awaits — deterministic to predict |
| preemptive threads (Python, Java, Go) | any instruction boundary | anywhere — but I/O blocks are the common yield |
| process workers (PHP-FPM, gunicorn sync) | truly parallel | the statement boundary, across workers |
| the DB | statement-by-statement | the query boundary |
| the OS/filesystem | syscall-by-syscall | the check→use syscall pair |

The race is won by landing a request in the *other* request's yield gap. The
interleave mechanic (a withheld last byte) is how you place a request inside
that gap deterministically.

## 4. The snapshot model — MVCC and the read

Most modern DBs are multi-version: a `SELECT` reads a snapshot, not the live
row. Two transactions each read the snapshot at their own T0 — which is why
both see the same pre-state even after one commits.

```text
Postgres READ COMMITTED: each STATEMENT gets a fresh snapshot — but a
non-locking SELECT still doesn't block the other writer.

Postgres REPEATABLE READ: the whole TRANSACTION reads one snapshot — a second
transaction can read a "frozen" old value and act on it (easier to win).

MySQL InnoDB REPEATABLE READ: same — snapshot reads, gap locks on writes.
```

The subtlety: a snapshot read makes the race *easier*, not harder — the loser
acts on a stale value and the write-write conflict is the only thing that
saves it, and only if the code checks `RowsAffected`.

## 5. The lock model — pessimistic vs optimistic

| Lock | How | Window |
|---|---|---|
| pessimistic (`FOR UPDATE`) | the read takes a row lock to commit | closed — B blocks until A commits, then sees new state |
| optimistic (`version` col) | the write checks the version | closed — B's update affects 0 rows |
| no lock | two snapshot reads, two writes | open |

The `version`-column trap: it only closes the *lost-update* on that row, not a
cross-row invariant (write-skew) — B still passes its *check* on the snapshot.

## 6. The constraint model — the only defence that can't be timed out

A constraint is enforced *by the storage engine at commit*, not by app code —
no scheduling can make two conflicting commits both succeed.

| Constraint | Enforces |
|---|---|
| `UNIQUE` | the loser raises on commit |
| `CHECK` | the loser's value violates the predicate |
| `PRIMARY KEY` | the duplicate key fails |
| `FOREIGN KEY` | the dependent write fails without the parent |
| `EXCLUSION` | a range/period overlap fails (Postgres) |

The app-level `if` can be raced; the `UNIQUE` can't — it's why the schema
audit is the strongest falsifier signal.

## 7. The isolation-level model — what each level actually guarantees

| Level | Dirty read | Non-repeatable read | Phantom | Write skew |
|---|---|---|---|---|
| READ UNCOMMITTED | yes | yes | yes | yes |
| READ COMMITTED | no | yes | yes | yes |
| REPEATABLE READ | no | no | yes (Postgres: no) | yes (Postgres: no) |
| SERIALIZABLE | no | no | no | no |

The one that surprises: **REPEATABLE READ does not stop write-skew** in MySQL —
two transactions can still violate a cross-row invariant. Only SERIALIZABLE
or an explicit lock does.

## 8. The distributed-systems model — when no lock exists

Across services there's no shared row to lock. The closes are architectural:

| Pattern | How it closes the window |
|---|---|
| conditional write at the owner | `ConditionExpression`/CAS — the data owner serializes |
| saga / reservation | the act is compensated, not prevented — race a hold that can be released |
| idempotency key | the second request is deduplicated |
| single-writer per key | route all writes for one key to one worker |
| fencing token | a monotonic token the owner checks — rejects the stale writer |

The lesson: "the check is in another service" is not a defence — it's the
vulnerability, because no lock spans the boundary.

## 9. The linearizability test — is the operation atomic at all?

An operation is linearizable if every observer sees it take effect at a single
point between its start and end. The check-then-act is **not** linearizable —
it takes effect at the read, but the state can change before the write. The
atomic `UPDATE ... WHERE` is linearizable: its effect is the single statement.

## 10. The serial-impossibility proof

The formal confirmation criterion: a race is proven iff the final state cannot
be produced by *any* serial ordering of the requests.

```text
requests: {A: redeem(code), B: redeem(code)}
serial orderings: A→B gives [success, fail]; B→A gives [fail, success]
raced outcome:      [success, success]   ← not in the serial set → proven
```

Every crossed state in `exploitation-shapes.md` is a state outside the serial
set. This is why the baseline matters: it enumerates the serial set.

## 11. The probabilistic-correctness model

A race is a *probabilistic* bug — it doesn't always fire. The evidence bar is
a single proven serial-impossible outcome, not a 100% hit rate. Reliability
(landing the pair every time) is an engineering problem solved by widening
the window or tightening the delivery — not a correctness question.

## 12. The window-width formula

```text
window_width ≈ work_between_read_and_write + db_round_trip + scheduling_delay
win_prob     ≈ f(delivery_tightness / window_width)
```

- `work_between`: external calls, second queries, ORM flush — the controllable
  part (a pathological input inflates it).
- `db_round_trip`: the latency to the DB — fixed for a given deployment.
- `scheduling_delay`: the yield gap — the interleave mechanic minimizes it.
- `delivery_tightness`: how close in time the requests start — single-packet
  maximizes it.

Make `window_width` big (pathological input, heavy field) or
`delivery_tightness` small (single-packet, interleave) — either moves the win
probability toward 1.
