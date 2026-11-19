# Workflow checklist — the printable engagement gate

The run-down checklist to keep next to the terminal. Tick each box; a missing
one is a step you skipped.

---

## Pre-flight

```text
□ classify.py named the class — web-race-condition confirmed, not a logic flaw
□ chain_match.py --record run — a card's probe in hand if one matches
□ the object I own is identified (my account, my code, a test entity)
□ the target is fresh if it's a one-shot (the SSOS rule)
□ --write-ack understood — the effect is bounded and reversible
```

## Inventory

```text
□ every writable endpoint listed (the bundle + the route table)
□ candidates are writable AND checked (not a blind insert)
□ ranked by flag-proximity: money → token → account → limit → vote
□ for each: the shared record named (code.used, account.balance, vote count)
```

## Window audit

```text
□ the read identified (the SELECT/get that loads the record)
□ the decide identified (the if that gates on the read)
□ the work identified (email/render/fetch/second-query — the width)
□ the write identified (the UPDATE/INSERT/commit)
□ the gap is real — read ≠ write, work between them
```

## Falsifier check

```text
□ grep for: FOR UPDATE, select_for_update, with_for_update, PESSIMISTIC
□ grep for: UPDATE ... WHERE <predicate> + rowcount, updateMany, update_all
□ grep for: UNIQUE, CHECK, PRIMARY KEY on the raced field
□ grep for: SERIALIZABLE + retry
□ grep for: findOneAndUpdate, ConditionExpression, WATCH/MULTI, IF
□ a transaction alone is NOT a falsifier — READ COMMITTED is still open
□ if falsified → record it and move to the next endpoint
```

## Baseline (always first)

```text
□ python3 tools/web/race_probe.py --url <ep> --body <b> -H <h> \
    --baseline-count 5 --count 0 --no-barrier --challenge <name>
□ the serial signature recorded: [___, ___, ___]
□ the "win" shape is NOT in the serial set (or it's not a race)
```

## The raced run

```text
□ python3 tools/web/race_probe.py --url <ep> --body <b> -H <h> \
    --concurrency N --count N --baseline-count 5 \
    --signature-mode <m> --write-ack --challenge <name>
□ concurrency matches the worker-pool ceiling
□ one request per connection (--concurrency opens N conns)
□ --url-b for the two-different-requests form
```

## Read the result

```text
□ max_in_flight — ≥2 means real overlap; 1 means inconclusive
□ the status/body split — does a crossed shape appear?
□ the STATE — GET the resource: did the effect double/cross?
□ the pair attributed — which two slots crossed?
□ NOT a win if: status-only, no state change, max_in_flight=1
□ a timeout/reset slot = unknown — discard it
□ a constraint-500 = falsifier — record it
```

## Verify the effect

```text
□ the crossed state is a PRIMITIVE — what does it unlock?
□ money → buy the gated item
□ token → confirm the pending change
□ identity → log in as the owned account
□ the flag is read from a LIVE response — not the crossed state
```

## Record

```text
□ hooks.py post-probe --verdict confirms --evidence-kind impact
□ --evidence = the raced split + the state read (verbatim)
□ --response = the tool output + the state read the excerpt came from
□ --hypothesis-id set
□ a falsifier → the ledger + knowledge/attempts/<name>.json (the reopen-if)
```

## Re-roll / escalate

```text
□ inconclusive → fix delivery, re-roll (never record as a negative)
□ 3 clean real-overlap no-cross runs → falsifier — record it
□ --reset-url between rolls — restore the starting state
□ budget out → decide.py escalate: chain_match→reclassify→writeup→novel_plan→fanout→solver
□ --strategy-used for each rung
```

## The one-line flow

```text
inventory → window → falsifier → baseline → race → max_in_flight → split →
state → attribute → verify → record → re-roll or falsify
```
