# Evidence rules — what confirms mass assignment and what never does

## The two-observation standard

A mass-assignment confirm needs BOTH:

1. **Storage**: the extra field appears in a read-back — `GET
   /api/users/can1` → `"role":"admin"` — differing from the control's
   `"role":"user"`.
2. **Decision**: the field changes a decision — `/admin` returns `200`
   where the control session gets `403`; the checkout totals from the
   bound `price`; the `verified` gate opens.

One observation alone: stored-but-inert is a NULL result (the class bar
— a stored field never read is not a finding); decision-without-store
is attribution confusion (something else changed it).

## The verbatim requirement

`post-probe --verdict confirms` requires `--evidence` to be a substring
of `--response`. Quote the read-back's exact bytes:

```bash
python3 tools/hooks.py post-probe <ch> \
  --request "POST /api/register {username:can1,role:admin}" \
  --verdict confirms --class web-mass-assignment \
  --hypothesis-id <id> --evidence-kind class \
  --evidence '"role":"admin"' --response "$(cat readback_can1.json)"
```

Then the decision evidence separately:

```bash
python3 tools/hooks.py post-probe <ch> \
  --request "GET /admin (can1 session)" \
  --verdict confirms --class web-mass-assignment \
  --hypothesis-id <id> --evidence-kind impact \
  --evidence '200 + "users":[...]' --response "$(cat admin_200.txt)"
```

## The control requirement

Every confirm needs the control pair — the same endpoint, the documented
body, default values. `role:"admin"` on read-back means nothing until
the control's `role:"user"` is on record. Byte-identical canary/control
= the falsifier.

## What never confirms

- **The write echo**: `{"role":"admin"}` in the POST response proves
  parsing, not storage. Read-back only.
- **A `200` alone**: registration succeeds for ordinary users.
- **A stored field that changes nothing**: `role:"admin"` stored but
  `/admin` still `403` — inert, null result. Record it; don't cite it.
- **A field name in an error**: `"role must be one of: user, admin"`
  proves the field EXISTS — a candidate, not a stored write.
- **A second request differing in two ways**: control `{u,p}` vs canary
  `{u,p,role}` — only the `role` may differ.
- **Cached read-back**: a stale `role:"user"` falsifies wrongly —
  re-GET fresh before recording.
- **Chain-card logic**: `web-logic-flaw`'s Pachinko card is not a mass-
  assignment proof; this class is CATALOGUE — nothing here has solved
  one; say so in notes.

## The attribution table

| Observation | Attribution |
|---|---|
| canary echo `admin`, read-back `user` | echo artifact — dropped |
| canary read-back `admin`, control `user` | field stored |
| read-back `admin`, gate `403` | inert — gate reads elsewhere |
| read-back `admin`, gate `200` | **confirmed — decision changed** |
| canary `400 unknown property` | schema falsifier |
| nested `{"user":{"role":..}}` stores | deep-merge / prefix binder |

## Impact vs class grades

- **class**: the stored field diff (`"role":"admin"` vs control).
- **impact**: the decision diff (`/admin` 200, `-50` total, `verified`
  gate open).

Record class first, impact when exercised — they're different
`--evidence-kind` values and different response files.
