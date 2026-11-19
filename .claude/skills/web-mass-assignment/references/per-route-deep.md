# Per-route deep — the binder at every route shape, with its probes

## `POST /register`, `/signup`, `/users` — create

The canonical binder. The allowlist here is `[username, password,
email]` usually — the form's declared fields. `User.create(req.body)`,
`User.objects.create(**data)`, `User::create($request->all())`.

**Probe set**: `role`, `is_admin`, `isAdmin`, `is_staff`, `verified`,
`is_active`, `balance`, `plan`, `permissions`, `groups`, `_t`, `type`.
Then carriers: flat JSON → form `role=admin` → nested `{"profile":
{"role":..}}` → `user[role]=admin` → `role[]=admin` → `role:1`/`true`.

**Trap**: `password_confirmation`, `terms`, `invite_code` — required
params the control must carry. A `400` on the control body = broken
baseline, not a class signal.

## `PATCH`/`PUT /users/me`, `/:id`, `/profile`, `/settings` — update

The second binder — usually WIDER because the profile is meant to be
editable. `PATCH` merges (deep-merge sites), `PUT` replaces.

**`PATCH` probe set**: flat `role` → nested `{"profile":{"role":..}}` →
`{"settings":{"admin":..}}` → `{"preferences":{"is_admin":..}}` →
`verified`, `balance`, `plan`, `permissions`, `groups`, `roles[]`.

**`PUT` probe**: FULL control body + extras — the replace wipes
omissions.

**The `me` vs `:id` line**: `/users/me` is your own — always probe `me`.
`/users/9` on another's record is IDOR + a rules violation.

## `POST /orders`, `/checkout`, `/cart`, `/billing` — economic

Domain objects. `price`, `unit_price`, `discount`, `coupon`, `total`,
`subtotal`, `shipping`, `tax`, `currency`, `quantity`, `status`,
`payment_status`, `order_status`.

**Probe**: `price:0`, `discount:100`, `total:0`, `quantity:-1`,
`currency:"AAA"` — the fields the totals code reads. Then exercise:
`POST /checkout` — does the bound `price` reach the total?

## `POST /import`, `/seed`, `/bulk`, `/migrate` — bulk

Operator endpoints — least-tested, often unguarded. `POST /import
[{"u":"x","role":"admin"}]` — the bulk binder binds array objects; the
allowlist may be absent where the per-object form's is present.

**`POST /admin/users`** — the widest binder, needs a privilege edge
first. Chain: bound `role` → `/admin` opens → `/admin/users` writes
the flag field.

## GraphQL mutations — args schema

```graphql
mutation{ createUser(input:{username:"x",role:ADMIN,verified:true}) }
mutation{ updateUser(id:9,input:{isAdmin:true,permissions:["*"]}) }
```

Introspection spells every arg — `UserInput`/`UpdateUserInput` types
carry `role`, `isAdmin`, `permissions`, `internal`, `debug`. Extra
input-object fields are mass assignment in the schema.

## `POST /password/reset`, `/verify`, `/invite` — state objects

`verified`, `token`, `expires`, `used`, `code`, `onboarding_complete`,
`activated`. `verified:true` bound at register skips the verification
edge — the state-transition model's fields are the workflow-skip.

## `POST /notes`, `/comments`, `/reviews`, `/posts` — content objects

`author_id`, `user_id`, `approved`, `moderated`, `flagged`, `deleted`,
`parent_id`, `project_id`. `author_id:1` forges authorship (IDOR-
adjacent); `approved:true` bound skips moderation.

## `GET` routes with params — the query carrier

`GET /users?role=admin` — `params`/`request.values` merge query into
the binder. A mutating `GET` is a second bug; the bound field reaching
it is the carrier.
