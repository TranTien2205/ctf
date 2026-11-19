# Workflow — the bounded race-condition engagement

The end-to-end loop: from "this looks like a check-then-act" to a verified
crossed state or a recorded falsifier. Bounded — the budget rule applies.

---

## 0. Before the class

The skill runs after the router names the class. Do the gate first:

```bash
python3 tools/classify.py "<obs>"                    # name the class
python3 tools/chain_match.py --source <dir> --record <name>   # a card that already solved this shape
python3 tools/decide.py <name>                        # what the controller says next
```

A matching chain card (ApexSurvive, SSOS) hands back the exact confirming
probe — run *that* before inventing one.

## 1. Recon — inventory the writable surface

```bash
# list every state-changing endpoint
grep -rhoE '"/(api/)?[a-z0-9_/-]+"' /tmp/bundle 2>/dev/null | sort -u | grep -iE \
  '(redeem|buy|vote|transfer|withdraw|verify|book|claim|register|order|reset|invite|pay|use|spin|join|bid|convert|refund|accept|submit|apply)'
```

Pick the endpoints that are (a) writable AND (b) checked — a conditional
update, not a blind insert. Rank them by flag-proximity: money → token →
account → limit.

## 2. Map the window — read, decide, work, write

For the chosen endpoint, find the four steps in source (or infer from the
response):

```text
1. read  — the SELECT/get that loads the record
2. decide — the if that gates on the read
3. work   — email/render/fetch/second-query (the window's width)
4. write  — the UPDATE/INSERT/commit
```

The window is 1→4. The work in step 3 is what makes it winnable.

## 3. Check the falsifier — is the window even open?

Before spending the write budget, look for the defence that closes it:

```bash
grep -rnE '(FOR UPDATE|select_for_update|with_for_update|SERIALIZABLE|UNIQUE|findOneAndUpdate|ConditionExpression|updateMany|\.update\(.*where|F\()' "$SRC"
```

- **Found** (atomic update / lock / constraint / serializable) → the class is
  closed for this endpoint — record the falsifier, move to the next endpoint.
- **Not found**, but a transaction wraps the pair → still open at READ
  COMMITTED — proceed.

## 4. Baseline — what serial produces

```bash
python3 tools/web/race_probe.py --url "$BASE/api/redeem" \
  --method POST --body '{"code":"XYZ"}' -H 'Cookie: session=...' \
  --baseline-count 5 --count 0 --no-barrier --challenge <name>
```

Record the serial signature: `[200, 409, 409, 409, 409]`. A "win" shape that
appears serially is not a race — recalibrate what you're proving.

## 5. The raced run

```bash
python3 tools/web/race_probe.py --url "$BASE/api/redeem" \
  --method POST --body '{"code":"XYZ"}' -H 'Cookie: session=...' \
  --concurrency 20 --count 20 --baseline-count 5 \
  --signature-mode status --write-ack --challenge <name>
```

Read: `max_in_flight` (did they overlap), the status/body split, versus
baseline.

## 6. Decide from the result

| Result | Meaning | Next |
|---|---|---|
| `max_in_flight`=1 | serialized, no overlap | inconclusive — fix delivery, re-roll |
| all responses = serial-loser shape | window narrower than burst | interleave/stall, or pathological input |
| crossed state (2×200 where baseline=1) | race confirmed | attribute the pair, verify the effect |
| some winners, clean losers, no cross | defence held under real overlap | falsifier — record, move on |

## 7. Attribute and verify the effect

The crossed state is a *primitive*, not a flag. Verify what it bought:

```bash
# the doubled effect
curl -s -b 'session=...' "$BASE/api/account" | python3 -c 'import sys,json;print(json.load(sys.stdin))'
# the token in the mailbox, the owned account's login, the bought item
```

Then the downstream check the effect passes: buy the gated item, use the
crossed token, log in as the owned account.

## 8. Record through the gate

```bash
python3 tools/hooks.py post-probe <name> --class web-race-condition \
  --hypothesis-id <h> --verdict confirms --evidence-kind impact \
  --evidence "raced run [200×2,409×18] vs baseline [200,409×4], max_in_flight=20; balance=-100 (floor 0)" \
  --response "<the tool output and the state read the excerpt came from>"
```

The `--evidence` excerpt must be a substring of `--response` — the gate checks.

## 9. Re-roll protocol

- `inconclusive` → lower `--concurrency`, or switch burst→interleave; re-roll.
- `--reset-url`/`--reset-body` restores the starting state between rolls.
- 3 clean re-rolls with real overlap and no crossed state → the window is
  closed — record the falsifier, move endpoint or class.

## 10. Stop conditions (the budget)

```text
per mechanism class: 5 probes or 15 active minutes → park or switch layer
per challenge:       25 probes or 45 active minutes → the controller answers escalate
escalation rungs:    chain_match → reclassify → writeup_search → novel_plan → fanout_sweep → solver_handoff
```

A spent budget is not the end — `decide.py` names the cheapest untried rung.
Record each with `state.py --strategy-used`.

## 11. The blast-radius pre-flight

Before any `--write-ack` run on a shared instance:

- the object is yours (your account, your code, a test entity)
- the effect is bounded and reversible
- a one-shot target (SSOS's startup-flag) is confirmed fresh — a consumed
  instance is unrecoverable for everyone
- no negative-balance or corrupted state lands on a shared demo object
