# Per-mechanism deep — each binder mechanism's internals and exploit

## A — merge-all (`Object.assign`, `setattr` loop, `create(req.body)`)

```js
Object.assign(user, req.body);        // every key copied
user.set(req.body);
{...user, ...req.body}                // shallow — nested replaces
```

The bug is ABSENCE — no allowlist anywhere. Flat extras land. The
detection: any extra key stores. The falsifier: none at the binder —
the model/check-set decides. The exploit: flat `role`/`is_admin`/
`balance`/`verified`.

## B — kwargs signature (`User(**json)`, `Model.new(**params)`)

```python
user = User(**request.get_json())     # TypeError on unknown keys
```

The signature IS the schema — `TypeError: unexpected keyword 'role'`
names the rejected field. The exploit: the signature includes the
dangerous field (`User(username, password, role)` accepts `role`) OR
the kwargs are filtered first. `TypeError` leaks the schema — the
signature's params are the writable set.

## C — allowlist (`permit`, `$fillable`, `[Bind]`, `pick`, `fields=`)

```ruby
params.require(:user).permit(:username, :password)
```

Declared keys only — flat extras drop (`200` silent). The exploit:
the DECLARED set includes the dangerous field (`permit(:name,:bio,
:role)`) OR a nested tunnel (`{"profile":{"role":..}}` where `profile`
is in the set) OR a second binder (`PATCH` allows what `POST` doesn't).

## D — strict schema (`additionalProperties:false`, `extra:forbid`)

```js
schema.validate(req.body);            // 400 on unknown
zod.object({...}).strict().parse(...);
```

The parser kills extras — `400`/`422`. The exploit: the form path
(different parser, no schema), the update endpoint (different schema),
nested object contents (schema validates `profile` as `object`, not
its keys), content-type confusion.

## E — deep merge (`_.merge`, `deepmerge`, recursive assign)

```js
_.merge(user, req.body);              // recursive — nested survives
deepmerge(user.profile, req.body.profile);
```

`{"profile":{"role":..}}` reaches `profile.role` the flat allowlist
can't drop. `_.merge` walks `__proto__` — the pollution overlap. The
exploit: depth-1 and depth-2 nested objects.

## F — nested association (`accepts_nested_attributes_for`)

```ruby
accepts_nested_attributes_for :profile
# user[profile_attributes][role]=admin binds the child's field
```

The child's writable fields reachable through the parent's accepted key.
`role` readonly on `User` but writable on `Membership`/`Profile` —
`{"membership":{"role":..}}` reaches it.

## G — discriminator (`_t`, `__t`, `type`, `user_type`)

```js
{_t:"AdminUser"}      // switches the schema to the privileged variant
```

The bound field selects WHICH schema applies — `AdminUser` carries
fields `User` lacks. The exploit: bind the discriminator, then bind
the privileged variant's fields.

## H — type coercion (post-binding)

```js
role: "admin"  → String column    // binds
role: true     → bool column      // binds
role: 1        → enum/int column  // binds
role: "admin"  → enum ["user"]    // rejects — wrong enum value
groups: "admin" → array column    // 500 — wrong type
groups: [{id:1}] → FK array       // binds
```

The model's TYPE is a second filter — the right-typed variant reaches
what the wrong-type misses.

## I — method permutation (`POST`/`PATCH`/`PUT`/`?_method=`)

Different binders per method — `PATCH` merge (wide), `PUT` replace
(binds or wipes), `POST` create (tight). `?_method=PUT` routes POST's
validation through PUT's handler — the override carrier.

## J — serializer-hidden (`toJSON`, `fields=`, `as_json`)

The field stores, the response hides it — `GET` returns `{"username",
"id"}` while `role` sits in the DB. Read-back blind; exercise the
decision directly — `200` on the gated route proves storage.
