# Read-modify-write — the window, modeled

The exploitable race is almost never "send fast twice". It is a read-modify-write
whose *read* and *write* are separated, so two in-flight requests each observe
the pre-write state and both pass a check that only one should have passed.

---

## 1. The abstract shape

```text
request handling:
  1. read state S            (SELECT balance, SELECT count, SELECT token)
  2. decide on S             (if balance >= amount; if count < limit; if unused)
  3. optionally do work      (render, email, external call, another query)
  4. write new state S'      (UPDATE balance = balance - amount; INSERT; UPDATE used=true)

the window is between 1 and 4. two requests that both execute step 1 before
either reaches step 4 both see S — and both pass step 2.
```

The bug is not speed. It is the gap: anything that widens the distance between
the read and the commit widens the window.

## 2. Where the gap comes from

| Gap source | What sits between read and write | Window |
|---|---|---|
| different functions | read in `get_balance()`, write in `debit()` | the whole call between them |
| an external call | email send, HTTP fetch, PDF render, template compile | tens of ms to seconds |
| a second query | read table A, validate against table B, write A | one extra round-trip |
| application-level check | `if user.redeemed` in code, not a DB constraint | the whole controller body |
| ORM unit-of-work | read entity, mutate object, `flush()` at request end | the entire request |
| missing unique constraint | `SELECT name` then `INSERT name` | the gap is structural; it never closes |
| no transaction at all | autocommit per statement | each statement is its own window |

## 3. What closes the window (the falsifiers)

The class falsifier: **the read and the write happen inside one transaction or
behind one lock.** Concretely:

| Defence | How it closes the window | Probe that confirms it |
|---|---|---|
| atomic statement | `UPDATE balance = balance - 5 WHERE balance >= 5` | concurrent runs never go negative |
| `SELECT ... FOR UPDATE` | row lock held from read to commit | second request blocks, then sees new state |
| serializable isolation | the DB aborts one of the pair | one request errors/retries; state stays consistent |
| optimistic version column | `UPDATE ... WHERE version = 7` fails for the loser | loser's update affects 0 rows |
| unique constraint | `INSERT` raises on the duplicate | second insert errors; no double state |
| application mutex / queue | the handler serializes | timing shows strict serialization |
| idempotency key | the second request is deduplicated | identical key → identical single effect |

When any of these is observed, the class is closed for that endpoint — record
the falsifier and move to another endpoint, do not raise the rate.

## 4. Reading the window in source

White-box tells, in order of reliability:

```text
# Python / Flask / SQLAlchemy — the classic gap
balance = Account.query.filter_by(id=uid).first().balance   # read
if balance >= amount:                                        # decide
    send_receipt_email(user)                                 # WORK inside the window
    account.balance = balance - amount
    db.session.commit()                                      # write — window closes

# Node — same gap across awaits
const row = await db.get('SELECT used FROM codes WHERE code=?')   // read
if (!row.used) {
    await grantPrize(user)                                          // work
    await db.run('UPDATE codes SET used=1 WHERE code=?', code)      // write
}

# the single-statement form that is SAFE
await db.run('UPDATE codes SET used=1 WHERE code=? AND used=0')     // no gap
if (changes === 0) reject()                                          // decided by the write itself
```

The tell is two awaits, or a read and a write, on the same record across
different functions — especially with `sendEmail`, `fetch`, `render`, or a
second query between them.

## 5. What "crossed state" looks like

The confirmation is never "both returned 200". It is an effect that cannot
occur serially:

| Resource | Serial-impossible outcome |
|---|---|
| single-use code | two successful redeems of the same code |
| balance | balance decremented below zero, or withdrawn twice the balance |
| vote/like limit | the count exceeded the allowed maximum |
| uniqueness | two rows with the same "unique" value |
| token delivery | the token generated for address A arrives at address B (ApexSurvive) |
| registration | an account exists whose credentials are yours but whose "owner" step the bot then fails (SSOS) |
| OTP counter | more attempts than the limit accepted |

Crossed state is attributable: name which request committed first and which
state each one observed.

## 6. First probes

Serial baseline first — a signature that also appears serially is not a race:

```bash
# baseline: does one request serially produce the "win" signature anyway?
python3 tools/web/race_probe.py --url "$BASE/api/redeem" \
  --method POST --body '{"code":"XYZ"}' -H 'Cookie: session=...' \
  --baseline-count 5 --count 0 --no-barrier --challenge <name>
```

Then the overlapping run:

```bash
python3 tools/web/race_probe.py --url "$BASE/api/redeem" \
  --method POST --body '{"code":"XYZ"}' -H 'Cookie: session=...' \
  --concurrency 20 --count 20 --baseline-count 5 \
  --signature-mode status-length --challenge <name>
```

Read the result as: `max_in_flight` (did they actually overlap), the count of
identical-success responses, and the exact status/body split versus baseline.
Two `200` redeems where baseline gives one `200` then `409`/`400` is the
serial-impossible outcome.

## 7. The two-request form

When the race is between two *different* requests (A changes state, B reads it),
use `--url-b`:

```bash
python3 tools/web/race_probe.py \
  --url "$BASE/profile"  --method POST --body '{"email":"a@x"}' -H 'Cookie: session=...' \
  --url-b "$BASE/profile" --method-b POST --body-b '{"email":"b@y"}' \
  --concurrency 2 --count 10 --baseline-count 5 --challenge <name>
```

A and B must overlap — check `max_in_flight` in the output; a report that never
overlapped is `inconclusive`, not a negative.
