# Per-endpoint map — where mass assignment lives, by endpoint shape

## `POST /register`, `/signup`, `/users`

The canonical surface — a model object created from the request body.

- **Probe**: documented body + ONE privileged field (`role`, `is_admin`,
  `balance`, `verified`, `plan`).
- **Read-back**: `GET /api/users/<name>`, `/api/me`, profile.
- **Exercise**: the gated route the field unlocks.
- **Notes**: register endpoints sometimes hash passwords and copy the
  rest — `User.create({...req.body, password: hash})` merges extras
  around the hash.

## `PATCH`/`PUT /users/:id`, `/profile`, `/me`, `/settings`

The second binder — usually WIDER than register because the profile is
meant to be editable. The allowlist covers display fields
(`display_name`, `bio`, `avatar`) while the model still carries `role`,
`verified`, `balance`.

- `PATCH` = merge — deep-merge sites where `{"profile":{"role":..}}`
  reaches nested objects.
- `PUT` = replace — omitted fields reset; extras bind if the replace
  target accepts them.
- Probe `PATCH` first — merge semantics preserve what PUT would wipe.

## `POST /orders`, `/checkout`, `/cart`, `/billing`

Domain objects with economic fields: `price`, `discount`, `total`,
`shipping`, `tax`, `coupon`, `currency`, `unit_price`, `quantity`.

- The bound field must reach the TOTAL — `price`/`discount` bound then
  exercised at checkout.
- `total`/`subtotal` as bindable fields = the carried-lie overlap with
  trust-in-earlier-step (web-logic-flaw).

## `/import`, `/seed`, `/bulk`, `/migrate`, `/admin/users`

Bulk binders — often written for operators, bound without the public
form's allowlist. `POST /admin/users` needs a privilege edge first
(chain order: find the role edge, THEN the admin binder).

## GraphQL mutations

`createUser`, `updateUser`, `updateProfile` — the args schema is the
binder. Introspection (`{__schema{mutationType{fields{name args{name
type{name}}}}}}`) dumps every bindable arg — a `role`/`isAdmin` arg on
a mutation is mass assignment spelled in the schema. Also: input-object
types with extra fields (`UserInput` carrying `role`).

## `/password/reset`, `/verify`, `/invite`

State-transition objects: `verified`, `token`, `expires`, `used` fields
bound at creation. `verified=true` bound at register skips the whole
verification edge.

## `/comments`, `/reviews`, `/posts`

Low-stakes objects — but `author_id`, `user_id`, `approved`,
`moderated` fields bind the same way. `author_id` bound to another user
= forged authorship (the IDOR-adjacent edge — file under IDOR when the
bug is object ACCESS, mass-assignment when it's the bound FIELD).

## The method-difference table

| Method | Binder behavior | Priority |
|---|---|---|
| `POST` | create — register allowlist usually tightest | second |
| `PATCH` | merge — widest, deep-merge nested | FIRST |
| `PUT` | replace — binds extras OR wipes omissions | third |
| `GET`+params | query binder — `params` union reaches the same model | test with `--method GET` |
| `POST`+`_method=PUT` | override routing | edge — try when others dead |
