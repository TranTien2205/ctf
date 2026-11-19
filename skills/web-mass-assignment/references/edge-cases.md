# Edge cases — where mass-assignment analysis breaks

## The serializer-hidden stored field

The field stores but no response shows it: `role:"admin"` persists in
the DB, `GET /api/me` returns `{"username":..,"id":..}` only. The
read-back falsifies wrongly. Detection: exercise the field directly —
hit the gated route; a `200` there proves storage without read-back.

## The echo-vs-store divergence

Mongoose `strict:true` echo: `{"role":"admin"}` appears in the POST
response (set on the instance) while `save()` drops it (not a schema
path). The echo lies about storage — read-back only.

## The type-mismatch near-miss

`role:1` binds to an INTEGER column, `role:true` to boolean, `role:
"admin"` to string — each may reach a different coercion path. A
rejected `role:1` doesn't falsify `role:"admin"`. One wrong-type retry
per semantic, not per spelling.

## The case-insensitive binder

ASP.NET model binding and some PHP frameworks bind case-insensitively:
`ROLE`, `Role`, `role` all reach `Role`. A rejected `role` might be a
serializer quirk, not the binder — `Role` is worth one probe when the
stack is .NET.

## The PUT-wipe footgun

`PUT` REPLACES the object: `{"role":"admin"}` alone may wipe
`username`/`password` and break the account. Probe `PUT` with the FULL
control body + extra fields, or the replace zeroes the rest.

## The PATCH-vs-POST allowlist difference

The register `POST` allowlists `[username, password]`; the profile
`PATCH` allowlists `[display_name, bio, avatar, role]` — a wider set
because profile-edit needs more fields. The second binder is usually
the live one.

## The nested-parent allowlist hole

Flat `role` rejected, but `{"profile":{"role":"admin"}}` survives —
the allowlist covers `profile` as a unit and the deep merge reaches
the nested `role`. Also `{"settings":{"admin":true}}`,
`{"preferences":{"role":..}}` — every allowed parent is a tunnel.

## The array-vs-scalar type gap

`role:"admin"` (scalar) rejected by a schema expecting `roles:[]` —
but `roles:["admin"]` binds. `group` vs `groups:[{id:1}]`. The model's
field TYPE selects the shape; the scalar-vs-array pair is one semantic,
two probes.

## The duplicate-key parser gap

`{"role":"user","role":"admin"}` — JSON parsers take last; a validator
reading the first and the binder taking the last = the parse-layer
two-validator gap. Form `role=user&role=admin` — first-vs-last parser
semantics decide.

## The foreign-key blind spot

`role` isn't on `users` — it's on the `memberships`/`user_roles` join
table. The flat field misses while `membership[role]` or
`{"membership":{"role":..}}` binds through a nested-association accept
(`accepts_nested_attributes_for`, `$request->user()->roles()->...`).

## The timestamps/`_t` fields

`createdAt`/`updatedAt` (Mongoose timestamps), `created_at`, `_t`
(discriminator), `__v` — bindable fields nobody guards. `_t:"AdminUser"`
changes the sub-schema to the privileged discriminator.

## The GraphQL args-only surface

`mutation{updateUser(id:9,role:ADMIN)}` — the args schema IS the binder;
introspection spells every bindable arg. A `role` arg on a mutation is
mass assignment in the schema itself.

## The method-override carrier

`POST /users/me?_method=PUT` or `X-HTTP-Method-Override: PUT` — POST's
validation (maybe allowlisted) routing through PUT's handler (maybe
unguarded). The override pair is a different binder.
