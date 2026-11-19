# Per-check deep — each guard's bypass mechanics

## The schema check — `additionalProperties:false`, `extra:forbid`

The parser validates the body's KEYS against a schema; unknown keys
`400`/`422`. Bypass paths:

- **form carrier**: `role=admin` form-encoded reaches a different parser
  with (often) no schema;
- **nested object**: `{"profile":{"role":..}}` — the schema validates
  `profile` as `type:object` without checking contents;
- **content-type confusion**: `application/json` schema-checked but
  `text/plain`/`application/x-www-form-urlencoded` bypassed;
- **update endpoint**: `PATCH`/`PUT` schemas may differ from `POST` —
  the update schema covers editable fields, maybe `role`.

## The allowlist check — `permit`, `$fillable`, `[Bind]`, `pick`

The binder accepts only declared keys; extras drop silently (`200`).
Bypass paths:

- **nested tunnel**: `{"profile":{"role":..}}` — `profile` is in the
  allowlist; the deep merge reaches `profile.role`;
- **prefixed**: `user[role]=admin`, `user.role=admin` — the allowlist
  covers `user`; the nested param reaches `role`;
- **second binder**: `PATCH`/`PUT` allowlists differ — `role` in the
  update's list but not register's;
- **array**: `roles[]`/`groups[]` — the allowlist covers `roles` as an
  array field.

## The type check — column/serializer types

`role` is `String`/`enum`/FK — the wrong type coerces or fails.
Bypass:

- `role:"admin"` (String) vs `role:true` (bool) vs `role:1` (enum int)
  vs `role:{"id":1}` (FK object);
- `groups:"admin"` `500`s (expects array) → `groups:["admin"]` or
  `groups:[{"id":1}]`;
- `verified:"yes"`/`"1"`/`true`/`1` — boolean-coercion variants.

## The readonly check — `attr_readonly`, `readOnly`, `editable:false`

Declared-readonly fields reject writes. Bypass:

- **create binder**: readonly may apply to updates only — `POST
  /register` may bind where `PATCH` refuses;
- **nested association**: `role` readonly on `User` but writable on
  `Membership` — `{"membership":{"role":..}}` reaches the child;
- **discriminator**: `_t` switching to a schema where the field IS
  writable.

## The ownership check — `403` on another's id

`PATCH /users/9` on another's record — `403` before the binder. Not a
mass-assignment block; an IDOR block. Probe your own `me`/`id` — the
ownership check is the scope boundary.

## The discriminator check — `_t`/`type`/`__t`

May be guarded (`_t` dropped) or may bind — switching the schema to the
privileged variant. Try `_t:"AdminUser"`, `type:"admin"`,
`user_type:"admin"`, `__t:"Admin"`.

## The optimistic-concurrency check — `version`/`__v`/`lock_version`

A bound `version` field can bypass "someone else changed it" — set it
high and the update wins. The concurrency field is itself mass-
assignable on most binders.
