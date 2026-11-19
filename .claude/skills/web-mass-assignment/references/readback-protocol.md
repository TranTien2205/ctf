# Read-back protocol — the control/canary/read-back method

The whole class's evidence protocol in one module: control request,
canary request, independent read-back, decision exercise. Skipping a
leg produces unattributable results.

## The four legs

```
leg 1 — control:      POST the documented body, verbatim
leg 2 — canary:       POST the same body + ONE extra field
leg 3 — read-back:    GET the object through a DIFFERENT endpoint
leg 4 — exercise:     hit the route/total/decision the field gates
```

## Leg 1 — the control

```bash
curl -i -X POST "$BASE/api/register" \
  -H 'Content-Type: application/json' \
  -d '{"username":"ctrl1","password":"x"}' > ctrl.txt
```

The control establishes: the endpoint works, the object is created, and
the default field values. `GET /api/users/ctrl1` → `{"role":"user"}` is
the DEFAULT the canary must beat.

## Leg 2 — the canary

```bash
curl -i -X POST "$BASE/api/register" \
  -H 'Content-Type: application/json' \
  -d '{"username":"can1","password":"x","role":"admin"}' > canary.txt
```

Two response shapes matter:

- **echo**: `{"id":9,"username":"can1","role":"admin"}` — the field
  appeared in the WRITE response. Proves parsing, maybe binding — NOT
  storage (frameworks echo bound-then-dropped fields).
- **error**: `400 "unknown property: role"` — strict schema, the
  falsifier for this content-type.

## Leg 3 — the read-back

```bash
curl -i "$BASE/api/users/can1"        # DIFFERENT endpoint than the write
# or the object detail / admin view / a second representation
```

The deciding observation:

| Read-back | Verdict |
|---|---|
| `role: "admin"` | field STORED — class signal; proceed to leg 4 |
| `role: "user"` | binder dropped it — allowlist falsifier |
| `role` absent | serializer hid it — field may still be stored; check a second representation or the decision directly |

The cached-view trap: read-backs can hit cached representations. If the
write echoed `admin` and the read-back shows `user`, re-GET with a
cache-buster (`?cb=<rand>`) or read a different representation before
calling it a falsifier.

## Leg 4 — the decision exercise

```bash
curl -i -b "$JAR" "$BASE/admin"          # the route the role gates
# or POST /checkout — does the bound price/discount change the total?
```

The field is a finding only if it CHANGES a decision:

- `role:admin` + `/admin` returns `200` with privileged data → the role
  is REAL — confirmed at impact level;
- `role:admin` + `/admin` still `403` → the stored field is inert —
  the gate reads a different field (maybe `is_staff`, `permissions`,
  or a separate admin table). The bound field is a null result.

## `binding_probe.py` — the automated legs 2–3

```bash
python3 tools/web/binding_probe.py \
  --url "$BASE/api/register" \
  --body 'username=p&password=x' \
  --readback "$BASE/api/me"
```

The tool runs the default field set with a canary value and grades each:
echoed in write response vs LANDED on the read-back. `--fields` narrows
to specific names; `--method GET` tests the query carrier; `--headers`
carries auth. A "landed" grade is the class candidate — leg 4 remains
manual.

## The paired-account discipline

Control and canary must be SEPARATE accounts (or objects): a canary
field on the control account contaminates the baseline. Fresh
`username` per request; keep write concurrency low on shared instances
(the AGENTS.md safety rule — test on objects you created, never mutate
another player's records until the boundary is proven).

## Attribution — what each leg rules out

- control `200` + canary `400` → the FIELD caused the rejection
  (schema knows it — maybe bindable with the right type).
- control `200` + canary `200` + echo diff → the field was received.
- echo diff + read-back same → stored somewhere the echo reflects.
- read-back diff + decision diff → the field is REAL — the full confirm.
