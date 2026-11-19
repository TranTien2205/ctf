# Detection surface — the complete map of where to look

The exhaustive surface: every place a check-then-act gap can hide, grouped by
the kind of shared state. The detection-side mirror of `per-surface.md`.

---

## 1. The request-parameter surface

Every endpoint where the request names a record the app reads then writes.

```bash
# the candidate routes — writable + checked
grep -rnE '(post|put|patch|delete)' "$SRC" -l | xargs grep -lnE \
  '(SELECT|\.get\(|findOne|QueryRow|objects\.get|em\.find)' | \
  xargs grep -lnE '(UPDATE|INSERT|commit|save|Exec|flush)'
```

| Parameter surface | The window |
|---|---|
| `?code=`/`{code}` | the code's `used` flag |
| `?id=`/`/obj/:id` | the object's checked field |
| `{amount}`/`{qty}` | the balance/stock check |
| `{username}`/`{email}` | the uniqueness check |
| `{token}`/`{code}` | the consume-once flag |
| `{vote}`/`{dir}` | the count/direction check |

## 2. The session-record surface

The shared record is per-session or per-flow — a cart, a draft, a pending
action.

```bash
grep -rnE '(session\.|req\.session|sessionStore|cart|draft|pending|order\.|checkout|flow_state|wizard)' "$SRC"
```

| Session record | The race |
|---|---|
| `session.cart` | `cart/add` racing `pay` |
| `order.draft` | an edit racing the submit |
| `user.pending_change` | two steps sharing the pending record |
| `session.registration` | register-step racing verify-step |
| `session.oauth_state` | two callbacks on one state |

## 3. The actor surface

The "other request" is a system actor — a bot, a job, an importer, another
player.

```bash
grep -rniE '(bot|admin|headless|puppeteer|selenium|visit|report|registerUser|startup|seed|fixture|cron|celery|sidekiq|worker|consumer|schedule)' "$SRC"
```

| Actor | The race |
|---|---|
| a bot's startup register | register the fixed account first |
| a scheduled job's claim | a second claim racing the worker's |
| an importer/seeder | your record racing the seed record |
| another player | a global prize two players both claim |
| a webhook/callback | fire the callback mid-request |

## 4. The data-layer surface

The shared state is below the app — DB, cache, index, replica.

```bash
grep -rnE '(cache\.|redis\.|memcache|read_replica|replica|search_index|elasticsearch|counter|sequence|increment)' "$SRC"
```

| Layer | The race |
|---|---|
| a cache key | `GET` racing the write+invalidate |
| a read-replica | a primary-write vs a lagged replica-read |
| a counter/sequence | the read-compute-write lost update |
| a search index | the index-update lag vs a query |

## 5. The external-resource surface

The shared state is outside the app entirely.

| Resource | The race |
|---|---|
| a file path | `exists` → `open` |
| a mailbox | `mint` → `send` (the cross) |
| an external API | `check-remote` → `act` |
| a payment provider | `authorize` → `capture` |
| a DNS record | `resolve-check` → `connect` (rebind) |
| a certificate/ownership | `check TXT` → `mark verified` |

## 6. The concurrency-primitive surface

The window is inside the synchronization itself.

```bash
grep -rnE '(mutex|lock|semaphore|ratelimit|throttle|idempot|dedup|version|fence|watch)' "$SRC"
```

| Primitive | The race |
|---|---|
| a rate limiter | `attempts < max` → `++` |
| a dedup key | `exists(key)` → `insert(key)` |
| a lock/semaphore | `check-held` → `act` |
| a version column | `version=7` → `update where version=7` |
| a fencing token | `token=old` → `act` |

## 7. The multi-request-flow surface

The "transaction" is a flow across requests.

```bash
grep -rnE '(step|stage|wizard|checkout|confirm|finalize|complete|submit|approve)' "$SRC"
```

| Flow | The race |
|---|---|
| cart → checkout → pay | `pay` racing `cart/add` |
| register → verify → activate | step-N racing step-M |
| oauth authorize → callback | two callbacks on one state |
| enrol → confirm (2fa) | the half-configured secret |

## 8. The surface-detection checklist

```text
□ every writable endpoint that takes a record id/code/amount
□ every session-record the flow carries
□ every system actor (bot, job, worker, importer)
□ every data-layer store (cache, replica, counter, index)
□ every external resource (file, mailbox, API, DNS, cert)
□ every synchronization primitive (lock, limiter, dedup, version)
□ every multi-step flow's shared record
```

## 9. The surface → probe table

| Surface | Probe |
|---|---|
| request-parameter | `race_probe` on the endpoint |
| session-record | `--url-b` two flow steps |
| actor | timing race vs the actor's schedule |
| data-layer | `--url-b` read vs write |
| external-resource | raw-socket stall or `--url-b` |
| concurrency-primitive | race the primitive itself |
| multi-request-flow | `--url-b` step-N + step-M |
