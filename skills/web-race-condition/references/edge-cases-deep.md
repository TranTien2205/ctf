# Edge cases deep — the exhaustive boundary catalogue

Every boundary shape where the standard playbook fails, reads wrong, or lies —
expanded.

---

## 1. Server-can't-parallelize cases

### 1a. The single-worker app

gunicorn `workers=1`, a dev server, a single-threaded framework — HTTP requests
serialize at the accept queue.

- **Detect**: two calls to a slow endpoint take `2×` the delay serially.
- **Route**: race the layer below — two replicas on a shared DB, a background
  worker, or the app's own queries interleaving at the DB.

### 1b. The multiplexed-client lie

N requests over one keep-alive connection serialize at the client or a
per-connection lock.

- **Detect**: `max_in_flight` = 1 despite `--concurrency 20`.
- **Fix**: `--concurrency N` opens N connections.

### 1c. The worker-pool ceiling

`--concurrency 50` against a 4-worker pool — only 4 run at once, the rest
queue.

- **Detect**: `max_in_flight` caps at the pool size.
- **Route**: `--concurrency` = worker count, or race the DB layer.

## 2. Gate-before-handler cases

### 2a. The rate limiter

A per-IP/per-session limiter `429`s the burst before the handler.

- **Detect**: `429`/`403` dominate; `max_in_flight` on the handler is low.
- **Route**: the limiter is check-then-act — race it, or stay under with a
  tighter interleave.

### 2b. The CSRF/origin gate

A per-request token or origin check — the burst carries a consumed token.

- **Detect**: `403`/`invalid_token` on raced but not serial.
- **Route**: race the token issuer, or use a burst-valid token / a
  SameSite-missing cookie flow.

### 2c. The replay-cache

The endpoint caches responses by request hash — the second `200` is a replay.

- **Detect**: byte-identical `200`s, no doubled state.
- **Route**: read the state — a replay produces no second effect; falsifier.

## 3. Target-shape cases

### 3a. The consumed one-shot

The resource is consumed on first use — the SSOS startup-flag, a one-time
code, a singleton prize.

- **Detect**: the first attempt (yours or a prior player's) consumed it.
- **Route**: confirm freshness *before* firing; one-shot means one shot.

### 3b. The wrong-actor trap

The resource is global but the check is per-account — racing one session hits
the account dedup.

- **Detect**: one-session race gives no cross; two sessions does.
- **Route**: two cookie jars behind a shared barrier.

### 3c. The read-only endpoint

A `GET` with no check-then-act — nothing to interleave.

- **Route**: inventory writable endpoints; the shared state must change.

## 4. Timing/clock cases

### 4a. The clock-skew window

The window's position depends on server-clock vs client-clock — an expiring
token, a deadline.

- **Detect**: results correlate with the arrival second, not the order.
- **Route**: fire the burst across the boundary second; or a
  not-yet-valid token used a second early.

### 4b. The marginal-window flakiness

Results differ run to run — the window is a coin-flip.

- **Route**: re-roll with `--reset-url`; widen the window (pathological
  input) until marginal becomes reliable.

## 5. Half-state cases

### 5a. The partial commit

A request crashed mid-window — read committed, write didn't, or vice versa.

- **Detect**: a `500`/timeout on one slot + a state that's neither pre- nor
  post- value.
- **Route**: the half-state is a finding (non-atomic commit) — record it,
  reset, discard the timeout slot.

### 5b. The retry-that-reads-post-commit

SERIALIZABLE aborts a loser and the app retries — the retry reads the
committed state and *correctly* declines.

- **Detect**: two `200`s but the second's state shows it read the *new*
  value — serial-possible.
- **Route**: that's the defence working — a falsifier, not a race.

## 6. Cross-layer cases

### 6a. The stale-read shadow

A `GET` reads a cache the `POST` invalidates — returns the pre-write value
post-commit.

- **Detect**: `GET` returns `verified:true` after `POST /revoke` 200.
- **Route**: a *stale-read* race — `--url-b` GET + POST; the fix is
  write-through, not a lock.

### 6b. The replica-lag read

A read-replica serves the pre-write value — a lag window.

- **Detect**: reads against the replica lag the primary.
- **Route**: race the lag — a write on the primary, a read on the replica
  inside the lag.

### 6c. The cross-service window

Service A validates service B's state over HTTP — no shared lock exists.

- **Detect**: the "check" crosses a service boundary.
- **Route**: race two requests that each trigger the cross-service flow.

## 7. The "not actually a race" cases

### 7a. The logic flaw in race's clothing

`if (balance>=0) withdraw(-100)` — the check itself is wrong; it works
serially.

- **Detect**: the "win" reproduces serially in baseline.
- **Route**: `web-logic-flaw`, not this skill — classify first.

### 7b. The normal double-response

The endpoint always returns `200` to a replay, or `200`-then-`200` is the
normal flow.

- **Detect**: the signature is in baseline.
- **Route**: the serial set already contains it — not a race.

### 7c. The idempotent-safe endpoint

The endpoint is designed idempotent — a duplicate request is a no-op.

- **Detect**: `Idempotency-Key` dedup, or `ON CONFLICT DO NOTHING`.
- **Route**: a falsifier — the dedup closes the window.

## The edge → route table

| Edge | Route |
|---|---|
| single worker | race the DB / worker layer |
| multiplexed client | `--concurrency` opens N conns |
| worker ceiling | match `--concurrency` to pool |
| rate limiter | race it or under-limit interleave |
| CSRF/origin | race the issuer / valid token |
| replay cache | read state — falsifier |
| one-shot | confirm freshness first |
| wrong actor | two sessions, one barrier |
| read-only | not a race — reclassify |
| clock-skew | fire across the boundary |
| marginal window | re-roll + widen |
| half-commit | finding — record, reset |
| retry-post-commit | falsifier |
| stale-read | `--url-b` GET + POST |
| replica lag | primary-write vs replica-read |
| cross-service | race two cross-service triggers |
| logic flaw | `web-logic-flaw` |
| normal double | in serial set — not a race |
| idempotent | falsifier |
