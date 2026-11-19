# Evidence map — what proves each part of the finding

## The storage evidence (class)

`GET` through a DIFFERENT endpoint shows the bound field:

```bash
curl -b "$JAR" "$BASE/api/me"          # {"role":"admin"}
curl -b "$JAR" "$BASE/api/users/9"     # {"role":"admin"}
```

The verbatim bytes — `"role":"admin"` as it appears — go in
`--evidence`; the full response goes in `--response`.

## The control evidence

The control's read-back shows the DEFAULT:

```bash
curl "$BASE/api/users/ctrl_001"        # {"role":"user"}
```

`role:"user"` on the control + `role:"admin"` on the canary = the
attributed diff. Byte-identical = the falsifier.

## The decision evidence (impact)

The gated route/total/state changes:

```bash
curl -b "$JAR" "$BASE/admin"           # 200 + {"users":[...]}
curl -b "$JAR" -X POST "$BASE/checkout" # {"total":0}
curl -b "$JAR" "$BASE/flag"             # the verify-gated flag
curl -b "$JAR" "$BASE/premium"          # plan-gated content
```

The `200` where the control session `403`s, or the bound total.

## The echo-caution evidence

The write's own response is NEVER storage:

```bash
# echo — parser's view, may lie
POST /register → {"id":9,"role":"admin"}      # maybe bound-then-dropped
# read-back — store's truth
GET /api/users/9 → {"role":"user"}             # dropped at save
```

The echo-artifact proves parse-reached, not storage.

## The serializer-hidden case

Field stores, never returns — `GET` shows `{"username","id"}` only.
Evidence is the DECISION alone:

```bash
curl -b "$JAR" "$BASE/admin"           # 200 — the field is real
```

Record "stored, serializer-hidden" — don't falsify on read-back
absence.

## The inert-field evidence

```bash
GET /api/me → "role":"admin"            # stored
GET /admin → 403                        # gate unchanged
```

Inert — the field bound but the gate reads elsewhere. A null result:
record it, don't cite it.

## The falsifier evidence

```bash
GET /api/me (canary) → "role":"user"   # dropped
GET /api/me (control) → "role":"user"  # identical
```

Byte-identical canary/control = the falsifier — the binder dropped
the extra field.

## The command shapes

```bash
# class evidence
python3 tools/hooks.py post-probe <ch> \
  --request "PATCH /users/me role=admin" --verdict confirms \
  --class web-mass-assignment --hypothesis-id <id> \
  --evidence-kind class --evidence '"role":"admin"' \
  --response "$(cat rb.txt)"

# impact evidence
python3 tools/hooks.py post-probe <ch> \
  --request "GET /admin" --verdict confirms \
  --class web-mass-assignment --hypothesis-id <id> \
  --evidence-kind impact --evidence '200 + "users"' \
  --response "$(cat admin.txt)"

# falsifier
python3 tools/hooks.py post-probe <ch> \
  --request "PATCH /users/me role=admin" --verdict falsified \
  --class web-mass-assignment --hypothesis-id <id> \
  --evidence-kind class --evidence 'rb "role":"user" = ctrl' \
  --response "$(cat rb.txt)"
```
