# Common questions — the race-condition FAQ

The questions that come up on every race engagement, with the probe that
answers each.

---

## 1. Is a race condition a real bug if I can only sometimes reproduce it?

Yes — a race is a probabilistic bug by definition. The class is proven by a
single serial-impossible outcome attributed to a named pair, not by a 100%
hit rate. A 5% success rate still proves the window exists; you then make it
reliable by widening the window or tightening the delivery.

## 2. Do I need many requests, or just two?

Two, correctly interleaved. The goal is to land the second commit inside the
first request's window — a flood hides which pair crossed and an
unattributable success isn't evidence. `race_probe --concurrency N` exists
for the burst form when the window is wide enough; the interleave form (a
last-byte stall or `--url-b`) is for the narrow window.

## 3. The endpoint returns 200 to everything — did I win?

Only if the *state* changed impossibly. Two `200`s where serial produces one
`200` + `409` is the race; two `200`s where serial also produces two `200`s
is a replay or a normal response. Read the state — the balance, the inventory
count — not the status.

## 4. The app wraps everything in a transaction — is the race closed?

No — a transaction is not a lock. At READ COMMITTED (the default) the `SELECT`
reads a snapshot and both transactions write. The window closes only with
`FOR UPDATE`, an atomic `UPDATE ... WHERE`, a constraint, or SERIALIZABLE.

## 5. How do I know if the requests actually overlapped?

`race_probe` reports `max_in_flight` — the peak number of requests in flight
at once. `1` = serialized (inconclusive, re-roll). `≥ 2` = real overlap — the
result is meaningful. Never interpret a `max_in_flight=1` run as a negative.

## 6. What's the difference between a burst and an interleave?

- **Burst**: N complete requests fired at once. Wins when the window is wide
  enough that one request commits while others are mid-read.
- **Interleave**: request A held open (a withheld last byte, a partial body)
  while B completes — lands B inside A's already-open window.

The interleave is for narrow windows; the burst for wide ones. The
ApexSurvive cross needed the interleave — a burst serialized.

## 7. My race won once but not again — real or noise?

Real — a race is probabilistic. Re-roll (with `--reset-url` to restore state)
until you can attribute the pair. If it won once, the window exists; if you
can't re-roll, the delivery or the reset is the problem, not the bug.

## 8. The second `200` has an identical body — did it double the effect?

Check the state. An identical `200` body with no doubled effect (inventory
didn't grow, balance didn't halve twice) is a response cache or a polite
dedup — a falsifier, not a win.

## 9. Is a negative balance a "real" crossed state or just a display bug?

A real crossed state — the serial floor is `0` and `balance = -amt` cannot be
produced serially. The balance column value, read back from `/api/account`,
is the evidence.

## 10. The rate limiter blocks the burst — is the endpoint safe?

No — the limiter gates how many requests reach the handler; it doesn't close
the handler's window. Race the limiter (it's a counter itself), or stay under
it with a tighter interleave.

## 11. What if the server only has one worker?

The HTTP race is closed — requests serialize at the accept queue. Race the
layer below: two replicas on a shared DB, a background worker's claim, or the
app issuing two queries that interleave at the DB.

## 12. A timeout during the race — does it count?

No — a timeout produced no response; the slot's contribution is unknown.
Discard it and re-roll. A timeout is never a success and never a falsifier.

## 13. How is a race different from a logic flaw on the same endpoint?

A race is temporal — the check is correct but the gap between check and act
lies. A logic flaw is spatial — the check itself is wrong, no timing needed.
`if (balance>=amt) withdraw()` races; `if (balance>=0) withdraw(-100)` is a
logic flaw that works serially.

## 14. The race is on a shared instance — can I run it?

Only on an object you own. A race corrupts the raced record — a negative
balance on the shared demo account is corruption for every player. Race your
own account/code/resource, and confirm a one-shot target is fresh before
firing (the SSOS rule).

## 15. When is "two of the same 200" actually the win?

When the serial baseline proves one `200` then declines, *and* the raced run
produces two `200`s, *and* the state shows the doubled effect. All three —
the split, the baseline, and the state read — are the attribution.
