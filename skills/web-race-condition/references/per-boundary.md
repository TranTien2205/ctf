# Per-boundary — which layer the window lives in

A race window exists at exactly one boundary. Identify the layer first — the
tool, the timing, and the fix are all layer-specific.

---

## 1. The HTTP-request boundary (the common case)

Two HTTP requests to the same app, each doing a read-then-write in its handler.
The window is the handler body.

- **Where**: any two `POST`s (or a `POST` and a `GET`) that touch the same record.
- **Tool**: `race_probe.py` burst or `--url-b` interleave.
- **Concurrency ceiling**: the server's worker pool (gunicorn workers, FPM
  children, thread pool) — the app can't run more handlers than it has workers.
- **Fix**: atomic statement / row lock / constraint.

## 2. The database boundary

The HTTP requests are serialized (single worker) but the *queries* interleave
at the DB — or two app replicas share one DB.

- **Where**: the DB is the shared mutable state; the app tier doesn't matter.
- **Tell**: two app instances/pods, or a single worker that issues queries to a
  shared DB — the race is at the query layer even if HTTP is serial.
- **Tool**: race the DB directly with two sessions, or send serial HTTP that
  the server *queues* but whose transactions still overlap at the DB.
- **Concurrency ceiling**: the DB's connection pool / max_connections.
- **Fix**: the isolation/lock answer — `FOR UPDATE`, atomic update, constraint.

## 3. The multi-request flow boundary

The "transaction" is a multi-step HTTP flow; state lives in a session/record
between steps.

```text
step1 POST /cart/add {item}        → session.cart = [item]
step2 POST /checkout               → reads cart, writes order{total}
step3 POST /pay                    → reads order.total, charges
```

The race is *across* steps — a `POST /cart/add` landing between `checkout`'s
price-compute and `pay`'s charge, or two `checkout`s reading the same cart.

- **Where**: the shared record (session, cart row, order row).
- **Tool**: `--url-b` — request A is step N, request B is a concurrent step M.
- **Fix**: the shared record must be versioned or locked across the flow; a
  price recomputed at pay-time closes the cart-modify race.

## 4. The request-vs-background boundary

The HTTP request enqueues work; a background worker (celery, sidekiq, cron, a
consumer) does the read-then-write. The race is request-vs-worker or
worker-vs-worker.

```text
request:  POST /job {args}  → INSERT job (pending)
worker:   poll → SELECT pending → mark running → execute
```

- **Where**: two workers claim the same job (no `SKIP LOCKED`), or a request
  that reads the job's result races the worker's write.
- **Tool**: `--url-b` racing the trigger against the worker poll, or two
  trigger requests racing to enqueue duplicate work.
- **Fix**: `SELECT ... FOR UPDATE SKIP LOCKED` for claims; idempotent workers
  for the rest.

## 5. The cache boundary

The read path hits a cache the write path updates — a stale-read race.

```text
GET /profile → cache.hit ? return : db.read + cache.set
POST /profile → db.write + cache.invalidate
```

A `GET` racing the `POST` can return the pre-write cached value *after* the
write committed — a stale-read window, or a cache-stampede (100 `GET`s miss
together and all hit the DB).

- **Where**: cache-aside (the app manages both) is the vulnerable shape.
- **Tool**: `--url-b` — race the read against the write+invalidate.
- **Fix**: write-through, versioned keys, or `cache.delete` before `db.write`
  (delete-then-write ordering still leaves a window; a proper close is
  versioned reads).

## 6. The filesystem boundary

A check-then-use on a file: `exists(path)` → `open(path)` — classic TOCTOU.

- **Where**: temp-file creation, upload validation, symlink/hardlink races.
- **Tool**: not `race_probe` — a tight rename/symlink loop against a local
  target, or two processes on a shared mount.
- **Fix**: `O_EXCL`, `open` on the fd from the check (not the path), atomic
  rename.

## 7. The distributed-system boundary

The strongest shape: no single lock spans the components.

```text
service A (billing) reads service B's (inventory) state over HTTP
A validates stock>0, then debits — B's stock was decremented concurrently
```

- **Where**: microservices, sagas, event-driven — the "transaction" spans
  services and can't lock.
- **Tool**: race two requests that each trigger the cross-service flow.
- **Fix**: the reservation/saga pattern, an idempotency key, or a conditional
  write at the data owner. There is no shared `FOR UPDATE`.

## 8. The session/cookie boundary

State carried in the request itself (a signed cookie, a JWT) — the "read" is
the token's claims, the "write" is a new token. Two requests with the same
token both validate against the pre-rotation claims.

- **Where**: token rotation, session fixation, JWT replay.
- **Tool**: race two requests carrying the same pre-rotation token.
- **Fix**: server-side token versioning / a denylist the read checks.

## 9. The boundary→tool→fix table

| Boundary | Shared state | Race tool | Close |
|---|---|---|---|
| HTTP request | app process | race_probe | atomic stmt / row lock |
| database | DB rows | 2 sessions / race_probe | isolation + lock |
| multi-request flow | session/order record | race_probe --url-b | version / recompute at commit |
| request-vs-worker | job queue | race_probe / 2 triggers | `SKIP LOCKED`, idempotency |
| cache | cache key | race_probe --url-b | write-through / versioned key |
| filesystem | file path | rename/symlink loop | `O_EXCL` / fd-from-check |
| distributed | two services | race two triggers | saga / conditional write |
| session/cookie | token claims | race 2 same-token reqs | server-side version |
