# Edge catalogue — the edge cases that break mass-assignment analysis

## The serializer-hidden store

Field stores, never returns — `GET` shows `{"username","id"}` while
`role:"admin"` sits in the DB. Read-back blind; exercise the decision
(`GET /admin`) — `200` proves storage without read-back.

## The echo-lie

Mongoose `strict:true`: `role` sets on the instance, appears in the
POST response, drops at `save()`. Echo shows `admin`, store holds
`user`. The divergence IS the signal — read-back only.

## The dual-type column

`role` accepts `String` AND enum `["user","admin"]` — `role:"admin"`
binds, `role:1` `400`s, `role:true` `400`s. The typed failure isn't
the field's falsifier — the right-typed variant may land.

## The case-insensitive binder

ASP.NET (`Role`/`role`/`ROLE`), some PHP, MySQL columns — case-
insensitive binding. A filtered `role` may be a serializer quirk —
`Role`/`ROLE`/`User.Role` worth one probe on .NET stacks.

## The PUT wipe

`PUT` replaces: `{"role":"admin"}` alone zeroes `username`/`email` —
the account breaks, the probe looks dead. PUT needs the FULL control
body + extras.

## The PATCH-vs-POST allowlist difference

`POST /register` allowlists `[u,p]`; `PATCH /users/me` allowlists
`[name,bio,role]` — wider. The second binder is usually the live one.

## The nested-parent hole

Flat `role` rejected; `{"profile":{"role":..}}` survives — the
allowlist covers `profile` as a unit; the merge reaches the nested
`role`. Every allowed parent (`settings`, `preferences`, `metadata`)
is a tunnel.

## The array-vs-scalar gap

`role:"admin"` scalar filtered; `roles:["admin"]` array binds;
`group` string rejected; `groups:[{id:1}]` FK-array binds. The model's
TYPE selects the shape.

## The dup-key parser gap

`{"role":"user","role":"admin"}` — parsers take last; a validator
reading first and binder taking last = the two-validator gap.
`role=user&role=admin` — first-vs-last parser semantics.

## The FK blind spot

`role` isn't on `users` — it's on `memberships`/`user_roles`/`groups`.
Flat `role` misses; `{"membership":{"role":..}}` or `user[role_ids][]=1`
binds through the nested-association accept.

## The timestamps/discriminator fields

`createdAt`, `updatedAt`, `__v`, `deleted_at`, `_t`, `type` — bindable,
unguarded, sometimes decision-relevant. `_t:"AdminUser"` switches the
sub-schema to the privileged variant.

## The GraphQL args-only surface

`mutation{updateUser(input:{role:ADMIN})}` — the args schema IS the
binder; introspection spells every arg. Extra input-object fields are
mass assignment in the schema.

## The method-override carrier

`POST` + `X-HTTP-Method-Override:PUT` or `?_method=PATCH` — POST's
validation routes through PUT's binder; different allowlists make the
override a carrier.

## The optimistic-concurrency bypass

`version`/`__v`/`lock_version` bound high — the "someone changed it"
check skipped; the update wins unconditionally.

## The cached read-back

`GET` returns `role:"user"` from a stale view — re-GET with `?cb=<rand>`
or a second representation before falsifying.
