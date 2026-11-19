# Race catalogue — the complete endpoint-indexed reference

The master lookup: every endpoint shape in one table — the record raced, the
window, the probe, the crossed state, and the close.

---

## Money / value

| Endpoint | Record | Window | Probe | Crossed state | Close |
|---|---|---|---|---|---|
| `/withdraw`, `/debit` | `account.balance` | `SELECT` → `UPDATE` | burst amt=full | balance `-amt` | atomic `WHERE bal>=amt` |
| `/transfer` | `account.balance` | `SELECT` → `UPDATE` | burst amt=full | 2× amt out | atomic transfer |
| `/pay`, `/charge` | `account.balance` | `SELECT` → `UPDATE` | burst | overdraw | atomic |
| `/convert`, `/exchange` | `balance` + `rate` | `SELECT` ×2 → `UPDATE` | burst | 2× output | atomic |
| `/redeem`, `/coupon` | `code.used` | `SELECT` → grant → `UPDATE` | burst | 2 grants | `WHERE used=0` |
| `/claim`, `/airdrop` | `user.claimed` | `SELECT` → grant → `UPDATE` | burst | 2 claims | atomic claim |
| `/refund` | `order.refunded` | `SELECT` → `UPDATE` | `--url-b` vs charge | refund+charge | atomic |

## Limit / counter

| Endpoint | Record | Window | Probe | Crossed state | Close |
|---|---|---|---|---|---|
| `/vote`, `/like` | `votes(u,t)` + `post.score` | `SELECT` → `INSERT` + `UPDATE` | burst | +2 for 1 voter | `UNIQUE(u,t)` |
| `/rate`, `/react` | `reactions(u,t)` | `SELECT` → `INSERT` | burst | duplicate reaction | `UNIQUE` |
| `/otp`, `/2fa` | `otp.attempts` | `SELECT` → `++` → compare | burst > cap | attempts > cap | atomic `WHERE <cap` |
| `/rate-limit` | `attempts` counter | `SELECT` → `++` | burst past cap | > cap processed | atomic increment |
| `/spin`, `/daily` | `user.spun_today` | `SELECT` → `UPDATE` | burst | 2 spins | atomic claim |

## Identity / uniqueness

| Endpoint | Record | Window | Probe | Crossed state | Close |
|---|---|---|---|---|---|
| `/register`, `/signup` | `users.email` | `SELECT` → `INSERT` | burst fixed email | 2 rows / own the actor's acct | `UNIQUE(email)` |
| `/username/claim` | `names.name` | `SELECT` → `INSERT` | burst | 2 owners | `UNIQUE(name)` |
| `/invite/accept` | `invites.uses` | `SELECT` → `INSERT` | `--url-b` 2 sessions | 2 members on 1 invite | `UNIQUE` consume |
| `/team/join` | `team.members` count | `SELECT` → `INSERT` | `--url-b` 2 joins | over-cap team | group lock |

## Token / verification

| Endpoint | Record | Window | Probe | Crossed state | Close |
|---|---|---|---|---|---|
| `/verify`, `/confirm` | `token.used` | `SELECT` → grant → `UPDATE` | burst correct code | 2 grants | `WHERE used=0` |
| `/profile`, `/email` | `profile` + `token` | update → re-read → notify | `--url-b` 2 emails | token A→B | same-txn notify |
| `/reset`, `/forgot` | `resets.token` | invalidate → mint → store | interleave | 2 valid tokens | atomic rotate |
| `/oauth/callback` | `oauth.state` | `SELECT` → exchange → `DELETE` | burst same pair | 2 exchanges | atomic consume |
| `/keys/rotate` | `keys.current` | `SELECT` → mint → `UPDATE` + inv | interleave | old key lives | atomic rotate |
| `/login` | `sessions(user)` | `SELECT` → `INSERT` | burst | 2 sessions under 1-policy | `UNIQUE` session |

## Resource / inventory

| Endpoint | Record | Window | Probe | Crossed state | Close |
|---|---|---|---|---|---|
| `/buy`, `/order` | `items.stock` | `SELECT` → `INSERT` → `UPDATE` | conc=stock+1 | `stock=-1` | atomic `WHERE stock>0` |
| `/book`, `/reserve` | `seats.seat` | `SELECT` → `INSERT` | burst | seat sold 2× | `UNIQUE(seat)` |
| `/upload`, `/create` | `files.name` | `exists` → `save`/`INSERT` | burst same name | 2 files / overwrite | `O_EXCL`/`UNIQUE` |
| `/import` | `batch.items` | per-item read→write | read mid-batch | half-applied state | batch txn |

## Flow / multi-step

| Endpoint | Record | Window | Probe | Crossed state | Close |
|---|---|---|---|---|---|
| `cart → checkout → pay` | `order.total` | compute → charge | `--url-b` `pay` + `cart/add` | charge ≠ order | recompute at pay |
| `register → verify` | `session.reg` | step-N vs step-M | `--url-b` steps | a skipped step | step lock |
| `draft → submit` | `draft` record | edit racing submit | `--url-b` | submitted-draft mismatch | version |
| `enrol → confirm` | `2fa.secret` | half-configured | `--url-b` | a confirmed bad secret | atomic enrol |

## Job / queue / worker

| Endpoint | Record | Window | Probe | Crossed state | Close |
|---|---|---|---|---|---|
| `/job/trigger` | `queue.status` | `SELECT` → `UPDATE` | 2 triggers | job ×2 | `SKIP LOCKED` |
| `/worker/claim` | `queue.status` | `SELECT` → `UPDATE` | claim race | double-execute | `FOR UPDATE SKIP LOCKED` |
| `/export` | `report.data` | snapshot vs update | `--url-b` export + write | half-state export | txn / version |

## View / read (stale-read races)

| Endpoint | Record | Window | Probe | Crossed state | Close |
|---|---|---|---|---|---|
| `GET /api/me` | `user.verified` | cache/snapshot vs write | `--url-b` GET + revoke | verified:true post-revoke | write-through |
| `GET /api/account` | `account` cache | cache vs invalidate | `--url-b` GET + write | stale view | versioned key |
| a read-replica | replica lag | primary-write vs replica-read | `--url-b` | lagged "truth" | read-your-writes |

## Joint / multi-resource

| Endpoint | Record | Window | Probe | Crossed state | Close |
|---|---|---|---|---|---|
| `team/members/remove` | `A+B` joint cap | read A+B → dec A | `--url-b` dec A + dec B | A+B < floor | SERIALIZABLE / group lock |
| `pooled/withdraw` | pooled balance | `A+B` invariant | `--url-b` | pooled overdraw | group lock |
| `tenant/quota` | `sum(usage)` | joint quota | `--url-b` | quota exceeded | owner-lock |

## Concurrency primitives

| Endpoint | Record | Window | Probe | Crossed state | Close |
|---|---|---|---|---|---|
| the rate limiter | `attempts` counter | `SELECT` → `++` | burst it | more pass | atomic increment |
| an idempotency key | `ops.key` | `exists` → `insert` | 2 same-key | 2 effects | `UNIQUE(key)` |
| a lock/semaphore | `lock.held` | `check-held` → `act` | race acquire | both hold | real lock scope |
| a version column | `version` | `v=7` → `update where v=7` | race the version | a lost update | the version itself |
