# Detection deep — every detection method, exhaustive

The deep version of `detection.md`: every way a window reveals itself, every
grep pattern, every measurement, every response tell — before any race fires.

---

## 1. Endpoint discovery — building the writable-surface inventory

A race needs a state transition. Build the complete list of write endpoints
before choosing one.

```bash
# from the front-end bundle
python3 tools/web/bundle_miner.py --url "$BASE" --out /tmp/bundle 2>/dev/null
grep -rhoE '"/(api/)?[a-z0-9_/-]+"' /tmp/bundle | sort -u | grep -iE \
  '(redeem|buy|vote|transfer|withdraw|verify|book|claim|register|order|reset|invite|pay|apply|use|spin|draw|join|bid|trade|convert|exchange|refund|cancel|approve|accept|submit)'

# from source — the route table
grep -rnE '(route|@app\.|router\.|path\(|app\.(get|post|put|patch|delete)|urlpatterns|func:)' "$SRC" \
  | grep -vE '(test|spec|mock)' | grep -iE '(post|put|patch|delete)'
```

The candidate set is the intersection: *writable* AND *checked* — the endpoint
does a conditional update, not a blind insert.

## 2. The read→write gap grep — per-language, exhaustive

### Python / Django / Flask / SQLAlchemy

```bash
grep -rnE '\.(first|get|one|filter|filter_by|get_or_404)\(' "$SRC" -A 15 \
  | grep -B2 -A8 -E '(commit|flush|save|update|add|delete)'
```

```python
# the shapes, ranked by gap size
obj = Model.query.get(id); obj.f = v; db.session.commit()        # ORM unit-of-work — widest
row = db.execute(select).first(); if ok: db.execute(update)      # two statements
with db.session.begin(): ...                                     # transaction — check what's inside
obj = Model.query.with_for_update().get(id)                      # FOR UPDATE — falsifier
```

Django specifics:

```python
obj = Model.objects.get(pk=id); obj.f = v; obj.save()            # no transaction — window
with transaction.atomic(): obj = Model.objects.select_for_update().get(pk=id)   # closed
Model.objects.filter(pk=id, balance__gte=amt).update(balance=F('balance')-amt)  # atomic — closed
```

### Node / Express / Sequelize / raw

```javascript
// the awaits are the yield points — every one is a schedule opportunity
const u = await User.findByPk(id);          // read
if (u.balance >= amt) {
  await sendEmail(u);                        // work inside window — the giveaway
  await u.update({balance: u.balance-amt});  // write — gap between findByPk and update
}
await db.query('UPDATE t SET x=x-1 WHERE id=? AND x>=1');   // atomic — closed
```

```bash
grep -rnE 'await .*(find|get|select|query)' "$SRC" -A 6 | grep -nE 'await .*(update|save|insert|create|destroy)'
```

### Go

```go
// two separate db calls — the widest form, no tx at all
var bal int; db.QueryRow("SELECT balance FROM a WHERE id=?", id).Scan(&bal)
if bal >= amt { db.Exec("UPDATE a SET balance=balance-? WHERE id=?", amt, id) }

// tx but non-locking read — still a window at READ COMMITTED
tx, _ := db.Begin(); tx.QueryRow("SELECT balance...").Scan(&bal); tx.Exec("UPDATE..."); tx.Commit()

// the closed forms
tx.QueryRow("SELECT balance FROM a WHERE id=? FOR UPDATE", id).Scan(&bal)
res, _ := db.Exec("UPDATE a SET balance=balance-? WHERE id=? AND balance>=?", amt, id)
n, _ := res.RowsAffected()          // the loser reads n==0 — check the code does
```

### Ruby / Rails

```ruby
# active_record: find → modify → save outside a transaction
u = User.find(id); u.balance -= amt; u.save!                    # window
User.transaction { u = User.lock.find(id); ... }                # closed
User.where(id: id).update_all("balance = balance - #{amt}")     # atomic — closed
```

### PHP

```php
$r = $db->query("SELECT balance FROM a WHERE id=$id");           // read
if ($r['balance'] >= $amt) {
    mail($user, ...);                                            // work in the window
    $db->query("UPDATE a SET balance=balance-$amt WHERE id=$id"); // write
}
```

### Java / JPA / Spring

```java
Account a = em.find(Account.class, id);        // read — attached
if (a.getBalance() >= amt) { a.setBalance(...); } // dirty-checked flush at commit — window
@Lock(LockModeType.PESSIMISTIC_WRITE) em.find(...) // closed
em.createQuery("UPDATE Account a SET a.balance=a.balance-:amt WHERE a.id=:id AND a.balance>=:amt")
```

## 3. The constraint audit — reading the schema

The single strongest static signal: does a constraint back the check?

```bash
grep -rniE '(create table|unique|primary key|constraint|index|check|foreign key)' "$SRC"/**/migrations "$SRC"/**/*.sql 2>/dev/null
```

| Schema says | Means |
|---|---|
| `UNIQUE(email)` on users | registration race closed at the DB |
| no constraint, code checks `if not exists` | window is structural — race is only a timing problem |
| `CHECK (balance >= 0)` | negative balance impossible — the DB aborts the loser |
| partial `UNIQUE ... WHERE used` | the "single use" claim is enforced — closed |
| composite `UNIQUE(user_id, target_id)` | double-vote closed |
| no `CHECK`, no `UNIQUE`, code-only `if` | open — go dynamic |

