# Troubleshoot — every way the race fails to run or to read

Symptom → cause → fix. The order is: fix the mechanics first, then the
interpretation, then the target.

---

## 1. `max_in_flight` = 1 — the requests serialized

**Cause**: one connection, a per-connection lock, or a single worker.

```bash
# verify the server can run two handlers at once — a slow endpoint
time (curl -s "$BASE/slow" & curl -s "$BASE/slow" & wait)
# 2× the delay = one worker; ~1× = real parallelism
```

- If one worker: race the DB layer or another tier — the HTTP race is closed.
- If parallelism exists but `max_in_flight`=1: one connection. `--concurrency N`
  opens N connections — confirm the client isn't multiplexing.

## 2. `max_in_flight` < requested concurrency — partial overlap

**Cause**: the server couldn't prime all connections before the barrier fired,
or the worker pool is smaller than `--concurrency`.

- `--barrier-timeout` fired before all connections primed → raise it.
- worker pool smaller than `--concurrency` → the extras queued; set
  `--concurrency` = the real ceiling.

## 3. All responses are the serial-loser shape — the window is narrower than the burst

**Cause**: the burst arrives *after* the first request already committed — the
window is ms-scale and the burst isn't tight enough.

- Switch burst → interleave: hold A open (last-byte stall), drop B inside.
- Widen the window: a pathological input that slows the check
  (`timing-oracle` — a catastrophic regex input, a heavy uniqueness field).

## 4. `429`/`403` on the burst — the race is throttled

**Cause**: a rate limiter or a per-request CSRF/origin check rejects the
flood before the handler.

- The limiter is itself check-then-act — race it, or stay under its threshold
  while still overlapping.
- A consumed CSRF token: race the token-issuing endpoint, or find a flow that
  accepts the same token for the whole burst.

## 5. Two `200`s but no doubled state — a replay, not a race

**Cause**: the endpoint caches responses by request hash, or the `200` means
"already done politely".

- Read the *state*, not the status: `GET /api/account` — did the effect
  double? Identical `200` bodies with no doubled effect is a replay cache —
  falsifier, not a win.

## 6. Inconsistent results run to run — the window is marginal

**Cause**: the burst lands inside the window only sometimes — network jitter,
a scheduler coin-flip, a marginal window width.

- Re-roll, don't flood: `--reset-url` restores state between rolls.
- Widen the window (pathological input) so the marginal becomes reliable.

## 7. A `500`/timeout on one slot — a half-commit

**Cause**: a request crashed mid-window — the read committed, the write
didn't, or vice versa.

- The half-state is a finding (non-atomic commit) — record it.
- The slot's contribution is `unknown` — discard it, reset state, re-roll.
- A timeout is never a success or a failure.

## 8. The "win" appears serially — it was never a race

**Cause**: the baseline shows the same signature as the raced run — the
endpoint always produces two `200`s.

- The baseline is the calibration: a signature in baseline is normal
  behavior. Recalibrate what you're proving — the crossed *state*, not the
  two `200`s.

## 9. Racing one session gives nothing — wrong actor

**Cause**: the resource is global but the check is per-account; racing one
session hits the account-level dedup correctly.

- Two cookie jars behind a shared barrier — race two *different* sessions on
  the global resource.

## 10. The race wins but nothing downstream — primitive with no gate

**Cause**: the crossed state doesn't unlock anything — a double-vote with no
threshold, a negative balance with no store.

- Map the primitive → the gate → the flag *before* racing. A race that buys
  nothing is a finding with no impact — record it and move to a primitive
  that pays.

## 11. `race_probe` refuses — `--write-ack` needed

**Cause**: the run is write-shaped (it changes state) and you didn't
acknowledge the blast radius.

- Confirm the object is yours and the effect is bounded; add `--write-ack`.
- On a shared instance: a one-shot/consumable target must be fresh — check
  first, race once.

## 12. The `--signature-mode` reads nothing — wrong split

**Cause**: the win/loss isn't in status — same `200` for both, difference in
the body or a header.

- `--signature-mode raw-body` — the raw body differs (a second token, a second
  cookie).
- `--signature-mode normalized-body` — strip timestamps/ids.
- `--signature-regex`/`--signature-header NAME` — pull the distinguishing
  field (`Set-Cookie`, a balance field, a `Location`).
- `--signature-bytes N` — compare only the first N bytes.

## 13. The interleave needs a manual stall — the tool can't hold a byte

**Cause**: `--url-b` fires two complete requests; the ApexSurvive cross needs
A held *mid-request* (last byte withheld).

- Write the raw-socket stall (`delivery-mechanics.md` §1): withhold A's last
  body byte, complete B, release A's byte. The stall keeps A's handler
  in-flight while B commits.

## 14. Everything's clean and there's still no cross — recorded negative

**Cause**: the window is closed — a defence you didn't grep for, a SERIALIZABLE
retry, an atomic update.

- 3 clean real-overlap runs, `max_in_flight` ≥ 2, all-loser shape, no cross:
  record the falsifier. The class is closed *for that endpoint* — move to
  another endpoint or the class is exhausted.
