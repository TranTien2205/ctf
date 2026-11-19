# Evasion — the defences that narrow but don't close, and how to get past them

Some defences make the race harder without closing the window. These are the
techniques for landing inside a narrow window.

---

## 1. Rate limiting — the race is throttled, not closed

A per-IP/per-session rate limiter rejects the burst with `429`s. The window in
the handler is still open — the limiter just gates how many requests reach it.

- **Race the limiter**: the limiter is itself a counter (`attempts < max →
  increment`) — a check-then-act. Burst the limiter's window so more requests
  pass it than it intends.
- **Stay under it**: lower `--concurrency` to the limit, but keep the
  requests overlapping — a 3-request interleave under a 10/sec limit still
  races.
- **Spread the identity**: per-IP limits → multiple source IPs (not always
  available in CTF); per-session → a second session (but the resource may be
  per-account — see the actor trap).

## 2. A narrow window — widen the check

The window exists but the burst misses it — the commit lands before the
second request's read. Widen the gap by slowing the check:

- **Pathological input**: a value that makes validation do more work — a
  catastrophic-regex email, a long uniqueness field on an unindexed column, a
  deeply-nested object the deserializer walks.
- **A heavy field**: a parameter that triggers a slow code path — a bcrypt on
  attacker-length input, a recursive serializer.
- **The PhantomFeed technique**: `email=a@` + 26 chars + `!` against a
  catastrophic regex measurably widened the verification window — the timing
  delta between arms is the signal that a widening primitive exists.

## 3. Sequential/serialized requests — a per-account lock

The app serializes requests per-account or per-session (a `user.mutex`, a
session lock). Two requests from one account never overlap.

- **Route around it**: the lock is per-account — race two *different*
  accounts on a global resource.
- **The lock's scope**: a lock acquired *after* the read, or released *before*
  the write, leaves the window open — the lock narrows it to before-acquire /
  after-release.

## 4. Connection multiplexing — hide the parallelism

The server deduplicates or serializes requests it sees as "the same" — a
request-id, an idempotency key, a connection-level lock.

- **Vary the irrelevant**: a different `X-Request-Id`, a different query
  param the app ignores — the requests look distinct to the deduper but
  identical to the check.
- **One request per connection**: bypasses a connection-level lock entirely.

## 5. A response cache — the second 200 is a replay

The endpoint caches its response by request hash. Two `200`s are a replay of
the first, not two effects.

- **Read the state**: `GET` the resource — did the effect double? A replay
  produces two `200`s but one effect — distinguish by the state read.
- **Vary to bypass the cache**: a cache-buster param (`?_=$RANDOM`) makes each
  request a distinct cache key — but if the check is on the same underlying
  record, the race still applies.

## 6. HTTP/2 prioritization — the barrier matters

On HTTP/2 the requests go out as frames; the order the server reads the last
DATA frames decides who commits first.

- **Single-packet burst**: all final DATA frames in one write — the tightest
  start. `race_probe`'s barrier does this.
- **The stall on h2**: withhold each stream's last DATA frame, then flush all
  at once — the h2 interleave.

## 7. A queue in front — the requests serialize at intake

The app enqueues requests and a single consumer processes them — the handler
race is closed by architecture, but the *queue-order* or the *consumer's own*
read-then-write may still be open.

- **Race the consumer's window**: the worker's `SELECT pending → UPDATE
  running` is the new window — race two triggers so two jobs land, or race
  the claim.
- **The enqueue check**: the "does this job already exist" check at enqueue
  is a check-then-insert — race it.

## 8. The optimistic-lock retry — SERIALIZABLE that retries

SERIALIZABLE aborts a loser, and a well-written app retries — the retried
request sees the committed state and *correctly* declines or applies. This is
the defence working, not a race to beat.

- **Distinguish**: a retry that reads post-commit state is serial-possible —
  not crossed state, a falsifier.
- **No bypass**: a correct retry loop is a real falsifier — record it.

## 9. Time-window defences — the deadline check

The app checks `now < deadline` at act-time. Race a request that arrives
*just* before the deadline against the act that runs after — the check and
the act straddle the boundary.

- **Fire the burst across the boundary second**: some requests' `now` lands
  before, some after — the check-time vs act-time gap is the window.
- **Or race the expiry**: a token valid-until-T used at T exactly — the
  `valid` read and the `use` act straddle the expiry.

## 10. The "defence" that isn't — a sleep or a busy-check

```python
time.sleep(0.01); if balance>=amt: update()    # a delay, not a lock
```

A `sleep` narrows the window statistically but doesn't close it — two
requests still read pre-state. Race it anyway; the delay just costs a few more
rolls.

## The evasion decision table

| Defence | Narrow or close? | Response |
|---|---|---|
| rate limit | narrow | race the limiter, or under-limit interleave |
| narrow window | narrow | pathological input / heavy field |
| per-account lock | narrow (or close for 1 acct) | two actors on a global resource |
| multiplexing dedup | narrow | vary irrelevant fields, 1 req/conn |
| response cache | narrow | read state, vary cache-buster |
| h2 serialization | narrow | single-packet / frame-level stall |
| intake queue | closes handler race | race the consumer's claim |
| SERIALIZABLE + retry | closes | falsifier |
| sleep/busy-wait | narrow | race it anyway |
