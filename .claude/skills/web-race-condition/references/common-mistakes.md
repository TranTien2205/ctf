# Common mistakes — the failure modes that burn the budget

Every way this skill goes wrong, ranked by how often it costs a challenge.

---

## 1. Flooding instead of interleaving

The #1 mistake. Sending 500 parallel requests produces two `200`s and tells
you nothing — you can't name which pair crossed, and an unattributable success
is not evidence.

- **Symptom**: "I got a double-win somewhere in the flood."
- **Fix**: two interleaved requests, or `--concurrency N --count N` with the
  per-slot split — name the pair. Re-roll, never flood.

## 2. Skipping the serial baseline

Racing before knowing what serial produces. The "win" signature (two `200`s)
may be the endpoint's *normal* response — the endpoint always `200`s and the
"double effect" is noise.

- **Symptom**: claiming a race on a signature that appears serially.
- **Fix**: `--baseline-count 5 --count 0 --no-barrier` *first*. A signature in
  baseline is not a race.

## 3. Reading status codes, not state

Two `200`s that mean "already done, politely" or a cached replay is not a
crossed state. The evidence is the *effect* — the negative balance, the second
grant — not the status.

- **Symptom**: two `200`s, but `GET /api/account` shows no doubled effect.
- **Fix**: the crossed state is in the state read, not the status split.

## 4. Racing a defended endpoint

Firing `race_probe` at an endpoint whose source shows `UPDATE ... WHERE` or
`FOR UPDATE`. The window is closed; you're measuring noise.

- **Symptom**: clean losers on every slot, `max_in_flight` fine, no cross —
  and you keep re-rolling.
- **Fix**: the constraint/lock audit *before* the probe. A falsifier is a
  recorded negative, not a retry signal.

## 5. One connection, "parallel" requests

Sending N requests over a single keep-alive connection and assuming they're
parallel. They serialize at the client or the framework's per-connection lock.

- **Symptom**: `max_in_flight` = 1 despite `--concurrency 20`.
- **Fix**: `--concurrency N` opens N connections — check `max_in_flight` in
  the report.

## 6. Treating `inconclusive` as `no`

A run where `max_in_flight` = 1 is not a negative — the requests never
overlapped. Recording it as a falsifier closes a class that was never tested.

- **Symptom**: the ledger says "race failed" but the requests serialized.
- **Fix**: `inconclusive` → fix delivery, re-roll. Only a real-overlap clean
  run is a falsifier.

## 7. Escalating the rate instead of the mechanics

"The burst didn't win, send 1000." The window doesn't get wider — you just
hide the pair that matters and DoS the target.

- **Symptom**: the target slows, the result is still unattributable.
- **Fix**: switch mechanics — burst → interleave → pathological-input widen —
  not count.

## 8. Racing the wrong actor

The resource is global (one seat) but you race two requests from *one*
account — and the account-level check (`user.claimed`) dedups correctly. You
needed two different actors on the global resource.

- **Symptom**: one-session race gives no cross, so you stop.
- **Fix**: two cookie jars behind a shared barrier — `--url-b` or two probes.

## 9. Claiming the crossed state as the flag

The double-redeem is a *primitive*. The flag is behind the gate the primitive
opens — the bought item, the owned account's bot output.

- **Symptom**: reporting "I won the race" and stopping before the effect pays.
- **Fix**: map the primitive → the gate → the flag. The race buys the
  foothold, not the flag.

## 10. Ignoring blast radius

Racing a shared demo account into negative balance, or a one-shot target on a
used instance — you've corrupted state for other players or consumed a
target nobody can recover.

- **Symptom**: other players' balances are off; the flag was already consumed.
- **Fix**: race an object you own; confirm a one-shot target is fresh *first*;
  `--write-ack` is the acknowledgement you read this.

## 11. A timeout counted as a result

A raced request that timed out produced no response — its contribution is
unknown. Counting it as success *or* failure corrupts the split.

- **Symptom**: "3 of 10 timed out so 7 ran clean" — and you score the 7.
- **Fix**: a timeout is `unknown` — discard the slot, re-roll. Never a
  confirm, never a falsifier.

## 12. Assuming a transaction is a lock

"The code wraps it in `BEGIN`/`transaction.atomic`/`@Transactional` — it's
atomic." At READ COMMITTED the read still snapshots and both write.

- **Symptom**: you skip a winnable endpoint because it's "in a transaction".
- **Fix**: a transaction is not a lock. Only `FOR UPDATE`, an atomic
  statement, a constraint, or SERIALIZABLE closes the window.
