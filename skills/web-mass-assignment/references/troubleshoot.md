# Troubleshoot — when the mass-assignment probe does nothing

## "The field just doesn't land"

Ordered causes, cheapest first:

1. **allowlist** — the binder whitelists. Read-back shows control state.
   → nested under an allowed parent (`{"profile":{"role":..}}`),
   → the update endpoint (`PATCH` — wider allowlist),
   → a different carrier (form vs JSON).
2. **strict schema** — `400 unknown property` on JSON.
   → form/multipart carrier (different parser, maybe no schema),
   → `PATCH`/`PUT` (different binder).
3. **serializer-hidden** — field stores, never returned.
   → exercise the decision directly (`/admin`, the gated route).
4. **cache** — read-back is stale.
   → `?cb=<rand>`; a second representation (`/api/me` vs detail).
5. **model absence** — the field isn't on the model.
   → check admin/sibling views; the model may genuinely be narrow —
   that's the class falsifier.

## "The field lands but nothing changes"

The stored-but-inert case — the gate reads elsewhere:

- find the gate's real field: diff a real admin's record vs yours
  (`GET /api/users/<admin_id>` if readable, or source);
- try sibling semantics: `is_staff` where `role` was inert,
  `permissions` where `is_admin` was;
- the gate may read a JWT claim — the bound field lands in the RE-ISSUED
  token after re-login (test: log out, log in, re-hit the gate).

## "The endpoint 400s on everything"

The baseline is broken before the probe:

- control body wrong — check the form's real field names;
- missing required param the allowlist demands (`password_confirmation`,
  `terms` checkbox);
- CSRF token missing on the form carrier;
- content-type mismatch — `application/json` sent as form.

## "The field lands but the response is 500"

Type/coercion crash — `role:"admin"` on an enum-typed column, `groups:
"admin"` on a join-table array. The 500 says the binder TRIED; the
right type may land: `groups:[{"id":1}]`, `role_id:1`,
`role:"user"` (a valid enum) as a control-value probe.

## "Two requests, one diff — can't tell which field"

The attribution rule — ONE extra field per canary. Two fields in one
request means the diff can't be attributed; split into two canaries.

## "The write succeeds but the object is broken"

PUT-wipe or a type-corrupting field — `{"role":..}` alone on PUT
zeroed the rest; `balance:"a lot"` corrupted the column. Always the
full control body + extras on PUT; canary VALUES the column type
accepts (`balance:9999` not `balance:"lots"`).

## "Every endpoint drops it"

Falsifier at the BINDER-FAMILY depth — the model's binders all allowlist.
The class is dead on the binders; check `/import`, admin paths, GraphQL
mutations (different binder code paths), then record the model-level
falsifier and move classes.

## "The control differs run to run"

Shared-instance churn — other users' writes change `GET` outputs. Read
a SELF-scoped endpoint (`/api/me` not `/api/users`) for a stable
control.
