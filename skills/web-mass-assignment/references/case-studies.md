# Case studies — mass-assignment shapes that appear in the wild

## Case 1 — the register `is_admin` (picoCTF-style)

An Express register endpoint: `User.create(req.body)` with a Mongoose
schema carrying `isAdmin`. The form sends `username, password`; the
binder accepts `isAdmin:true` flat. Read-back `GET /api/me` shows
`isAdmin:true`; `GET /admin` `200`s with the flag. One bound field —
the whole chain.

**Lesson**: the register binder isn't always the tight one; a permissive
`create` accepts what the form doesn't declare.

## Case 2 — the profile `role` (HTB-style)

A PATCH `/users/me` allowing `display_name`, `bio`, `avatar` — plus
`role`. The update binder's allowlist is wider than register's (the
profile is "meant to be editable"). `role:"admin"` binds; the admin
route opens. The register was clean; the update was the hole.

**Lesson**: the second binder is usually the live one — probe `PATCH`
before concluding.

## Case 3 — the nested tunnel (Rails-style)

`User.update(params.require(:user).permit(:name, :bio, profile_attributes:
[:theme]))` — `profile` is allowed as a unit; `user[profile_attributes]
[role]=admin` binds through the accepted nested key. The flat `role`
was dropped; the nested survived.

**Lesson**: `permit` covers the parent, not the child's fields — the
nested-association tunnel is the Rails-specific hole.

## Case 4 — the economic override (e-commerce CTF)

`POST /orders` accepting `product`, `quantity` — plus `price`. The
totals code read `order.price` (the bound field) not `product.price`
(the catalog lookup). `price:0` bound; checkout totalled `0`; the flag
item "purchased."

**Lesson**: the bound field reaching the TOTAL is the economic shape —
`price`/`discount`/`total`/`unit_price` all candidates.

## Case 5 — the `verified` skip (auth-flow CTF)

`POST /register` with `verified:true` bound — the verification email
step skipped; `GET /flag` (verify-gated) opened directly. The bound
`verified` was the whole edge.

**Lesson**: `verified`/`is_active`/`approved`/`activated`/`email_
verified_at`/`onboarding_complete` — the state fields are the workflow-
skip mechanism reached through the binder.

## Case 6 — the discriminator switch (Mongoose CTF)

`{"_t":"AdminUser"}` bound at register — the sub-schema switched to the
privileged discriminator, exposing `clearance`/`admin_flag` fields the
base schema lacked. The bound `_t` was the schema-switch.

**Lesson**: `_t`/`__t`/`type`/`user_type` — the discriminator fields
nobody guards.

## Case 7 — the chained admin binder

`PATCH /users/me {"role":"admin"}` → `/admin` opens → `POST /admin/users
{"flag_visible":true}` — the admin binder's own mass-assignment wrote
the flag-visible field. Two layers.

**Lesson**: the bound field is the EDGE; the second binder is the WRITE.
