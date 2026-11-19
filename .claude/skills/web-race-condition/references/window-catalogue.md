# Window catalogue — every place a check→act gap can open

The exhaustive inventory of *where* the separation happens, organized by the
code construct that creates the gap.

---

## 1. The two-statement gap

The canonical window: a `SELECT` and an `UPDATE`/`INSERT` as two separate
statements, no transaction.

```python
row = db.execute("SELECT used FROM codes WHERE code=?", code)   # stmt 1
if not row.used:
    db.execute("UPDATE codes SET used=1 WHERE code=?", code)     # stmt 2 — autocommit each
```

- **Width**: one round-trip between statements.
- **Where**: any autocommit pair.

## 2. The ORM unit-of-work gap

```python
obj = Model.query.get(id)          # SELECT — attached to session
if obj.field:
    obj.field = new
    db.session.commit()            # UPDATE at commit — the whole body is the window
```

- **Width**: the entire handler body — the widest code-level window.
- **Where**: Django `obj.save()`, SQLAlchemy `session.commit`, JPA dirty-flush,
  ActiveRecord `obj.save`.

## 3. The async-await gap

```javascript
const row = await db.get('SELECT ...')     // yield — the other request runs
if (!row.used) {
    await db.run('UPDATE ...')              // yield — again
}
```

- **Width**: each `await` is a deterministic yield — the other request runs
  right there.
- **Where**: Node, asyncio, any `async`/`await` chain.

## 4. The multi-function gap

```python
def handler():
    balance = get_balance(uid)      # read in one function
    if balance >= amt:
        debit(uid, amt)             # write in another — the call between is the window
```

- **Width**: the whole call chain between the two functions.
- **Where**: any read-helper + write-helper split.

## 5. The external-call gap

```python
token = mint(new_email)                     # read/mint
db.commit()                                  # commit
sendEmail(profile.email, token)              # the external call INSIDE the window
#        ^ re-reads the address — a second request's commit lands between
```

- **Width**: ms to seconds — the widest, most reliable window.
- **Where**: `sendEmail`, `mail`, `fetch`, `webhook`, `requests.get`,
  `render`, `pdf`, `notify` — between the commit and the re-read.

## 6. The multi-query gap

```python
a = db.execute("SELECT * FROM t1 WHERE ...")     # read table A
if a.ok:
    b = db.execute("SELECT * FROM t2 WHERE ...") # read table B to validate
    db.execute("UPDATE t1 SET ...")               # write table A
```

- **Width**: the extra round-trip.
- **Where**: validate-against-another-table — the validation read is unlocked.

## 7. The cache-invalidation gap

```python
# write path
db.execute("UPDATE user SET verified=false WHERE id=?")
cache.delete(f"user:{id}")          # the invalidate is AFTER the write — a GET can hit the stale cache
```

- **Width**: the invalidate-write ordering — a `GET` between the write and the
  delete returns the stale value.
- **Where**: cache-aside where the invalidate isn't inside the write's txn.

## 8. The request-flow gap

```text
step1 POST /cart/add     → session.cart
step2 POST /checkout     → compute total → order
step3 POST /pay          → charge order.total
```

- **Width**: the whole inter-request flow — the widest window of all.
- **Where**: multi-step checkouts, wizards, OAuth flows, 2FA enrol.

## 9. The worker-claim gap

```python
job = db.execute("SELECT * FROM queue WHERE status='pending' LIMIT 1")   # read
db.execute("UPDATE queue SET status='running' WHERE id=?", job.id)        # write
execute(job)
```

- **Width**: between the claim-read and the claim-write.
- **Where**: any job queue without `SKIP LOCKED`.

## 10. The check-then-use (filesystem) gap

```python
if os.path.exists(path):                # check
    open(path, 'w').write(data)          # use — the path re-resolves
```

- **Width**: between the `exists` and the `open` — a symlink swap lands.
- **Where**: temp files, upload paths, archive extraction.

## 11. The token-rotation gap

```python
new_token = mint()
db.execute("UPDATE tokens SET current=?", new_token)     # store new
db.execute("DELETE FROM tokens WHERE token=?", old_token) # invalidate old — after the store
```

- **Width**: between the new store and the old invalidate — the "dead" token
  lives.
- **Where**: refresh-token rotation, session rotation.

## 12. The constraint-free-check gap (structural)

```sql
-- the check exists ONLY in app code; the schema has no backing constraint
CREATE TABLE votes (user_id INT, post_id INT);   -- no UNIQUE(user_id,post_id)
```

```python
if not Vote.query.filter_by(user=u, post=p).first():   # code check
    db.session.add(Vote(user=u, post=p))                # insert
```

- **Width**: structural — the gap can never close at the DB.
- **Where**: any code-level `if not exists` with no backing constraint.

## 13. The replica-lag gap

```text
write goes to the primary; a read hits a lagged replica → returns pre-write
```

- **Width**: the replication lag — ms to seconds.
- **Where**: read-replica routing, read-your-writes violations.

## 14. The lock-scope gap

```python
lock.acquire()
# ... but the lock was acquired AFTER the read, or released BEFORE the write
read(); lock.release(); write()          # the window is before-acquire / after-release
```

- **Width**: the un-locked portion of the read→write.
- **Where**: a lock that doesn't span the whole critical section.

## The gap → width → exploit table

| Gap | Width | Best delivery |
|---|---|---|
| two-statement | ~ms | burst |
| ORM unit-of-work | whole handler | burst |
| async-await | per-await | burst or interleave |
| multi-function | call-chain | interleave |
| external-call | ms-seconds | burst — reliable |
| multi-query | round-trip | burst |
| cache-invalidate | ordering | `--url-b` GET+POST |
| request-flow | whole flow | `--url-b` steps |
| worker-claim | claim gap | two triggers |
| fs check-then-use | syscall pair | rename/symlink loop |
| token-rotation | store↔invalidate | interleave |
| constraint-free | structural | any — always open |
| replica-lag | ms-seconds | primary-write vs replica-read |
| lock-scope | un-locked span | race the un-locked part |
