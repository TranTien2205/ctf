# Evidence rules deep — the exhaustive standard for proving a race

The complete evidence contract: every rule a race verdict must satisfy, every
way a "win" fails to be evidence, and the record that survives review.

---

## 1. The serial-set axiom

A race is proven iff the observed outcome is outside the set of outcomes
reachable by any serial ordering of the requests. Every evidence rule derives
from this.

```text
requests {A, B} on resource R.
serial orderings: A→B and B→A produce the serial set S.
a raced outcome O ∉ S is a race. O ∈ S is not — even if it "felt" concurrent.
```

## 2. The baseline rule — enumerating the serial set

You cannot prove `O ∉ S` without knowing `S`. The baseline enumerates it.

```bash
python3 tools/web/race_probe.py --url "$BASE/api/redeem" \
  --body '{"code":"XYZ"}' -H 'Cookie: s=..' \
  --baseline-count 5 --count 0 --no-barrier --challenge <name>
```

| Baseline | The serial set S |
|---|---|
| `[200, 409, 409, 409]` | one success, rest decline |
| `[200, 200]` | both succeed serially — "two 200s" is NOT evidence |
| `[400, 400]` | all decline — a "200" would be suspicious for other reasons |

**Never** interpret a raced result without the baseline.

## 3. The overlap rule — the requests must actually overlap

`max_in_flight` is the proof that the requests were in flight together.

| Value | Reads as |
|---|---|
| 1 | serialized — inconclusive (never a result, never a falsifier) |
| ≥ 2, < requested | partial overlap — usable if the crossed state appears |
| = requested | clean overlap |

A run that didn't overlap cannot prove anything — it's neither a win nor a
negative.

## 4. The attribution rule — name the pair

The proof names which two requests crossed: "slot 3 and slot 11 both committed
inside the window". A flood that produces an extra success among hundreds
doesn't name the pair — unattributable.

```text
attributable:   race_probe per-slot split → slots 3, 11 committed in-window
unattributable: "3 of 500 returned 200" — which pair?
```

Lower `--concurrency` until you can name the pair. If you can't attribute it,
it's not evidence.

## 5. The state rule — the effect, not the status

The crossed state is read from the *state* — the balance, the inventory, the
count, the mailbox — not the HTTP status.

| Status alone | State |
|---|---|
| two `200`s | `GET /api/inventory` shows 2 items → evidence |
| two `200`s | `GET /api/account` shows no double → a replay, not a race |

## 6. The quote-the-response rule — `post-probe`

`hooks.py post-probe --verdict confirms` requires the verbatim excerpt inside
`--response`:

```bash
python3 tools/hooks.py post-probe <name> --class web-race-condition \
  --hypothesis-id <h> --verdict confirms --evidence-kind impact \
  --evidence "raced [200×2,409×18] vs baseline [200,409×4], max_in_flight=20; GET /api/account balance=-100" \
  --response "<the race_probe output + the state read the excerpt came from>"
```

The `--evidence` must be a substring of `--response` — the gate checks the
quote, not the claim.

## 7. The timeout/reset rule — never a result

A timed-out or reset slot produced no readable response — its contribution is
unknown. Discard it; it's never a success and never a falsifier.

## 8. The IntegrityError rule — a constraint 500 is a falsifier

A `500`/`IntegrityError`/`duplicate key` on the loser is the constraint doing
its job — the defence held. Record it as a falsifier, not a crash and never a
win.

## 9. The falsifier rule — a clean real-overlap no-cross

```text
baseline:  [200, 409, 409, 409]
raced:     max_in_flight 20, [200, 409×19]  ×3 rolls
state:     one grant only
verdict:   falsifier — the defence held under real overlap
```

A falsifier requires *real overlap* — `max_in_flight` ≥ 2 across clean rolls.
An `inconclusive` run never closes the class.

## 10. The blast-radius rule — own the object

A write-shaped run needs `--write-ack`, and the object must be yours:

- your account, your code, a test entity
- bounded, reversible effect
- a one-shot target is confirmed fresh *before* firing (the SSOS rule — a
  consumed instance is unrecoverable for everyone)
- no corrupted state lands on a shared/demo object

## 11. The primitive≠flag rule

The crossed state is a *primitive* — the flag is behind the gate it opens.
Do not claim a flag from the race; claim it from the live response the
primitive unlocked (`hooks.py pre-flag`).

## 12. The evidence record template

```text
challenge:   <name>
class:       web-race-condition
endpoint:    POST /api/redeem
alphabet:    C — single-use code
window:      SELECT used → grant → UPDATE used=1  (app.py:210-218)
defence:     none — no constraint, no tx, no lock (constraint audit §3)
baseline:    [200, 409, 409, 409, 409]  (5 serial)
raced:       concurrency 20, max_in_flight 20 → [200×2, 409×18]
crossed:     GET /api/inventory → 2 items from code XYZ
attribution: slots 3 and 11 committed within the window
verdict:     confirms — serial-impossible outcome
primitive:   double-grant → buy the flag_item gate
response:    <the race_probe output + the inventory read>
```

## 13. The evidence-grade ladder

| Grade | Evidence | Can you claim? |
|---|---|---|
| full | baseline + overlap + crossed state + attributed pair + effect verified | confirms |
| strong | baseline + overlap + crossed state, attribution fuzzy | confirms with a note — re-roll to attribute |
| weak | overlap + a "win-looking" status, no state read | inconclusive — read the state |
| none | a flood, an un-verified 200, a timeout | not evidence — re-roll |

## 14. The anti-patterns that fail review

- "two 200s = double-redeem" — without the state read.
- "500 requests, 3 wins" — without naming the pair.
- "it worked once" — without re-rolling to attribute.
- "the baseline also does that" — then it's not a race.
- "I saw max_in_flight but it was 1" — no overlap, no result.
- "the flag-ish thing I got" — the crossed state isn't a flag; the effect
  that unlocks it is read separately.
