# Read-back protocol deep — the four-leg method, formally

## Leg 1 — control

```bash
curl -X POST "$BASE/api/register" -H 'Content-Type: application/json' \
  -d '{"username":"ctrl_001","password":"x"}' > ctrl.txt
curl "$BASE/api/users/ctrl_001" > ctrl_rb.txt
```

The control establishes three baselines: the endpoint works, the object
exists, and the DEFAULT field values (`"role":"user"` is the baseline
the canary must beat). A control `200` is the endpoint's health; the
read-back is the model's default.

## Leg 2 — canary

```bash
curl -X POST "$BASE/api/register" -H 'Content-Type: application/json' \
  -d '{"username":"can_001","password":"x","role":"admin"}' > canary.txt
```

**ONE extra field** — the attribution rule. Two fields in one canary
makes the diff unattributable. The canary's USERNAME differs from the
control's (paired accounts, not mutations of the same object).

## Leg 3 — read-back

```bash
curl "$BASE/api/users/can_001" > rb.txt    # different endpoint
# or the object detail / admin view / a second representation
```

The three outcomes:

| `rb.txt` shows | Verdict |
|---|---|
| `role:"admin"` | STORED → leg 4 |
| `role:"user"` | endpoint falsifier |
| `role` absent | serializer-hidden → exercise directly |

The cached-view trap: `role:"user"` from a stale representation — re-GET
with `?cb=<rand>` before recording.

## Leg 4 — decision exercise

```bash
curl -b "$JAR" "$BASE/admin"            # role gate
curl -b "$JAR" -X POST "$BASE/checkout" # totals gate
curl -b "$JAR" "$BASE/flag"             # verify gate
curl -b "$JAR" "$BASE/premium"          # plan gate
```

The decision is whichever gate the field gates — `check_admin()`,
`totals()`, `verified_required()`, `plan_required()`. A `200` where the
control session gets `403` is the decision-diff.

## The paired-account rule

Control and canary are SEPARATE accounts — `ctrl_001` and `can_001`,
not the same record mutated. A canary write on the control account
contaminates the baseline.

## The read-back-vs-echo rule

The write's `200` response (the echo) shows the parser's view —
`{"role":"admin"}` may appear while `save()` drops it. The `GET`
through a DIFFERENT endpoint is the store's truth.

## The serializer-hidden case

Field stores, never returns — `GET` shows `{"username","id"}` while
`role` sits in the DB. Read-back is blind; exercise the decision
directly — `200` on the gated route proves storage without read-back.

## The second-representation fallback

`GET /api/me` narrow → try `GET /api/users/<id>`, the admin view, the
detail page, a different serializer — the field may appear on one
representation and not another.

## The JWT re-issue leg

`role` stored, gate reads the TOKEN's claim — log out, log in; the
re-issued token carries the bound `role`. The decision exercise after
re-login is the true test.
