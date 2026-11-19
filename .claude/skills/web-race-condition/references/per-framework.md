# Per-framework — how each stack leaves the window open

Each runtime schedules the second request differently. The framework decides
where the yield points are and which defence actually exists.

---

## 1. Node / Express — the single-threaded illusion

Node is single-threaded *between* awaits — which is exactly why the race works:
every `await` yields the loop to the other request.

```javascript
app.post('/redeem', async (req, res) => {
  const code = await db.get('SELECT used FROM codes WHERE code=?');   // yield #1
  if (!code.used) {
    await grantPrize(req.user);                                        // yield #2 — widest
    await db.run('UPDATE codes SET used=1 WHERE code=?');              // yield #3, then commit
    res.json({ok: true});
  }
});
```

- **Yield points**: every `await`, every `.then`, every stream event. Two
  requests interleave at each one.
- **The trap**: `async` makes the gap look atomic on the page — "single
  threaded" is only true inside synchronous runs between awaits.
- **Defence**: a single atomic statement, `SELECT ... FOR UPDATE` inside a
  transaction, or a mutex package. `Promise.all` of the read+write is not a
  defence.
- **Worker count**: `cluster`/PM2 forks multiply workers — each is a separate
  process, and an app-level mutex in one worker doesn't hold across them.

## 2. Python / Flask / Django / SQLAlchemy — threads and the ORM flush

```python
@app.route('/withdraw', methods=['POST'])
def withdraw():
    acct = Account.query.get(uid)          # read — attached to session
    if acct.balance >= amt:
        send_receipt(acct)                  # blocking I/O — the window widens here
        acct.balance -= amt
        db.session.commit()                 # flush+commit at the end — huge window
```

- **Yield points**: any blocking call (the ORM's second query, `requests.get`,
  `send_mail`, `time.sleep`). GIL or not, threads release on I/O.
- **The ORM trap**: the `commit()` at request end means the entire handler body
  is inside the window — the read happened at `query.get`, the write at
  `commit`, everything between is gap.
- **Defence**: `with_for_update()`, `transaction.atomic()` with
  `select_for_update()`, or `Model.objects.filter(...).update(F('balance')-amt)`
  (atomic). A Django `F()` expression is the idiomatic close.
- **Worker count**: gunicorn/uwsgi sync workers are processes — N workers run
  N handlers truly in parallel; gevent/eventlet workers interleave on I/O.

## 3. Go / net/http / database/sql — true parallelism

```go
func redeem(w http.ResponseWriter, r *http.Request) {
    var used bool
    db.QueryRow("SELECT used FROM codes WHERE code=?", c).Scan(&used)  // read
    if !used {
        grant(user)                                                     // work
        db.Exec("UPDATE codes SET used=1 WHERE code=?", c)             // write
    }
}
```

- **Yield points**: anywhere — goroutines are preemptively scheduled and run
  truly in parallel. Every request is its own goroutine on a pooled
  connection.
- **The trap**: `db.QueryRow` then `db.Exec` issue on *different* pooled
  connections — even inside `tx`, check the code used `tx.QueryRow`/`tx.Exec`,
  not `db.` (which opens a second connection outside the transaction).
- **Defence**: `tx` with `SELECT ... FOR UPDATE`, atomic `UPDATE ... WHERE`,
  or a `sync.Mutex` (single-process only — useless across replicas).
- **Worker count**: unbounded goroutines — no ceiling; the DB connection pool
  is the real limit.

## 4. Ruby / Rails — the `save` outside `transaction`

```ruby
def withdraw
  acct = Account.find(params[:id])          # read
  if acct.balance >= amt
    ReceiptMailer.send(acct).deliver_now     # work — window
    acct.update!(balance: acct.balance-amt)  # write
  end
end
```

- **Yield points**: any blocking I/O (mailer, HTTP call, second query).
- **The trap**: `find` → `update!` looks like one operation and isn't.
  `update_all` and `update_counters` are the atomic forms.
- **Defence**: `Account.transaction { a = Account.lock.find(id); ... }`
  (`lock` adds `FOR UPDATE`), or `update_counters`/atomic `UPDATE`.
