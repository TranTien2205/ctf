# Per-endpoint deep — each binder's surface, its allowlist shape, its probes

## `POST /register`, `/signup`, `/users` — the create binder

The tightest allowlist lives here usually: `[username, password, email]`
— the form's declared fields and nothing more. But `User.create(req.body)`
and `fill($request->all())` skip the allowlist entirely.

**Probe order**: `role` flat → `is_admin` → `verified` → `balance` →
nested `{"profile":{"role":..}}` → form carrier `role=admin` →
`user[role]` prefixed → typed `role:1`/`role:true`.

**The second create binder**: `POST /users` (admin-facing) vs `POST
/register` (public) — the admin one is wider but needs the privilege
edge. `POST /signup` vs `/register` may be different handlers with
different binders — probe both.

**The register-specific fields**: `password_confirmation`, `terms`,
`invite_code`, `referral` — required params the control body must
carry. A `400` on the control means the baseline is wrong, not the
class.

## `PATCH /users/me`, `/:id`, `/profile` — the update binder

The WIDEST binder — the profile is meant to be editable. `PATCH` =
merge semantics: `{"profile":{"role":..}}` deep-merges into the nested
object; flat `role` may drop while nested survives. The update
allowlist is usually `[name, bio, avatar, ...]` — wider than register's
but still a list; the nested tunnel is the reach.

**Probe order**: `role` flat → `{"profile":{"role":..}}` → `{"settings":
{"admin":..}}` → `verified` → `balance` → `plan` → `role[]` array →
`groups:[{id:1}]` FK array → `Role` case (.NET).

**The `me` vs `:id` difference**: `/users/me` resolves your own id;
`/users/:id` takes any id — probing another's id is the IDOR violation.
Always `me`.

## `PUT /users/:id`, `/profile` — the replace binder

`PUT` REPLACES: the body becomes the object. Extras bind if the model
accepts them; OMITTED fields reset to defaults (the wipe). `{"role":
"admin"}` alone on PUT zeroes `username`, `email`, `password`.

**Probe**: the FULL control body + extras — `{"username":"x","email":
"e","password":"p","role":"admin"}`. A `200` where PUT alone `500`s
(the missing required fields) is the wipe signature.

## `POST /orders`, `/checkout`, `/cart` — the economic binder

Domain objects: `item_id`, `product`, `quantity`, `price`,
`unit_price`, `discount`, `coupon`, `total`, `subtotal`, `shipping`,
`tax`, `currency`, `status`, `payment_status`.

**Probe**: `price:0`, `discount:100`, `total:0`, `quantity:-1`,
`currency:"XXX"` — the fields the totals code reads. The bound field
must reach the total: `POST /orders {"price":0}` → `POST /checkout` →
total `0` → flag item "purchased."

## `POST /import`, `/seed`, `/bulk`, `/migrate` — the bulk binder

Operator endpoints binding arrays/objects wholesale — least-tested,
often unguarded because "only admins call them." `POST /import` with
`[{"username":"x","role":"admin"}]` — the bulk binder's allowlist may
be absent where the per-object form's is present.

## GraphQL mutations — the args binder

```graphql
mutation{ createUser(input:{username:"x",role:ADMIN}) }
mutation{ updateUser(id:9,input:{role:ADMIN,verified:true}) }
```

The args schema IS the binder — introspection spells every arg.
`UserInput`/`UpdateUserInput` types carry fields the form's mutation
never sends: `role`, `isAdmin`, `permissions`, `internal`. Extra
input-object fields are mass assignment written in the schema.

## `POST /admin/*` — the admin binder

The widest — but needs a privilege edge first. Chain order: find the
role edge (a bound `role` on `/users/me` or `/import`), THEN `POST
/admin/users {"flag_visible":true}` — the admin binder's own mass-
assignment writes the flag field.
