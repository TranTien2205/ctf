# First hour — the business-logic engagement's first sixty minutes

The timed walk — what the first hour of a logic-flaw challenge looks
like when the alphabet is swept in the right order.

## 0:00–0:10 — recon

```bash
python3 selfcheck.py
python3 tools/state.py chal --category web --target $BASE \
  --challenge-name "..." --event "..."
python3 tools/classify.py "<obs>"
python3 tools/chain_match.py --record chal
python3 tools/web/bundle_miner.py --url $BASE/static/app.js --out /tmp/b
```

Deliverable: the endpoint list (the edge list) + the field map from
`GET` responses.

## 0:10–0:20 — baselines + the 60-second probes

- happy-path flow saved verbatim (`b_*.txt` files);
- `GET /flag`, `/admin`, `/export` bare — the zero-cost terminals;
- `POST /register + role=admin` → read-back;
- `POST /confirm` (or terminal) bare → `302`/`200`+pair.

Four probes, four potential CONFIRMs — the cheap cells first.

## 0:20–0:35 — the mechanism sweep

| Minutes | Mechanism | The probe |
|---|---|---|
| 3 | boundary | `-1`, `0`, `NaN`, `1e309` on `qty`/`price`/`discount` |
| 3 | replay | redeem/claim ×2 serially |
| 3 | transform | `id` at limit/limit+1/malformed — diff rejections |
| 3 | trust | mutate the carried `total`/`price` |
| 3 | idempotency | same-key replay, mutated body |

Fifteen minutes of probes covers most of the alphabet. Each row ends
in confirm (→ chain) or falsifier (→ next row) — the falsifiers are
what keeps it to fifteen minutes.

## 0:35–0:50 — the chain walk

Each confirmed edge opens the next:

- `role:admin` → enumerate gated surface → flag field;
- `confirmed+unpaid` → the order's flag field;
- `balance:+50×2` → the overpriced flag item;
- transform gap → `transform-math.md` → the wrap write.

## 0:50–0:60 — flag gate or escalate

- flag in a live response → `pre-flag` → `classify_solve.py`;
- alphabet spent → `decide.py` — the next rung (`writeup_search`,
  `novel_plan`, `fanout_sweep`), never a sixth spelling.

## What the hour is NOT

- not 60 minutes of payload variants in one mechanism cell;
- not 60 minutes without a recorded falsifier;
- not 60 minutes where no `--response` was ever attached to a verdict.

The hour ends with a flag, a kill map, or an escalation — all three are
recorded states, not silence.
