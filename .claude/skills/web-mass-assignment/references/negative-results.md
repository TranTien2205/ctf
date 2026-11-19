# Negative results — recording mass-assignment dead ends so they stay dead

## The honest-null principle

A mass-assignment negative is VALUABLE — it closes a cell of the
matrix so the next session doesn't re-walk it. Record every falsifier
with its DEPTH: which content-type, which endpoint, which carrier.
"Nothing worked" is useless; "`role` dropped by JSON binder on
POST /register, allowlist at the endpoint layer" is a map.

## The negative taxonomy

| Negative | The record |
|---|---|
| `400 unknown property` on JSON | schema falsifier — content-type cell |
| `200` + field dropped on read-back | allowlist falsifier — endpoint cell |
| field stored, gate unchanged | inert-field null — semantic cell |
| field stored but never returned | serializer-hidden — exercise-only |
| no privileged fields in model | model-level falsifier — class dead |
| `400` on control body | baseline broken — fix shape first |

## What to record per falsifier

```bash
python3 tools/hooks.py post-probe <ch> \
  --request "POST /register role=admin (json)" \
  --verdict falsified --class web-mass-assignment \
  --hypothesis-id <id> --evidence-kind class \
  --evidence 'readback "role":"user" identical to control' \
  --response "$(cat readback.json)"
```

And in `../field-notes.md`:

```
## POST /register — endpoint falsifier
- control `{"u":..,"p":..}` → `{"role":"user"}` on /api/me
- canary `+"role":"admin"` → `{"role":"user"}` — dropped at binder
- carrier: JSON flat; form path untested
- depth: ENDPOINT (the allowlist lives in this route's binder)
- remaining cells: form/multipart, PATCH /users/me, nested profile
```

## The depth-annotated kill map

```
matrix = {
  "POST /register": {
    "json/flat":    "FALSIFIED — allowlist drop",
    "form/flat":    "FALSIFIED — same drop",
    "json/nested":  "untested",
    "multipart":    "untested"
  },
  "PATCH /users/me": {
    "json/flat":    "FALSIFIED — drop",
    "json/nested":  "CONFIRMED — profile.role stored",
    ...
  }
}
```

The matrix is the honest state — a cell marked "untested" is a live
lead, a cell marked falsified is spent.

## Inert-field negatives

`role:"admin"` STORED, `/admin` still `403` — the field bound but the
gate reads `is_staff`. Record:

```
- role:admin stored (readback confirmed)
- GET /admin → 403 identical to control session
- verdict: INERT — gate reads elsewhere; is_staff is the next semantic
```

An inert result is not a falsifier — the binder binds; the FIELD was
wrong. Different negative, different next step.

## The serializer-hidden trap

Field stored, never returned — the `GET` can't confirm. Record "stored,
serializer-hidden" and exercise the decision directly; don't falsify
on read-back absence alone.
