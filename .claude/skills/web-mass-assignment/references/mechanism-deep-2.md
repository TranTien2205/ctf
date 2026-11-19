# Mechanism deep 2 — the merge internals, continued

## The `Object.assign` / spread merge

```js
Object.assign(user, req.body);
// shallow: {"profile":{"role":..}} REPLACES user.profile wholesale
//   if profile was {theme:"dark", role:"user"}, after merge it's
//   {role:"admin"} — the theme is gone, role is bound

{...user, ...req.body}
// same shallow semantics — top-level keys replaced entirely

_.merge(user, req.body);
// DEEP: {"profile":{"role":..}} merges INTO existing profile —
//   {theme:"dark", role:"admin"} — theme preserved, role bound

deepmerge(user, req.body);
// same deep semantics — the recursive tunnel
```

Shallow vs deep decides whether `{"profile":{"role":..}}` REPLACES
`profile` (bound but wiping siblings) or MERGES (bound preserving
siblings). Both bind `profile.role`; the deep merge preserves the
other profile fields.

## The `create`/`update`/`save` binding

```js
User.create(req.body);          // schema paths bind at create
User.update(req.body, {where}); // schema paths bind at update
user.save();                    // persists bound attributes
```

`create` vs `update` may use different allowlists — `create` binds the
form's declared fields; `update` binds the editable set (wider). The
`timestamps` plugin adds `createdAt`/`updatedAt` — bindable.

## The `strict`/`strictQuery` Mongoose split

```js
// strict:true (default) — unknown keys dropped at save
// strict:false — unknown keys persist
// strictQuery — separate control for query filters
```

`role` set on the instance shows in `user.role` (the echo) but drops
at `save()` under `strict:true`. The echo-lie: `{"role":"admin"}` in
the POST response, `{"role":"user"}` in the store.

## The Python `**kwargs` internals

```python
User(**request.get_json())
# → User(username=..., password=..., role="admin")
# the __init__ signature: User(username, password, email)
# → TypeError: unexpected keyword 'role'

# OR the signature includes it:
User(username, password, role=None, balance=0)
# → role="admin" binds silently — the signature IS the allowlist
```

The `TypeError` is a schema leak — enumerate the signature by probing
candidate fields; the error names whether each is in the signature.

## The `setattr`/`__dict__.update` loops

```python
for k, v in request.json.items():
    setattr(user, k, v)           # binds every key

user.__dict__.update(request.json) # binds every key to the instance dict
```

No signature check — `role`, `is_admin`, `balance` bind if they're
attributes. `__dict__.update` bypasses properties/descriptors too.

## The `permit`/`require` internals (Rails)

```ruby
params.require(:user).permit(:name, :bio)
# require — the :user key must exist
# permit  — only :name, :bio allowed through

params[:user]                     # unfiltered — all keys pass
params.require(:user).permit(:name, :bio, :role)
#                                  ↑ role IN the set — the bug
```

`permit` is the allowlist — but the DECLARED set may include `role`
(an admin form's list reused on the public endpoint).

## The `$fillable`/`$guarded` internals (Laravel)

```php
protected $fillable = ['name', 'bio'];        // allowlist
protected $guarded  = ['id'];                 // denylist — everything else
protected $guarded  = [];                     // unguarded — everything
```

`User::create($request->all())` — the `$fillable` decides; `$guarded=[]`
means EVERYTHING fills. `email_verified_at`, `is_admin`, `role` all
bind if not guarded.

## The `[Bind]` internals (ASP.NET)

```csharp
public IActionResult Update([Bind(Include="Name,Bio")] User user)
// Include — the allowlist; absent → ALL public setters bind
//   including IsAdmin conventions
// Exclude — the denylist — everything except named
```

Case-insensitive on property names — `Role`/`role`/`ROLE`/`User.Role`
all reach `Role`.
