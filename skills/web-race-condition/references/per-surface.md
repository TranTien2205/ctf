# Per-surface — the whole race surface, mapped

Every place a check-then-act window can live, organized by where the shared
state sits.

---

## 1. The application-record surface

The shared state is an app row — a user, an order, a code, a vote.

| Endpoint family | Shared record | The window |
|---|---|---|
| redeem/coupon/claim | the code row | `SELECT used` → `UPDATE` |
| withdraw/transfer | the balance column | `SELECT` → `UPDATE` |
| vote/like | the vote row + tally | `SELECT count` → `INSERT` + `UPDATE` |
| register | the user row | `SELECT email` → `INSERT` |
| buy/book | the stock/seat | `SELECT stock` → `UPDATE` |
| verify/otp | the token + attempts | `SELECT` → `UPDATE` ×2 |
| reset | the reset token | invalidate → mint → store |
| profile | the profile row | update → re-read → notify |
| login/session | the session row | `SELECT` → `INSERT` |
| invite/accept | the invite row | `SELECT uses` → `UPDATE` |
| upload/create | the file/name row | `exists` → `INSERT`/`save` |
| rotate/refresh | the key row | `SELECT` → `UPDATE` + invalidate |
| oauth callback | the state row | `SELECT` → `DELETE` |

## 2. The session-state surface

The shared state is a per-request-carried or per-session record — a cart, a
draft, a pending action, a cookie's claims.

| Flow | Shared record | The window |
|---|---|---|
| cart→checkout→pay | the cart/order row | compute-total vs commit-total |
| register→verify→activate | the pending-registration record | two steps sharing the draft |
| oauth authorize→callback | the state/nonce record | state consume vs a second callback |
| 2fa enrol→confirm | the half-configured secret | enrol writes, confirm reads |
| draft→submit | the draft record | an edit racing the submit |
| multi-tab checkout | the order record | two tabs racing the same order |

## 3. The data-layer surface

The shared state is below the app — the DB, a cache, a search index.

| Layer | Shared state | The window |
|---|---|---|
| DB rows | the row | `SELECT`/`UPDATE` gap — the base case |
| cache | the cached value | read-cache vs write+invalidate |
| search index | the indexed doc | index-update lag vs a query |
| a replica | the replica's lagged copy | read-replica staleness |
| a counter/sequence | the counter | read-compute-write lost update |

## 4. The external-resource surface

The shared state is outside the app — a file, an API, a mailbox.

| Resource | The window |
|---|---|
| a file path | `exists` → `open` — the fs TOCTOU |
| a mailbox | mint-token → send (the ApexSurvive cross) |
| an external API | check-remote-state → act |
| a payment provider | authorize → capture |
| a DNS/cert record | check-ownership → issue |

## 5. The concurrent-actor surface

The "other request" isn't yours — it's a system actor racing you, or you
racing it.

| Actor | The window |
|---|---|
| a bot's startup | register/seed a fixed account before the bot does |
| a scheduled job | the job's claim vs a second claim |
| a background worker | the worker's read-then-write vs a request |
| another player | a global resource two actors both consume |
| the importer/seeder | the seed record vs your registration |

## 6. The concurrency-primitive surface

The window is in the synchronization itself.

| Primitive | The window |
|---|---|
| a lock/mutex | check-held → act (the lock's scope) |
| a semaphore | acquire → release |
| a rate limiter | `attempts < max` → `++` |
| a dedup/idempotency key | `exists(key)` → `insert(key)` |
| a version column | `version=7` → `update where version=7` |

## 7. The surface → probe table

| Surface | Probe |
|---|---|
| app record | `race_probe` burst on the endpoint |
| session-state | `--url-b` two flow steps |
| DB/cache/replica | `--url-b` read vs write |
| external resource | raw-socket stall or `--url-b` |
| concurrent actor | timing race vs the actor's schedule |
| concurrency primitive | race the limiter/dedup itself |

## 8. The coverage checklist

```text
□ every writable endpoint inventoried
□ every endpoint's shared record named
□ every window's read→write pair found
□ every constraint/lock audited
□ the actor surface checked (bots, jobs, workers, other players)
□ the flow surface checked (multi-step records)
□ the data-layer surface checked (cache, replica, counter)
□ falsifier or crossed state recorded per endpoint
```