- **Worker count**: Puma threads interleave; Puma/Unicorn workers are
  processes — both forms exist.

## 5. PHP / Laravel / plain — shared-nothing per request

```php
$bal = $db->query("SELECT balance FROM a WHERE id=$id")->fetch();
if ($bal['balance'] >= $amt) {
    mail($user, 'receipt', ...);              // work — window
    $db->query("UPDATE a SET balance=balance-$amt WHERE id=$id");
}
```

- **Yield points**: the whole request is one PHP process/thread — but two
  *requests* run in two FPM workers truly in parallel. The window is between
  the two `query()` calls.
- **The trap**: PHP's per-request isolation fools people into thinking races
  don't apply — they do, across concurrent FPM workers sharing one DB.
- **Defence**: `SELECT ... FOR UPDATE` inside `DB::transaction`, atomic
  `UPDATE ... WHERE`, or `INSERT ... ON DUPLICATE KEY`.
- **Worker count**: PHP-FPM pool size — match `--concurrency` to it.

## 6. Java / Spring / JPA — the dirty-checking flush

```java
@Transactional
public void withdraw(long id, int amt) {
    Account a = repo.findById(id).get();       // read — entity attached
    if (a.getBalance() >= amt) {
        notifier.send(a);                       // work — window
        a.setBalance(a.getBalance() - amt);     // dirty — flushed at commit
    }
}
```

- **Yield points**: threads are true parallelism; the JPA dirty-checking flush
  happens at commit — the entire method is the window.
- **The trap**: `@Transactional` looks safe but the non-locking `findById`
  still reads the snapshot; SERIALIZABLE or `PESSIMISTIC_WRITE` is needed.
- **Defence**: `@Lock(PESSIMISTIC_WRITE)` on the finder, a `Version` column
  (optimistic — loser's update fails), or a JPQL bulk `UPDATE ... WHERE`.
- **Worker count**: servlet thread pool — large; the DB is the contention
  point.

## 7. Serverless / FaaS — the stateless trap

```javascript
exports.handler = async (event) => {
  const item = await db.get({Key: id});          // DynamoDB-style get
  if (!item.used) {
    await grant(item);
    await db.put({...item, used: true});         // separate call — no tx by default
  }
};
```

- **Yield points**: every `await` — and the functions themselves are fully
  concurrent across warm containers.
- **The trap**: there is no process-local lock that means anything — each
  concurrent invocation is a different container. Only the datastore's
  conditional write closes the window.
- **Defence**: a conditional update (`ConditionExpression` /
  `attribute_not_exists`), which is the *only* atomic primitive available.
- **Worker count**: effectively unbounded concurrency — the easiest target
  for a burst.

## 8. Async Python — the event-loop form

```python
async def redeem(request):
    row = await db.fetch_one('SELECT used FROM codes WHERE code=:c', c)   # yield
    if not row.used:
        await grant(user)                                                  # yield
        await db.execute('UPDATE codes SET used=1 WHERE code=:c', c)      # yield
```

- Same shape as Node: each `await` schedules the other coroutine.
- **Defence**: `async with db.transaction()` + `FOR UPDATE`, or atomic update.
- **Worker count**: uvicorn workers × the event loop's coroutine concurrency.

## 9. The yield-point summary table

| Stack | Yield / parallel mechanism | Window shape | Atomic close |
|---|---|---|---|
| Node | `await` schedules other request | between awaits | single `UPDATE ... WHERE` |
| Python sync | thread release on I/O | entire handler to `commit()` | `select_for_update`, `F()` |
| Go | goroutine preemption | any point | `tx` + `FOR UPDATE`, atomic update |
| Rails | thread I/O release | `find`→`update!` | `transaction`+`lock`, `update_counters` |
| PHP | FPM workers truly parallel | between `query()` calls | `FOR UPDATE`, `ON DUPLICATE` |
| Java/JPA | thread pool + dirty flush | method body to commit | `PESSIMISTIC_WRITE`, `Version` |
| Serverless | concurrent containers | between datastore calls | conditional write only |
| async Python | `await` schedules coroutine | between awaits | `transaction()` + `FOR UPDATE` |
