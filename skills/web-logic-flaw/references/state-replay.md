# State replay — a one-time transition is not one-time

A transition marked "one-time" is not — the coupon redeems twice, the vote
counts twice, the token replays, the refund issues twice. The transition
checks "is this valid?" but not "has this been used?"

## The mechanism

```
POST /redeem {"code": "SAVE50"}  → +50 credit
POST /redeem {"code": "SAVE50"}  → +50 credit   ← the second application
                                                  produces the same effect
```

The endpoint validates the input — the code exists, the token is signed —
but does not record that the transition already ran. The state machine
allows the same transition twice.

## The detection

### The one-time signals

Any endpoint that names a single-use semantic:

- `/redeem`, `/coupon`, `/voucher`, `/gift` — redeem once.
- `/vote`, `/like`, `/rate` — count once per user.
- `/reset`, `/recover` — token single-use.
- `/refund`, `/cancel` — once per order.
- `/invite`, `/refer` — once per invitee.
- `/claim`, `/collect` — once per entitlement.
- `/transfer` — the balance should leave once.
- `/verify` — a verification should complete once.

### The replay surface

```bash
# does the response differ between the first and second application?
curl -i -b "$JAR" -X POST "$BASE/redeem" -d 'code=SAVE50'
curl -i -b "$JAR" -X POST "$BASE/redeem" -d 'code=SAVE50'
```

A different response — `already redeemed`, `code used` — is the falsifier.
An identical response is the live surface.

## The probe

```bash
# the first application — the baseline state
curl -i -b "$JAR" "$BASE/balance" > before.txt
curl -i -b "$JAR" -X POST "$BASE/redeem" -d 'code=SAVE50'
curl -i -b "$JAR" "$BASE/balance" > after1.txt

# the second application — the replay
curl -i -b "$JAR" -X POST "$BASE/redeem" -d 'code=SAVE50'
curl -i -b "$JAR" "$BASE/balance" > after2.txt

# compare — did the balance increase twice?
diff before.txt after1.txt; diff after1.txt after2.txt
```

## The confirmation

The second application produces the same effect — the balance increased
twice, the vote counted twice, the refund issued twice:

```
before.txt: {"balance": 100}
after1.txt: {"balance": 150}
after2.txt: {"balance": 200}   ← the second redeem added 50 again
```

## The falsifier

The transition records its use — the second application is rejected:

```
HTTP/1.1 409 Conflict
{"error": "code already redeemed"}
```

or the state does not change on replay — `after2.txt` matches `after1.txt`.

## The replay shapes

| Shape | The transition | The payoff |
|---|---|---|
| coupon replay | redeem the same code twice | double credit |
| vote replay | vote the same way twice | double count |
| token replay | reuse a reset/recovery token | repeated recovery |
| refund replay | refund the same order twice | double refund |
| invite replay | accept the same invite twice | double invite credit |
| claim replay | claim the same entitlement twice | double entitlement |
| transfer replay | replay the same transfer | double debit of the source |
| verify replay | replay a verification | bypass a re-verification |
| session replay | replay a logged-out session | session resurrection |
| nonce replay | replay a one-time nonce | signature reuse |

## The replay vs race distinction

A replay is sequential — the second request runs after the first completes.
A race is concurrent — the two requests overlap in time. Sequential replay
succeeding is a logic flaw; concurrent replay succeeding is a race. The
probe distinguishes them: send the second request after the first's
response arrives. If it still succeeds, it is a logic flaw — the transition
is never recorded at all. If it fails serially but succeeds concurrently,
it is a race — see `web-race-condition`.

```bash
# sequential — logic-flaw test
curl -X POST .../redeem -d 'code=X' ; curl -X POST .../redeem -d 'code=X'

# concurrent — race test (tools/web/race_probe.py)
python3 tools/web/race_probe.py --url "$BASE/redeem" --write-ack \
  --body 'code=X' --concurrency 10
```

## The evidence rules

- The before/after state must be verbatim — the balance, the count, the
  order state — from the application's own view, not the POST response.
- Two identical `200`s is weak — the second `200` may be an idempotent
  "already done" response. The state change is the proof.
- A `409`/`400` naming "already used" is the falsifier — record it verbatim.

## The traps

- **A friendly `200` on replay is not proof.** Many frameworks return
  `{"status": "ok"}` for already-redeemed codes. Read the state.
- **The record may lag.** A second request fired before the first's write
  commits is a race, not a replay — the serial test answers it.
- **Replays may work per-session.** The same code on a different account
  succeeding is a different shape — multi-use code, not replay.
- **Some transitions are legitimately multi-use.** A discount code for
  "10% off every order" is not a flaw — read the intended semantics from
  the copy or the source.
