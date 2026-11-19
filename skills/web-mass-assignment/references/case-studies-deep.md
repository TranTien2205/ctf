# Case studies deep — the mass-assignment incident anatomy

## Study 1 — the `User.create(req.body)` register

**Shape**: Express + Mongoose. `User.create(req.body)` with a schema
carrying `isAdmin`, `balance`, `plan`. The form sends `username`,
`password`, `email`; the binder accepts `isAdmin:true` flat.

**The bug**: `create()` binds every SCHEMA path — `isAdmin` is a
declared schema field, so it binds. The schema's presence IS the
writable surface; the form's absence is irrelevant.

**The probe**: `{"username":"x","isAdmin":true}` → `GET /api/me` shows
`isAdmin:true` → `GET /admin` `200`s.

**The lesson**: Mongoose `create` binds schema paths, not form fields —
the schema is the allowlist by accident. `strict:false` or `Object.
assign` makes it worse (everything binds).

## Study 2 — the `permit` that included `role`

**Shape**: Rails. `User.update(params.require(:user).permit(:name,
:bio, :role))` — `role` IN the permit list. The developer allowed it
for an admin form and the same strong-params method served the public
`PATCH /users/:id`.

**The bug**: shared strong-params — the admin's `permit` list used on
the public endpoint. The allowlist is correct code; the SHARING is the
bug.

**The probe**: `PATCH /users/me` with `user[role]=admin` → stored →
admin route opens.

**The lesson**: a correct `permit` can still leak — check WHICH
permit list each endpoint uses.

## Study 3 — the `setattr` loop

**Shape**: Flask + SQLAlchemy.

```python
for k, v in request.json.items():
    setattr(user, k, v)
```

**The bug**: the loop binds every key to a model attribute — `role`,
`is_admin`, `balance` all land if they're columns. No signature, no
allowlist.

**The probe**: `{"role":"admin"}` → `GET` shows it → `check_admin()`
reads `user.role` → `200`.

**The lesson**: the `setattr`/`__dict__.update`/`merge` loop is the
silent bug — no TypeError, no schema, just binding.

## Study 4 — the deep-merge profile

**Shape**: `_.merge(user, req.body)` or `deepmerge` on PATCH. Flat
`role` filtered; `{"profile":{"role":"admin"}}` merges into the
existing `profile` object recursively.

**The bug**: the allowlist covers `profile` as a unit; the recursive
merge reaches `profile.role` the flat filter can't see. `_.merge`
walks `__proto__` too — the pollution overlap.

**The probe**: `{"profile":{"role":"admin"}}` → `profile.role` stores
→ the gate reading `user.profile.role` opens.

**The lesson**: deep-merge handlers are the nested-tunnel sites —
`profile`, `settings`, `preferences`, `metadata` parents.

## Study 5 — the `**json` TypeError leak

**Shape**: `User(**request.get_json())`. `TypeError: unexpected
keyword 'role'` on `{"role":"admin"}` — the signature rejects it.

**The leak**: the error NAMES the rejected field; a second probe with
a signature field (`email`? `is_active`? `verified`?) — the error for
THAT names whether it exists. The signature IS the schema, and the
TypeError leaks the writable set.

**The lesson**: the kwargs signature is a soft allowlist that leaks
itself — enumerate the signature by probing candidate fields and
reading which the TypeError accepts.

## Study 6 — the discriminator switch

**Shape**: Mongoose `{"_t":"AdminUser"}` bound — the discriminator
field selects the sub-schema. `AdminUser` carries `clearance`,
`admin_flag`, `permissions` the base `User` lacks.

**The probe**: `_t:"AdminUser"` at register → the `AdminUser` schema
binds → `clearance:"top"` binds on the second PATCH → the clearance-
gated flag opens.

**The lesson**: `_t`/`__t`/`type`/`user_type` are the schema-switch
fields — binding one changes the writable surface entirely.
