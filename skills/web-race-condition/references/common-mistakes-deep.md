# Common mistakes deep — every failure mode, exhaustively

The exhaustive failure catalogue. Each mistake: the symptom, the root cause,
and the correction.

---

## 1. Delivery mistakes

### 1a. Flooding instead of interleaving

500 parallel requests produce two `200`s and no attribution — you can't name
which pair crossed.

- **Root cause**: confusing throughput with overlap. The goal is landing a
  second commit inside a named window, not volume.
- **Fix**: two interleaved requests (`--url-b` or a last-byte stall), or
  `--concurrency N --count N` with the per-slot split to name the pair.

### 1b. One connection, "parallel" requests

N requests over one keep-alive connection serialize at the client or the
framework's per-connection lock.

- **Symptom**: `max_in_flight` = 1 despite `--concurrency 20`.
- **Fix**: `--concurrency N` opens N connections — read `max_in_flight` in the
  report.

### 1c. Escalating the count, not the mechanics

"The burst didn't win, send 1000." The window doesn't get wider — you hide
the pair and DoS the target.

- **Fix**: switch mechanics (burst → interleave → pathological widen), not
  count.

### 1d. No barrier sync — a staggered burst

Requests fired at slightly different times; the first commits before the last
starts.

- **Fix**: `--barrier-timeout` primes all connections then releases together —
  the single-packet form.

## 2. Interpretation mistakes

### 2a. Skipping the serial baseline

Racing before knowing what serial produces. A "win" signature that appears
serially is normal behavior.

- **Fix**: `--baseline-count 5 --count 0 --no-barrier` first. The serial set
  is the calibration.

### 2b. Reading status, not state

Two `200`s that mean "already done politely" or a cached replay is not a
crossed state. The evidence is the *effect*.

- **Fix**: `GET` the resource — the balance, the inventory, the count — not
  the status split.

### 2c. Treating inconclusive as negative

A run where `max_in_flight` = 1 never overlapped — it's not a falsifier.

- **Fix**: `inconclusive` → fix delivery, re-roll. Only a real-overlap clean
  run is a falsifier.

### 2d. A timeout counted as a result

A timed-out slot produced no response — its contribution is unknown.

- **Fix**: discard the slot, re-roll. A timeout is never success or failure.

### 2e. A `500`/`IntegrityError` read as a win

The constraint firing produces a `500`/`IntegrityError` on the loser — that's
the defence working, not a crash, and never a second success.

- **Fix**: read the error — `23505`/`1062`/`IntegrityError` is a falsifier.

## 3. Target-selection mistakes

### 3a. Racing a defended endpoint

Firing at an endpoint with `UPDATE ... WHERE`/`FOR UPDATE` in source. The
window is closed.

- **Fix**: the constraint/lock audit *before* the probe.

### 3b. Racing the wrong actor

The resource is global but the check is per-account — racing one session hits
the account dedup.

- **Fix**: two cookie jars behind a shared barrier.

### 3c. Racing a one-shot on a used instance

The SSOS trap — the flag was consumed at startup; the instance can't be won.

- **Fix**: confirm freshness *before* firing; a consumed instance is
  unrecoverable.

### 3d. Racing a shared/demo object into corruption

A negative balance on the shared account corrupts it for every player.

- **Fix**: race an object you own; `--write-ack` is the acknowledgement.

## 4. Scope mistakes

### 4a. Assuming a transaction is a lock

"Wrapped in `BEGIN`/`@Transactional` — it's atomic." At READ COMMITTED the
read still snapshots and both write.

- **Fix**: a transaction is not a lock. Only `FOR UPDATE`, an atomic
  statement, a constraint, or SERIALIZABLE closes the window.

### 4b. Confusing race with logic flaw

A race needs overlap; a logic flaw works serially. `if (balance>=0)
withdraw(-100)` is a logic flaw, not a race — race_probe on it gives a
trivial, serial result.

- **Fix**: classify first — `classify.py` names the class; the confusable is
  `web-logic-flaw`.

### 4c. Claiming the crossed state as the flag

The double-redeem is a *primitive* — the flag is behind the gate it opens.

- **Fix**: map primitive → gate → flag. The race buys the foothold.

### 4d. Racing a read-only endpoint

A `GET` with no check-then-act has nothing to interleave — it's not a race
target.

- **Fix**: inventory writable endpoints; the shared state must change.

## 5. Process mistakes

### 5a. Not recording negatives

A falsifier you don't record is a budget you'll spend twice — the next run
re-walks the closed endpoint.

- **Fix**: every falsifier → the ledger → `knowledge/attempts/` with the
  reopen-if.

### 5b. Not attributing the pair

"I got a double-win somewhere" — an unattributable success isn't evidence.

- **Fix**: the per-slot split names the pair; if you can't name it, re-roll
  with lower concurrency.

### 5c. Re-rolling without a reset

Run N starts where run N-1 ended — the balance/code is already consumed.

- **Fix**: `--reset-url`/`--reset-body` restores the starting S between rolls.

### 5d. The signature-mode reads nothing

The win/loss isn't in the status — same `200`, difference in the body.

- **Fix**: `raw-body` / `normalized-body` / `regex` / `signature-header` —
  pull the distinguishing field.

### 5e. Reading the chain card's prose as the probe

`family_leads` matches are guidance, not the probe — the card's
`first_confirming_probe` is what to run.

- **Fix**: `--record` the card, run its `first_confirming_probe` — not the
  mechanism prose.

## The mistake → correction table

| Mistake | Correction |
|---|---|
| flood not interleave | `--url-b` / stall / name the pair |
| one conn "parallel" | `--concurrency` opens N conns |
| escalate count | switch mechanics |
| no barrier | `--barrier-timeout` single-packet |
| no baseline | `--baseline-count` first |
| status not state | `GET` the resource |
| inconclusive=negative | fix delivery, re-roll |
| timeout=result | discard, re-roll |
| 500=win | `IntegrityError` is a falsifier |
| defended endpoint | audit first |
| wrong actor | two sessions, one barrier |
| used one-shot | confirm freshness first |
| shared object | race what you own, `--write-ack` |
| tx=lock | only lock/atomic/constraint/SERIALIZABLE closes |
| race≠logic | classify first |
| primitive=flag | map to the gate |
| read-only endpoint | inventory writable only |
| no negative record | ledger + kill-map |
| no attribution | name the pair |
| no reset | `--reset-url` |
| wrong signature-mode | raw/normalized/regex/header |
| family_leads=probe | run `first_confirming_probe` |
