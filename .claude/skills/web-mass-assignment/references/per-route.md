# Per-route — the mass-assignment surface per route shape

## `POST /register`, `/signup`, `/users`

The create binder — the canonical surface. The allowlist here is
usually TIGHTEST (the form declares exactly `[username, password]`).
Probe `role`/`is_admin`/`verified`/`balance` flat; the register's own
allowlist often survives while the update binder doesn't.

## `PATCH /users/me`, `/:id`, `/profile`, `/settings`

The update binder — usually the WIDEST (the profile is meant to be
editable). First probe here. Deep-merge site: `{"profile":{"role":..}}`
reaches nested objects. `PATCH` = merge (extras survive), `PUT` =
replace (extras bind or the replace wipes others).

## `POST /orders`, `/checkout`, `/cart`, `/billing`

Domain objects with economic fields. Probe `price`, `discount`,
`total`, `unit_price`, `currency`, `shipping`, `tax`, `quantity`. The
bound field must reach the TOTAL — `price` bound then exercised at
checkout.

## `POST /import`, `/seed`, `/bulk`, `/migrate`

Bulk binders — operator-written, often unguarded. `POST /admin/users`
needs a privilege edge first. Bulk endpoints may bind fields the
per-object forms strip.

## GraphQL mutations

`createUser`, `updateUser`, `updateProfile`, `updateSettings` — the
args schema is the binder. Introspection spells every bindable arg —
`role`, `isAdmin`, `permissions` as literal args. Input-object types
carry extra fields the form's mutation never sends.

## `POST /password/reset`, `/verify`, `/invite`

State-transition objects — `verified`, `token`, `expires`, `used`
bindable at creation. `verified:true` bound at register skips the
verification edge entirely.

## `POST /notes`, `/comments`, `/reviews`, `/posts`

Low-stakes objects — `author_id`, `user_id`, `approved`, `moderated`
bind the same way. `author_id` forged = IDOR-adjacent authorship;
`approved:true` bound = moderation-skip.

## `GET` routes with query params

`GET /users?role=admin` — the params-union reaching the binder; a
mutating GET is a second bug. `binding_probe.py --method GET` tests
the carrier.

## `POST /admin/*`

The widest binder — but needs a privilege edge FIRST. Chain order:
find the role edge (via `/import` or a first bound `role`), then the
admin binder's own mass-assignment writes the flag-visible field.
