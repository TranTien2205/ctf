# Edge cases — the boundary shapes that break the normal playbook

The cases where the standard "burst the endpoint" advice fails or lies.

---

## 1. The single-worker server — no HTTP parallelism

**Shape**: gunicorn `workers=1`, a dev server, a single-threaded app.

Two requests can never overlap at the handler — they serialize at the accept
queue. The HTTP race is structurally impossible.

- **Detect**: two calls to a slow endpoint take `2×` the delay serially.
- **Route**: race the layer below — two replicas sharing a DB, a background
  worker, or the app issuing two queries that interleave at the DB. A
  single-worker app on a *shared* DB still races at the query boundary.

## 2. The multiplexed-client lie — one connection, serial responses

**Shape**: you send N requests over one keep-alive connection and read the
responses in order.

HTTP/1.1 pipelines answer in order; many frameworks hold a per-connection
lock. The requests look parallel on the wire and run serial in the handler.

- **Detect**: `max_in_flight` = 1 despite `--concurrency 20`.
- **Fix**: one request per connection; `--concurrency N` opens N connections.

## 3. The worker-pool ceiling — concurrency > workers

**Shape**: `--concurrency 50` against a 4-worker FPM pool.

Only 4 handlers run at once; the rest queue. `max_in_flight` will read the
pool ceiling, not 50 — the burst is really 4 overlapping + 46 queued.

- **Detect**: `max_in_flight` caps at the worker count.
- **Route**: `--concurrency` = worker count; or race the DB where the queries
  queue anyway and interleave at the DB.

## 4. The rate-limited endpoint — the race is throttled away

**Shape**: a per-IP or per-session rate limiter answers `429` to the burst
before the handler runs.

- **Detect**: `429`/`403` responses dominate; `max_in_flight` on the real
  handler is low.
- **Route**: the limiter is itself a check-then-act — race *it* (the counter
  race), or find the limit it enforces and stay under it while still
  overlapping. A `429` on the loser is the limiter doing its job, not the
  target defence.

## 5. The CSRF/origin gate — the second request is rejected

**Shape**: a per-request CSRF token or origin check — the burst carries a
stale/consumed token.

- **Detect**: `403`/`invalid_token` on every raced request but not on serial.
- **Route**: the CSRF token is single-use → the race is on the *token*; race
  the endpoint that issues it, or use a token that's valid for the whole
  burst, or a SameSite-missing cookie-based flow (the SSOS shape).

## 6. The idempotent/response-cache endpoint — the 200 is a replay

**Shape**: the endpoint caches its response by request hash or returns a
stored result — the second `200` is a cached replay, not a second effect.

- **Detect**: identical `200` bodies byte-for-byte; the *state* didn't change
  (inventory didn't double).
- **Route**: read the state, not the status. Two identical `200`s with no
  doubled effect is a replay cache, not a race — falsifier for the class at
  that endpoint.

## 7. The consumed-target trap — one-shot resources

**Shape**: the resource is consumed on first use and cannot be re-rolled —
the SSOS startup-flag, a one-time code, a singleton prize.

- **Detect**: the first attempt (yours or a prior player's) consumed it.
- **Route**: confirm the target is *fresh* before firing; a consumed instance
  is unrecoverable. This is a blast-radius check, not a probe — check
  freshness first, race once.

## 8. The partial-failure ambiguity — one request half-committed

**Shape**: request A's handler crashed mid-window — the read committed, the
write didn't, the state is half-updated.

- **Detect**: a `500`/`timeout` on one slot plus a state that's neither the
  pre- nor the post- value.
- **Route**: the half-state is itself a finding (a non-atomic commit) — record
  it, reset with `--reset-url`, and treat the slot's timeout as *unknown*, not
  success or failure.

## 9. The clock/timing-skew variant — the window moves

**Shape**: the window's position depends on clock skew between client and
server (an expiring token, a deadline).

- **Detect**: results correlate with the request's arrival second, not its
  order.
- **Route**: pin the timing — race *within* the window by controlling the
  server's view of time (a not-yet-valid token used a second early), or find
  the boundary second and fire the burst across it.

## 10. The two-account trap — the actor isn't the resource

**Shape**: the resource is global (one code, one seat) but the check reads a
*per-account* flag (`user.claimed`).

Two requests from the *same* account both pass `!user.claimed` — but the bug
needs two different actors on the global resource. Same-session racing gives
a false negative (the account-level dedup held).

- **Detect**: racing one session produces no cross; racing two sessions does.
- **Route**: two cookie jars, one shared barrier — `--url-b` or two probes
  behind a sync point.

## 11. The stale-cache shadow — the read that lies

**Shape**: a `GET` reads a cache the `POST` invalidates — the read returns
the pre-write value even *after* the write commits.

- **Detect**: `GET` returns `verified:true` after `POST /revoke` returned 200.
- **Route**: this is a *stale-read* race, not a double-write — `--url-b`
  `GET` + `POST`. The fix is write-through or versioned keys, not a lock.

## 12. The retry-storm false positive — the app retries a loser

**Shape**: SERIALIZABLE aborts a loser and the app/framework auto-retries —
the retried request sees the committed state and *succeeds*.

- **Detect**: two `200`s but the second's state shows it read the *new* value
  (the retry saw the commit) — serial-possible, not crossed.
- **Route**: check *what* the second 200 read. A retry that reads post-commit
  state is the defence working, not a race — falsifier.
