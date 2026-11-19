# Detection — where to look, what to look for, first probes

Race conditions hide in the gap between a check and a commit. Detection is
finding the gap — in source, in the endpoint inventory, or in a timing probe —
not firing the race itself.

---

## 1. The endpoint inventory — where windows live

Sweep the app's writes first. A race needs a state change; read-only endpoints
have nothing to interleave.

| Endpoint shape | Check-then-act pattern | Alphabet row |
|---|---|---|
| `POST /redeem`, `/coupon`, `/claim`, `/invite/accept` | code read → grant → mark used | C, G, R |
| `POST /withdraw`, `/transfer`, `/pay`, `/convert` | balance read → debit | B, M, W |
| `POST /vote`, `/like`, `/react`, `/rate` | count read → insert → tally | D |
| `POST /register`, `/signup` | uniqueness read → insert | A, N |
| `POST /buy`, `/book`, `/reserve`, `/order` | stock read → decrement | H, T |
| `POST /verify`, `/confirm`, `/activate` | token read → grant → mark used | O, V |
| `POST /reset`, `/forgot` | token mint → send | per-check-token §2 |
| `POST /profile`, `/settings`, `/email` | field update → re-read → notify | E, P, X |
| `POST /login`, `/session` | session policy read → insert | S |
| `POST /upload`, `/import`, `/create` | exists check → write file/row | F |
| `POST /otp`, `/2fa`, `/pin` | attempts read → increment → compare | L, O |
| `GET /callback` (oauth) | state read → exchange → delete | per-check-token §6 |
| `POST /keys/rotate`, `/token/refresh` | current read → rotate | per-check-token §8 |
| any `POST` with a limit ("only 3 allowed") | count read → conditional insert | J, L |

Grep the front-end bundle and source for these route names:

```bash
grep -rniE '(redeem|coupon|voucher|claim|withdraw|transfer|vote|like|react|book|reserve|order|verify|confirm|activate|reset|forgot|invite|register|signup|quota|limit|attempt|stock|balance|credit|redeem|spin|draw|lottery|daily|reward)' \
  "$SRC" --include='*.js' --include='*.ts' --include='*.py' --include='*.rb' --include='*.go' --include='*.php' -l
```

## 2. The source tells — two reads of the same record

The reliable signature is a **read and a write on the same record across a
boundary**: two awaits, two functions, or two statements with work between.

```python
# grep for the gap shapes in source
grep -rnE '(SELECT|\.get\(|\.find|\.first\(|query\()' "$SRC" -A8 \
  | grep -nE '(UPDATE|INSERT|\.save|\.commit|\.flush|send|email|render|fetch)'

# the classic: read → decide → work → write
balance = get_balance(uid)          # read
if balance >= amt:                  # decide
    notify()                        # work — the window's width
    set_balance(uid, balance-amt)   # write
```

Per-language tells:

| Language | The gap looks like |
|---|---|
| Python/SQLAlchemy | `.first()` / `.get()` → attribute change → `session.commit()` |
| Node/Sequelize | `await findOne` → `await update`/`save` |
| Node/raw | `await db.get` → `await db.run` |
| Go | `tx.QueryRow` → `tx.Exec`, or worse: two separate `db.` calls |
| Rails | `find` → attribute set → `save` outside `transaction` |
| PHP | `SELECT` → `if` → `UPDATE` with intervening `mail()` |
| Java/JPA | `em.find` → setter → implicit flush at commit |

The work between read and write is what makes the window winnable: `send*`,
`mail`, `fetch`, `render`, `pdf`, `template`, `sleep`, a second `SELECT`.

## 3. The missing-constraint tell

The structural signal: the check exists **only in application code**.

```sql
-- schema has NO unique constraint on the thing the code checks
CREATE TABLE votes (user_id INT, post_id INT);            -- no UNIQUE(user_id,post_id)
CREATE TABLE codes (code TEXT, used BOOL);                -- no partial unique on used
CREATE TABLE users (email TEXT, password TEXT);           -- no UNIQUE(email)
```

Read the schema/migrations before probing: a code-level `if not exists` with no
backing constraint means the window *cannot* close at the DB layer — the race
is only a matter of landing timing.

## 4. The transaction tell

Search for whether the read+write share a transaction:

```bash
grep -rnE '(BEGIN|transaction|atomic|FOR UPDATE|SERIALIZABLE|LOCK|unique|UNIQUE)' "$SRC" | grep -iv node_modules
```

- **No `transaction`/`BEGIN` around the pair** → autocommit; each statement its
  own window.
- **`FOR UPDATE` / `SELECT ... LOCK`** → the read takes a lock; the window is
  closed for that row. This is the falsifier.
- **`SERIALIZABLE`** → the DB aborts a loser; still check the app retries —
  an aborted request that returns 500 without retry is a DoS, not a bypass.

## 5. The timing probe — measuring the window without racing

Before spending the write budget, measure whether a window exists at all.

The PhantomFeed technique: a pathological input that stalls the check. An
input that makes validation slow widens the gap measurably.

```bash
# time a normal input vs a pathological one — the delta is the window width
for i in 1 2 3; do
  curl -s -o /dev/null -w '%{time_total}\n' -X POST "$BASE/profile" \
    -d '{"email":"a@b.co"}' -H 'Cookie: session=...'
done
for i in 1 2 3; do
  curl -s -o /dev/null -w '%{time_total}\n' -X POST "$BASE/profile" \
    -d '{"email":"a@abcdefghijklmnopqrstuvwxyz!"}' -H 'Cookie: session=...'
done
```

A consistent ms-scale delta between arms means the check itself is slow — the
window is wide enough to land in without exotic timing.

## 6. The response-shape tell

Responses that name a check the app did separately from the write:

| Response | What it reveals |
|---|---|
| `{"error":"already used"}` on second serial redeem | the check exists; whether it's atomic is the question |
| `409 Conflict` / `insufficient funds` | a check ran — now find if it's in the same statement |
| a success that includes the *prior* state (`"remaining":0`) | the read and the act are visibly separate |
| `Set-Cookie` with a fresh session on every login | no session-count check at all (closed) or one worth racing |

## 7. Multi-step flows — the widest windows

The widest windows live across HTTP boundaries, where "the transaction" is a
multi-request flow held in session state:

- **Cart → checkout → pay**: price read at cart, charged at pay — modify the
  cart mid-payment.
- **Register → verify → activate**: state carried between requests; race the
  steps.
- **OAuth authorize → callback**: state/nonce consumed at callback.
- **2FA enrol → confirm**: the secret sits half-configured.

These are checked the same way: find where step N reads what step N-1 wrote,
and whether a parallel request can rewrite it mid-flow.

## 8. The triage decision

| Finding | Route |
|---|---|
| code-level check, no DB constraint, read+write separated | race it — `race_probe` |
| atomic `UPDATE ... WHERE` or `FOR UPDATE` | falsifier — record, move on |
| multi-request flow with session state | map the steps, find the shared record |
| write path safe but a slow check | timing-oracle pathological input |
| nothing writable in the endpoint inventory | not a race target — reclassify |

The classify gate: `python3 tools/classify.py "<obs>"` and
`python3 tools/chain_match.py --source <dir> --record <name>` run before this
skill — a matching card hands back the probe that already worked.
