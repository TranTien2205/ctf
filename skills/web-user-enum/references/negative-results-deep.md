# Negative results (deep) — the cell-addressed dead ends

## The dead-end matrix

```
                body   status+loc   timing   side    = verdict
/login          unif    unif         unif     unif    = closed
/register       LEAK    -            -        -       = oracle (text)
/reset          unif    unif         +180ms   unif    = oracle (timing)
/check-username bool-false                                 = direct oracle
```

Each cell is a measured result — `unif`, `LEAK`, a delta, `closed`,
`unmeasured`. A row of all-`unif` is a closed form; a `LEAK` cell is
the oracle.

## The cell-addressed record

A negative is recorded at the (form × channel) cell:

```json
{"form":"/login","channel":"timing","result":"good_med=9 bad_med=8 jit=3",
 "verdict":"closed — sub-jitter"}
{"form":"/reset","channel":"send-side","result":"both queue","verdict":"closed"}
{"form":"/check-username","channel":"direct","result":"404","verdict":"no endpoint"}
```

A `unmeasured` cell is a gap, not a negative — it must be probed or
explicitly marked `gap`.

## The honest-negative shapes

- **`uniform`** — the channel measured identical; a real closure
- **`sub-jitter`** — a real delta below the noise floor; a weak-hash app
- **`no-repeat`** — a one-off anomaly that did not survive a re-send
- **`masked`** — the diff is per-request noise, not a differential
- **`no-endpoint`** — the form/route does not exist
- **`throttle`** — a `429`/`423`/delay within the burst
- **`scope`** — the measurement is out-of-scope (a mass spray)

## The kill-map write

A fully-closed form → `knowledge/attempts/<chal>.json` records the dead
layers so the next attempt does not re-walk them. A closed channel
within an open form is a partial negative — the other channels are
still live.

## The negative-that-feeds rule

A closed enum form is still input to:
- `web-auth-session` — a uniform-auth target's session is the next layer
- `web-logic-flaw` — the reset-flow bug does not need an enum oracle
- `web-idor` — a `/api/users/{id}` read is its own oracle
- `knowledge/attempts/` — the dead-layer record

A negative is a measurement, not a stop.
