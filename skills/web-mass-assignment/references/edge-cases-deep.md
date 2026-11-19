# Edge cases deep — the hard-to-classify mass-assignment states

## The serializer-hidden stored field

The field lands in the store; no response returns it. `GET /api/me`
shows `{"username","id"}` while `role:"admin"` sits in the DB. The
read-back is blind — the only evidence is the DECISION:

```bash
# stored-but-hidden: exercise directly
curl -b "$JAR" "$BASE/admin"      # 200 = the field is real
```

Detection: the write echoed the field (parse reached it), the read-back
doesn't, the decision says yes — serializer-hidden confirmed.

## The echo-lie

Mongoose `strict:true` + `user.set(req.body)`: `role` sets on the
instance, appears in the response, drops at `save()`. The echo shows
`admin`, the store holds `user`. The divergence IS the signal — always
read-back; the echo is the parser's promise, the store is the truth.

## The dual-type column

`role` accepts `String` AND the enum `["user","admin"]` — `role:"admin"`
binds, `role:1` `400`s, `role:true` `400`s. The typed failure is not
the field's falsifier — the right-typed variant may land. One type-
retry per semantic.

## The case-insensitive binder

ASP.NET (`Role`/`role`/`ROLE` equivalent), some PHP (`$user->Role`),
MySQL columns (case-insensitive at the storage layer). A filtered
`role` may be a serializer quirk — `Role`/`ROLE`/`User.Role` are worth
one probe on .NET stacks.

## The array-vs-scalar gap

`role` scalar filtered, `roles:["admin"]` array binds; `group` string
rejected, `groups:[{id:1}]` FK-array binds. The model's TYPE (scalar vs
array, string vs FK object) selects the shape — the scalar/array pair
is one semantic, two probes.

## The discriminator switch

Mongoose `_t`, Rails STI `type`, a `user_type` field — binding it
switches the schema to the privileged variant. `_t:"AdminUser"` is
mass assignment into a different SCHEMA.

## The timestamps/version blind fields

`createdAt`, `updatedAt`, `__v`, `deleted_at` — bindable, unguarded,
sometimes decision-relevant (`__v` for optimistic-concurrency, a bound
`created_at` for age-gates).

## The optimistic-concurrency bypass

`version`/`__v`/`lock_version` bound to a high value — the "someone
else changed it" check is skipped; the update wins unconditionally.
Mass assignment reaching the concurrency field.

## The GraphQL input-object hole

```graphql
mutation{ updateUser(input:{id:9, role:ADMIN, internal:true}) }
```

The `UserInput` type carries fields the form's mutation never sends —
introspection dumps the args; extra input fields are mass assignment
spelled in the schema.

## The foreign-key tunnel

`role` isn't on `users` — it's on `user_roles`/`memberships`. The flat
`role` misses; `{"membership":{"role":"admin"}}` or `user[role_ids][]=1`
binds through the nested-association accept.

## The admin-created-object edge

`POST /admin/users` — the admin binder is wider but needs a privilege
edge FIRST. Chain order: find the role edge (maybe via `/import` or a
second bug), THEN the admin binder's mass-assignment writes the flag
field.

## The method-override carrier

`POST` + `X-HTTP-Method-Override:PUT` or `?_method=PATCH` — POST's
validation routes through PUT's handler; different allowlists on the
two methods make the override a carrier.
