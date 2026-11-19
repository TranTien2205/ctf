# Evidence rules — what counts as a race, what doesn't

The discipline module. A race is the hardest class to attribute — the evidence
bar is higher than for a deterministic bug.

---

## 1. The serial-baseline rule

**No race verdict without a serial baseline.** The baseline establishes what
serial execution produces; the raced run must produce something serial never
did.

```bash
# always first: serial, no barrier, a few reps
python3 tools/web/race_probe.py --url "$BASE/api/redeem" \
  --method POST --body '{"code":"XYZ"}' -H 'Cookie: session=...' \
  --baseline-count 5 --count 0 --no-barrier --challenge <name>
```

A signature that appears serially is **not** a race — it's just the endpoint's
normal behavior. Two `200`s in baseline means the endpoint always returns `200`
and your "double redeem" is noise.

## 2. The overlap rule

**`max_in_flight` must prove the requests actually overlapped.** If the tool
reports `max_in_flight = 1`, the requests ran serially — the run is
`inconclusive`, never a negative and never a positive.

| `max_in_flight` | Reads as |
|---|---|
| 1 | serialized — inconclusive; fix delivery, re-roll |
| ≥ 2 but < requested | partial overlap — note it; the result is still usable if the crossed state appears |
| = requested concurrency | clean overlap — the result is meaningful |

## 3. The attribution rule

**You must be able to name the two requests that crossed.** A flood that
produces an extra success among hundreds doesn't say which pair crossed —
unattributable, not evidence.

```text
attributable:   "A committed at T, B committed inside A's window at T+3ms,
                 producing balance=-50 that only both-in-flight explains"
unattributable: "out of 500 requests, 3 returned 200 — one of them double-won"
```

`race_probe` reports the status/body split per request slot — use it to name
the pair. If you can't, re-roll with lower `--concurrency` until you can.

## 4. The crossed-state rule

The only confirmation is a **serial-impossible outcome** — a state that cannot
be produced by running the requests one at a time in any order:

| Resource | Serial-possible (not evidence) | Serial-impossible (evidence) |
|---|---|---|
| redeem | one 200, rest 4xx | two 200s for one code |
| balance | balance drops by amount once | balance = -amt, or drops by 2×amt |
| vote | one vote recorded | score +2 for one voter |
| register | one account created | two rows with one email, or you own a bot's account |
| session | one cookie issued | two distinct working cookies under a one-session policy |
| token delivery | token to its own address | token to the *other* in-flight address |

Two `200`s alone are not crossed state — the *effect* must be impossible
serially. A `200` that means "already used, but politely" is not a win.

## 5. The quote-the-response rule

A `confirms` verdict requires the verbatim response excerpt. For a race that
excerpt is the **status/body split plus the post-state read**:

```text
--evidence "baseline: [200,409,409,409]; raced: [200,200,409,...] max_in_flight=20;
            GET /api/account balance=-100 (serial floor 0)"
```

The `--response` is the raced run's output plus the state read — the excerpt
must be a substring of it.

## 6. The falsifier rule

A falsifier is an observation that **closes the class** for that endpoint —
record it and stop, do not retry harder:

| Falsifier observed | Meaning |
|---|---|
| atomic `UPDATE ... WHERE` + rowcount check in source | window closed at the statement |
| `FOR UPDATE` / `select_for_update` / `PESSIMISTIC_WRITE` | read is locked to commit |
| `UNIQUE` constraint on the raced field | the DB rejects the second write |
| SERIALIZABLE + retry | the DB aborts a loser |
| `findOneAndUpdate` / `ConditionExpression` / `updateMany` rowcount | datastore-atomic |
| raced run: loser gets clean 4xx, no crossed state, `max_in_flight` clean | defence held under real overlap |

A falsifier is a **recorded negative**, not a failure — write it to the ledger
so the next attempt doesn't re-walk it.

## 7. The timeout / reset rule

**A timeout is never a confirm.** A raced request that timed out produced no
readable response — its contribution to the outcome is unknown. A connection
reset is the same. Discard that slot's result and re-roll; do not count a
timeout as a success or a failure.

## 8. The blast-radius rule

**Race an object you own.** A write-shaped run without `--write-ack` is refused
by the tool. Before firing:

- the resource is yours (your account, your code, a test object)
- the effect is reversible or bounded
- on a shared instance: the SSOS rule — a one-shot consumable target must be
  fresh, and once consumed it's gone for everyone; confirm freshness first
- the run won't corrupt another player's state (a negative balance on the
  *shared* demo account is corruption, not a win)

## 9. The re-roll rule

`inconclusive` is not `no`. When the mechanics fail to overlap:

```text
max_in_flight < requested  → lower concurrency, or single-packet/interleave
all-losers                 → window narrower than the burst → interleave/stall
flaky network              → re-roll; don't read noise as a result
```

A re-roll uses `--reset-url`/`--reset-body` to restore the starting state so
each attempt begins from the same S — without it, run N starts where run N-1
ended.

## 10. The evidence record template

```text
endpoint:        POST /api/redeem
alphabet row:    C — single-use code
window:          SELECT used → grant → UPDATE used=1 (no constraint, no tx)
baseline:        5 serial → [200, 409, 409, 409, 409]
raced run:       concurrency 20, max_in_flight 20 → [200×2, 409×18]
crossed state:   2 grants for code XYZ; GET /api/inventory shows 2 items
attribution:     slots 3 and 11 both committed within the window
verdict:         confirms — serial-impossible outcome
falsifier check: no FOR UPDATE, no UNIQUE(used), no atomic update in source
```

Write this shape into `hooks.py post-probe` — `--evidence` is the raced split
plus the state read, `--response` the raw tool output it came from.
