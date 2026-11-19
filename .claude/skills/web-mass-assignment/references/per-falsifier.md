# Per-falsifier — each falsifier's shape, its kill-depth, its open cells

## Falsifier 1 — `400/422 unknown property` (content-type depth)

The parser's schema rejects extras. `{"role":"admin"}` → `400`.

- **Kills**: extras on the JSON path for that endpoint.
- **Open**: `role=admin` form (different parser); multipart; `PATCH`/
  `PUT` (different schema); `{"profile":{"role":..}}` (schema validates
  the parent, not contents); `?role=` query.
- **The leak**: a named rejection (`"role must be one of: user,admin"`)
  confirms `role` exists and is an enum — the falsifier leaks the model.

## Falsifier 2 — `200` + dropped on read-back (endpoint depth)

The binder consumed the request and discarded the extra key — `permit`,
`$fillable`, `[Bind]`, `pick`.

- **Kills**: flat extras on that endpoint.
- **Open**: `{"profile":{"role":..}}` nested under an allowed parent;
  `user[role]=admin` prefixed; `PATCH`/`PUT` (wider allowlist);
  `/import` (bulk binder); `roles:["admin"]` array (the allowed field
  may be array-typed).

## Falsifier 3 — dropped on ALL carriers (binder-family depth)

Flat, nested, prefixed, array, typed, JSON, form, multipart, query —
every binder drops it.

- **Kills**: the model's conventional binders.
- **Open**: `/import`/bulk (different code path); GraphQL mutations
  (args schema is a separate binder); `/admin/*` (needs a privilege
  edge); method-override (`?_method=`).

## Falsifier 4 — no privileged fields exist (model depth)

`GET` responses on EVERY object show no `role`, `is_admin`, `balance`,
`verified`, `plan` — the model is genuinely narrow. `role` lives in a
separate `admins` table; `balance` in a `wallets` table the user-model
never exposes.

- **Kills**: the class on this app — nothing privileged to bind.
- **Open**: the OTHER models' binders — `POST /wallets` with a bound
  `balance`; `POST /memberships` with a bound `role`; `POST /orders`
  with a bound `price` (the economic model, not the user model).

## Falsifier 5 — stored but unchanged decision (semantic depth)

`role:"admin"` STORES — read-back confirms — but `/admin` `403`s. The
gate reads `is_staff`, `permissions`, a join table, or a JWT claim.

- **Kills**: `role` as a decision-changer.
- **Open**: the field the gate ACTUALLY reads — `is_staff`,
  `permissions`, `groups`, `access_level`; the JWT re-issue edge
  (re-login carries `role` in the token); a different decision the
  field drives (display, a totals computation).

## The falsifier-to-cells map

| Falsifier | Dead cells | Live cells |
|---|---|---|
| `400` JSON | json/flat on this endpoint | form, multipart, nested, PATCH, PUT, query |
| `200`+drop | flat on this endpoint | nested, prefixed, array, typed, other endpoints |
| drop-all | all carriers on all endpoints | /import, GraphQL, /admin, override |
| model absent | all user-model fields | other models' binders |
| inert `role` | `role` semantic | `is_staff`, `permissions`, JWT re-issue |

## The pair discipline

Every falsifier needs a CONTROL: `role:"user"` on the canary's read-
back is the falsifier ONLY because the control also showed `role:"user"`.
A canary-only `role:"user"` is ambiguous — `user` may be the default
OR the drop's product. Byte-identical = falsifier; canary > control =
bound.
