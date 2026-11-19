# White-box hunt — finding the window in source, with file and line

White-box is the fast path: the window is a code pattern, and grep finds it
faster than any probe. The deliverable is a named read→write pair with the
constraint audit that says it's open.

---

## 1. The grep ladder — from route to record

```bash
# 1. the write endpoints
grep -rnE '(post|put|patch|delete)\s*\(|@(app|router|bp)\.(post|put|patch|delete)|urlpatterns|Route::' "$SRC" \
  | grep -vE '(test|spec|mock|fixture)'

# 2. inside those handlers: a read and a write on the same record
grep -rnE '(SELECT|\.get\(|\.find|\.first|\.filter|findByPk|findOne|QueryRow|em\.find|objects\.get)' "$SRC" -A 12 \
  | grep -B4 -A8 -E '(UPDATE|INSERT|DELETE|\.save|\.commit|\.flush|\.update|Exec|persist|update!)'
```

For each pair found, answer: same record? work between them? atomic or
constraint-backed?

## 2. The constraint audit — the strongest signal

```bash
# read the schema — does anything back the app-level check?
grep -rniE '(unique|primary key|constraint|check\s*\(|index|create table)' \
  "$SRC"/**/migrations "$SRC"/**/schema* "$SRC"/**/*.sql 2>/dev/null
```

| Schema | Verdict |
|---|---|
| `UNIQUE` on the raced field | closed — falsifier |
| `CHECK (balance >= 0)` | closed for the negative-balance race |
| partial `UNIQUE ... WHERE used` | closed for single-use |
| no constraint + code-level `if` | **open — the window is structural** |

The code-only check is the gold: the window can never close at the DB, so
winning is only a timing problem.

## 3. The transaction audit

```bash
grep -rnE '(BEGIN|transaction|atomic|autocommit|isolation|FOR UPDATE|LOCK|SERIALIZABLE|REPEATABLE)' "$SRC" | grep -v node_modules
```

| Observed | Window |
|---|---|
| two statements, no `BEGIN` | autocommit — open |
| `BEGIN` + non-locking read + write | still open at READ COMMITTED |
| `FOR UPDATE` / `select_for_update` on the read | closed |
| `SERIALIZABLE` | closed; check retry handling |
| multi-statement with `await`/`yield` inside | open — every yield is a schedule point |

## 4. The work-in-window grep — what widens it

```bash
grep -rnE '(SELECT|\.get\(|findOne|QueryRow)' "$SRC" -A 10 | grep -nE \
  '(send|email|mail|smtp|fetch|request|http|render|template|pdf|compile|sleep|delay|notify|webhook|call|await |\.then)'
```

Every `send`/`fetch`/`render`/`sleep`/`await` between the read and the commit
is window width. A `sendEmail` between `SELECT` and `UPDATE` is the
ApexSurvive shape.

## 5. Per-language gap patterns

### Python — the ORM commit-at-end

```python
# grep this shape
obj = Model.query.get(id)          # read — attached
if obj.field: ...
    db.session.commit()            # write — everything between is window

# closed forms to falsify
with db.session.begin(): Model.query.with_for_update().get(id)
Model.query.filter(Model.id==id, Model.bal>=amt).update({'bal': Model.bal-amt})
```

### Node — the await chain

```javascript
// grep: findOne/findByPk/get then update/save/run, with an await between
const u = await M.findByPk(id);           // yield #1
if (u.x) { await work(); await u.update(); }  // yield #2 — the gap
```

### Go — db. vs tx.

```go
// grep for db.QueryRow + db.Exec (two different pooled connections — widest)
db.QueryRow("SELECT ...").Scan(&v)   // no tx
if v { db.Exec("UPDATE ...") }         // separate conn — gap
// vs tx.QueryRow + tx.Exec (one conn, still non-locking at READ COMMITTED)
// vs tx.QueryRow("... FOR UPDATE") — closed
```

### Rails

```ruby
# find → update! outside transaction
u = M.find(id); u.update!(f: v)
# closed: M.transaction { M.lock.find(id) }; M.update_counters / update_all
```

### PHP

```php
// two ->query() calls, no transaction, work between
$r = $db->query("SELECT ..."); if (...) { mail(...); $db->query("UPDATE ..."); }
```

### Java/JPA

```java
// em.find attached + dirty-checking flush at commit
Account a = em.find(Account.class, id); a.setBalance(...);   // method body is window
// closed: @Lock(PESSIMISTIC_WRITE), @Version, bulk UPDATE
```

## 6. The multi-table window

```text
validate against table A (unlocked read) → write table B
```

`FOR UPDATE` only locks the row actually selected. A validation read of a
*different* table is unlocked — two transactions both validate and both write.
Grep for a `SELECT` on one table feeding an `if` that gates an `INSERT`/`UPDATE`
on another.

## 7. The async-boundary hunt

```bash
grep -rnE 'await |yield |\.then\(|async def|go func|goroutine|Thread|executor|Promise' "$SRC" \
  | grep -v node_modules | grep -B2 -A2 -E '(SELECT|UPDATE|INSERT|commit|save|Exec|QueryRow)'
```

Every yield between the read and the write is where the other request
schedules. In an async/Node handler the count of `await`s between `find*` and
`update`/`save` is roughly the number of chances the other request gets.

## 8. The session-state flow hunt

```bash
grep -rnE '(session\.|req\.session|session\[|sessionStore|cart|order\.|checkout|pay|draft|pending)' "$SRC"
```

Find the record that carries state across requests — `session.cart`,
`order.draft`, `user.pending_action`. Then find which step reads it and which
writes it. The race is two requests crossing on that record mid-flow.

## 9. The bot/actor hunt — the SSOS shape

```bash
grep -rniE '(bot|admin|headless|puppeteer|selenium|visit|report|registerUser|startup|seed|fixture)' "$SRC"
```

Find a fixed/seeded actor: a bot that registers a known account at startup, a
seeded admin, a scheduled job. Racing to own the identity *before* the actor
claims it is the SSOS primitive — the highest-value race because the actor
then does privileged work on your account.

## 10. The hunt deliverable

```text
endpoint:    POST /api/profile            (app.py:142)
window:      token minted L148 → UPDATE email L152 → sendEmail(re-read) L160
gap:         sendEmail between commit and re-read; two functions
constraint:  no UNIQUE(email), no FOR UPDATE — open
falsifier:   none — proceed to baseline + raced run
actor:       none — not an SSOS shape
```

That record goes into `state.py` as the hypothesis with the file:line —
`classify.py --source` already wrote the class; the hunt adds the mechanism.