## 4. The transaction-scope audit

For each read→write pair found, determine what transaction they share:

```bash
grep -rnB5 -A15 'UPDATE\|INSERT\|DELETE' "$SRC" | grep -nE 'BEGIN|transaction|autocommit|isolation|FOR UPDATE|LOCK IN SHARE|SKIP LOCKED|NOWAIT'
```

| Scope observed | Window |
|---|---|
| two statements, no `BEGIN` | autocommit — open |
| `BEGIN` … read … work … write … `COMMIT` | transaction but **non-locking read** — still a window at READ COMMITTED |
| `SELECT ... FOR UPDATE` inside the txn | closed |
| isolation `SERIALIZABLE` | closed at DB; check app retry handling |
| `REPEATABLE READ` | the *read* sees a snapshot — the window is wider, not closed |

The subtle one: **a transaction does not close the window by itself.** READ
COMMITTED and REPEATABLE READ both let two transactions read the same pre-state
and both write — the second just overwrites or errors depending on the shape.
Only a lock (`FOR UPDATE`), an atomic single statement, or SERIALIZABLE closes
it.

## 5. The async-yield inventory

Every place the runtime can switch tasks between read and write:

```bash
grep -rnE 'await |yield |\.then\(|callback|async def|goroutine|go func|Thread|executor|asyncio' "$SRC" | grep -v node_modules | wc -l
```

- **Node**: every `await` between `findOne` and `update` is a yield — the event
  loop schedules the other request right there.
- **Python**: threads switch on any I/O — the second query, the `send`, the
  `requests.get`.
- **Go**: goroutines yield at channel ops, I/O, and the scheduler's whim.
- **async Python**: `await db.fetch` then `await db.execute` — the loop can
  interleave a second coroutine between them.

Count the yields between the read and the commit — each one is a coin flip the
other request can win.

## 6. The response-forensics pass

Before racing, read what the serial responses already reveal:

```bash
# the check's own error reveals the check exists and where it sits
curl -s -X POST "$BASE/api/redeem" -d '{"code":"USED"}' -H 'Cookie: s=..'   # "already used" — a code check exists
curl -s -X POST "$BASE/api/withdraw" -d '{"amount":99999}' -H 'Cookie: s=..' # "insufficient" — a balance check exists
curl -s -X POST "$BASE/api/vote" -d '{}' -H 'Cookie: s=..'                   # 4xx naming the missing field
```

| Response detail | Reads as |
|---|---|
| error strings differ between "doesn't exist" and "already used" | two separate checks — the window is between them |
| `"remaining": N` in the body | the count is read and returned — race the boundary N→N+1 |
| a `Location` redirect on success vs error | success path is distinguishable — a clean signature |
| identical body, status 200 vs 409 | `--signature-mode status` suffices |

## 7. The multi-request-flow map

For flows spanning requests, map which record carries the state:

```text
step1 POST /cart/add {item}        → writes session.cart
step2 POST /checkout               → reads cart, computes price, writes order
step3 POST /pay                    → reads order.total, charges
```

The race: `POST /cart/add` and `POST /pay` overlapping — the charge reads a
total computed before (or after) the add commits. Find the shared record
(`session`, `order`, `cart` row) and the read that consumes it.

## 8. The timing-oracle discovery sweep

```bash
# for each candidate endpoint, compare response time of a normal vs pathological input
for inp in 'a@b.co' 'a@abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!' "$(python3 -c 'print("a"*500)')@x.co'; do
  echo "== $inp"; for i in 1 2 3; do
    curl -s -o /dev/null -w '%{time_total}\n' -X POST "$BASE/endpoint" \
      -d "{\"field\":\"$inp\"}" -H 'Cookie: s=..'
  done; done
```

A pathological input that takes measurably longer is a check that does more
work — a wider window for free. Candidates: regex validation, uniqueness
lookups on unindexed columns, recursive serializers, `bcrypt`/`scrypt` on
attacker-influenced input lengths.

## 9. The "is it even concurrent" check

Before racing, confirm the server can run two handlers at once:

```bash
# an endpoint that sleeps — if two calls overlap, wall-clock < 2× sleep
time (curl -s "$BASE/slow" & curl -s "$BASE/slow" & wait)
```

If two requests to a deliberately slow endpoint take 2× the sleep serially, the
server is single-worker — drop `--concurrency` to match, or race a different
layer (the DB, a background job) — or the race is unwinnable at the HTTP layer.

## 10. The decision table

| Observed | Route |
|---|---|
| code check, no constraint, gap between statements | `race_probe`, `per-check-*` |
| atomic `UPDATE ... WHERE` with rowcount gate | falsifier |
| `FOR UPDATE` / `SERIALIZABLE` / unique constraint | falsifier |
| multi-request flow, shared session record | map the shared record, `--url-b` |
| write path safe, slow check found by timing | pathological-input widening |
| single-worker server | race the DB layer or another tier |
| no writable endpoint | not a race target |
