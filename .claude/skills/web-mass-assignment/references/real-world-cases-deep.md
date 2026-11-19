# Real-world cases deep — the mass-assignment incident history

## GitHub 2012 — the incident that named the class

A Rails app where `User` had a `public_key` field for SSH access.
`attr_accessible` (Rails 3's allowlist) didn't include it, but the
update form bound `params[:user]` including `user[public_key]`. An
attacker sent `user[public_key]=<their-key>` to another user's profile
update — the bound SSH key wrote into the victim's account → full repo
push access as anyone (the Rails repo itself was the demo target).

**The mechanism**: `User.update(params[:user])` — the nested-params
convention (`user[public_key]`) reaching the SSH-key field through an
unfiltered `params[:user]` binding.

**The lesson**: the UPDATE binder is the live surface; nested params
are the Rails carrier; the bound field (a credential) IS the exploit
without needing a gate.

## The `attr_protected` / `attr_accessible` era (Rails 3)

`attr_accessible` = allowlist; `attr_protected` = denylist. `attr_
protected :role` blocked `role` while allowing everything else — the
denylist's gap (forgetting a dangerous field) is the same bug. Rails 4
replaced it with strong params (`permit`) — moving the allowlist to
the controller per-action, which made SHARED allowlists the new risk.

## The over-posting family (ASP.NET)

ASP.NET model binding accepts any POST field matching a model property
— `[Bind(Include="Username,Password")]` is the allowlist, often absent.
`IsAdmin` convention fields bound on register/update forms. The
"over-posting" name is this stack's term — same class.

**The lesson**: `.NET` binders are case-insensitive on property names —
`Role`/`role`/`ROLE`/`User.Role` all reach `Role`; a filter checking
`role` misses `Role`.

## The ORM `**kwargs` family (Django/Flask/Python)

`User.objects.create(**request.data)` — kwargs binding where the
signature is the schema. `TypeError: unexpected keyword 'role'` names
the model's fields; `is_staff`, `is_superuser`, `groups`,
`user_permissions` bind when the signature includes them.
`setattr`/`__dict__.update`/`merge` loops bind silently — no signature
check at all.

## The deep-merge family (JavaScript)

`_.merge(user, req.body)` — Lodash's recursive merge reaching
`profile.role`, `settings.admin`, `metadata.flags` the flat allowlist
can't see. `_.merge` walks `__proto__` — `{"__proto__":{"polluted":
true}}` is the prototype-pollution overlap; `{"profile":{"role":..}}`
is the mass-assignment reach. Same mechanism, different reach.

## The discriminator family (Mongoose)

`_t`/`__t`/`type`/`user_type` fields selecting the sub-schema —
`{"_t":"AdminUser"}` switches to the privileged discriminator. The
discriminator is mass assignment INTO a different schema — a bound
field that changes WHICH fields exist.

## The bulk-import family

`/import`, `/seed`, `/bulk`, `/migrate` — operator endpoints binding
arrays of objects, "admin-only" in name but often unauthenticated or
reachable through the public API. The bulk binder's allowlist is
absent where the per-object form's exists — the least-tested surface.

## The GraphQL family

`mutation{ updateUser(input:{role:ADMIN}) }` — the input-object type
carries fields the form's mutation never sends. Introspection dumps
the args; the schema IS the writable surface. Mass assignment written
in the API schema itself.
