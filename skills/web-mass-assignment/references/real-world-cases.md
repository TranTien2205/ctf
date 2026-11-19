# Real-world cases — mass-assignment incidents and their shapes

## The GitHub Rails case (2012)

The canonical mass-assignment incident — a Rails app where `User.attr_
accessible` didn't include `public_key`, but the model bound
`user[public_key]` on the update form. A forged `user[public_key]`
param wrote an attacker's SSH key into another user's account — full
repo push access as anyone. The fix was GitHub's response within hours;
the class name entered the security lexicon.

**The mechanism**: Rails' `accepts_nested_attributes_for` / unfiltered
`params[:user]` binding — the update form's nested params reached the
SSH-key field.

**The lesson**: the update binder is the live surface; nested params
are the Rails carrier; the bound field (a credential) IS the exploit.

## The over-posting family (.NET / ASP.NET)

ASP.NET's model binding accepts any POST field matching a model
property — `[Bind(Include)]` is the allowlist, often absent. `IsAdmin`
convention fields bound on register/update forms; the "over-posting"
name comes from this stack. The fix is `[Bind]` or a DTO; the bug is
the absent include-list.

**The lesson**: `.NET` binders are case-insensitive on property names —
`Role`/`role`/`ROLE`/`User.Role` all reach `Role`.

## The ORM `**kwargs` family (Django/Flask)

`User.objects.create(**request.data)` or `User(**request.json)` —
Python kwargs binding where the signature IS the schema. `TypeError`
on unknown keys names the model's fields; `is_staff`, `is_superuser`
bind when the signature includes them. `setattr`/`__dict__.update`
loops bind silently.

**The lesson**: the kwargs signature is a soft allowlist — `TypeError`
leaks the schema; the `setattr` loop is the silent bug.

## The deep-merge family (JavaScript)

`_.merge(user, req.body)` / `Object.assign` / `{...}` spread — the
recursive merge reaching `profile.role`, `settings.admin`, `metadata.
flags` the flat allowlist can't see. Lodash's `_.merge` additionally
walks `__proto__` — the prototype-pollution overlap.

**The lesson**: deep-merge handlers are the nested-tunnel sites;
`profile`/`settings`/`metadata` parents are the tunnels.

## The discriminator family (Mongoose)

`_t`/`__t`/`type` fields selecting the sub-schema — `{"_t":"AdminUser"}`
switches the binder to the privileged schema, exposing fields the base
schema lacks. The discriminator is mass-assignment INTO a different
schema.

**The lesson**: `_t`/`type`/`user_type` are the schema-switch fields;
binding one changes the writable surface entirely.

## The bulk-import family

`/import`, `/seed`, `/bulk`, `/migrate` — operator endpoints binding
arrays of objects, often unguarded because "only admins call them."
The bulk binder accepts fields the per-object forms strip.

**The lesson**: bulk binders are the least-tested surface; `/admin/*`
binders need a privilege edge but are widest.
