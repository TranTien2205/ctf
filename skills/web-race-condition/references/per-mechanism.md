# Per-mechanism — the underlying race mechanism, each variant

The mechanism is *how* the check and the act separate. Each variant has its own
window shape, probe, and close.

---

## 1. Read-modify-write (RMW) — the base mechanism

```text
read S → decide on S → write S'    — the canonical gap
```

Two transactions each read `S`, both pass the check, both write. The window is
the whole read→write span.

- **Where it lives**: every ORM `find → modify → save`, every two-statement
  check-then-update.
- **Probe**: `race_probe` same-request burst on the consuming endpoint.
- **Crossed state**: the doubly-applied effect.
- **Close**: atomic `UPDATE ... WHERE`, `FOR UPDATE`, constraint.

## 2. Check-then-act (CTA) — RMW's logic form

```text
if (read_predicate): act()
```

The "read" is a predicate (`balance>=x`, `!used`, `count<max`) and the "act"
is an effect, possibly with no corresponding write — the state change is the
side effect, not an UPDATE.

- **Where it lives**: guards, validators, ACL checks, rate limits.
- **Probe**: same burst; the crossed state is the act running twice.
- **Close**: the predicate must be part of the act's atomic op, or a lock.

## 3. Double-spend — the resource-consume race

```text
read resource → if available: consume resource
```

A specialization of RMW where the "value" is a consumable — a code, a balance,
a seat. The race spends it twice.

- **Where it lives**: redeem/withdraw/book/vote endpoints.
- **Probe**: `race_probe` on the consume endpoint; the crossed state is the
  resource consumed twice.
- **Close**: the consume must be conditional-on-unused in one statement.

## 4. TOCTOU on a name/path — the filesystem form

```text
exists(name) ? safe : use(name)    — or: check(name) → open(name)
```

The check reads the path's properties; the use re-resolves the path — and an
attacker swaps what the path points to between them.

- **Where it lives**: temp files, upload validation, symlink targets, archive
  extraction.
- **Probe**: not `race_probe` — a tight rename/symlink loop racing the
  check→open, or two processes.
- **Crossed state**: the open acts on a different file than the check saw.
- **Close**: operate on the fd from the check (`openat2`/`O_NOFOLLOW`/
  `O_EXCL`), never re-resolve the path.

## 5. Time-of-check to time-of-use on identity — the session form

```text
validate(token claims at T1) → act(at T2 on the claims)
```

The "state" is a token the request carries — a JWT, a session. Two requests
with the *same* pre-rotation token both validate against the pre-state.

- **Where it lives**: token rotation, session revocation, JWT replay,
  "logout-all".
- **Probe**: race two requests carrying the same superseded token.
- **Crossed state**: the dead token still authenticates.
- **Close**: server-side token version the read checks at act-time.

## 6. Signal/interrupt race — the async-callback form

```text
handler begins → async callback (signal, event, completion) interrupts mid-window
```

The "second request" isn't a request — it's an interrupt that re-enters the
handler or mutates shared state between the check and the act.

- **Where it lives**: signal handlers, async completions, interruptible
  syscalls, node callbacks.
- **Probe**: a trigger that fires the interrupt inside the window — a second
  request, a signal, a concurrent event.
- **Close**: make the check→act uninterruptible (mask signals, a critical
  section).

## 7. Dirty-read race — the uncommitted-visibility form

```text
T1: reads T2's UNCOMMITTED write → acts on it → T2 rolls back
```

At READ UNCOMMITTED a transaction sees another's uncommitted write, acts on a
value that never officially existed.

- **Where it lives**: `READ UNCOMMITTED`/`read committed` misconfig, `nolock`
  hints, reporting paths.
- **Probe**: T2 starts a write and holds it uncommitted; T1 reads and acts on
  it; T2 rolls back — T1 acted on a phantom.
- **Crossed state**: an effect driven by a value that was never committed.
- **Close**: any isolation ≥ READ COMMITTED.

## 8. Write-skew — the multi-record invariant race

```text
T1: reads A and B, checks A+B>=cap, decrements A
T2: reads A and B, checks A+B>=cap, decrements B
```

Both check the *joint* invariant, each on a different record — both pass,
and A+B goes below cap. `FOR UPDATE` on each row doesn't help; the invariant
is across rows.

- **Where it lives**: "total across rows must stay ≥ X" — a team cap, a
  pooled balance, a shared quota.
- **Probe**: `--url-b` — A decrements row1, B decrements row2.
- **Crossed state**: the joint invariant violated though each row's check
  passed.
- **Close**: SERIALIZABLE, or a single lock/row that serializes the *group*
  (a parent-row lock, `pg_advisory_xact_lock`).

## 9. Lost-update — the blind-write race

```text
T1: reads counter=5 → computes 6 → writes 6
T2: reads counter=5 → computes 6 → writes 6    → expected 7, got 6
```

No check at all — just two read-compute-writes that overwrite each other. The
count loses an increment.

- **Where it lives**: counters, tallies, `stats.views = views + 1` done in
  app code.
- **Probe**: `--count N` identical increments; read the counter — it's less
  than N.
- **Crossed state**: `counter < N` after N accepted increments.
- **Close**: `UPDATE c = c + 1` (atomic increment), or a version column.

## 10. Phantom-read — the range-check race

```text
T1: SELECT * WHERE status='open' → decides on the empty/nonempty set
T2: INSERT a row with status='open' → commits
```

T1's range query sees a set; T2's insert changes what the range *would* return
— a `FOR UPDATE` on the rows T1 saw doesn't lock the *gap* where T2's phantom
row lands.

- **Where it lives**: "is there any open X" gates, "count of Y < N" checks.
- **Probe**: T1's "no open X" check racing T2's `INSERT status='open'`.
- **Crossed state**: T1 acts as if no open X exists while T2 just created one.
- **Close**: SERIALIZABLE (predicate lock) or a lock on the table/parent that
  serializes the range.

## 11. The batch/bulk race — a window across a loop

```text
for item in batch: read item; if ok: write item    — the whole loop is one window
```

A batch loop checks and writes item-by-item without a transaction — a
concurrent request can interleave *between iterations*, seeing the batch
half-applied.

- **Where it lives**: bulk imports, batch updates, migration-like endpoints.
- **Probe**: a reader racing the batch's midpoint.
- **Crossed state**: a state that mixes applied and unapplied items.
- **Close**: wrap the batch in one transaction, or a batch-level lock.

## 12. The mechanism → probe → close table

| Mechanism | Window | Probe | Close |
|---|---|---|---|
| RMW | read→write | burst | atomic update / lock |
| CTA | predicate→act | burst | predicate in the act |
| double-spend | consume | burst | conditional consume |
| path TOCTOU | check→open | rename/symlink loop | fd-from-check |
| identity TOCTOU | claims→act | 2 same-token reqs | token version |
| interrupt | callback | trigger inside window | uninterruptible section |
| dirty-read | uncommitted | hold + read + rollback | ≥ READ COMMITTED |
| write-skew | joint invariant | --url-b 2 rows | SERIALIZABLE / group lock |
| lost-update | read-compute-write | N increments | atomic increment / version |
| phantom-read | range | insert racing range | SERIALIZABLE / table lock |
| batch | between iterations | reader mid-batch | batch txn / lock |
