# Mechanism deep — the merge internals per binder family

## The merge-all pattern

```js
// Express + Mongoose / Sequelize
Object.assign(user, req.body);          // every key copied
user.set(req.body);                     // strict-respecting
User.create(req.body);                  // schema paths only (strict)
{...user, ...req.body}                  // shallow — nested replaced wholesale
```

`Object.assign` and spread merge EVERYTHING including nested objects —
`{"profile":{"role":..}}` replaces `user.profile` wholesale (shallow)
or merges recursively depending on whether the handler uses a deep-
merge helper (`_.merge`, `deepmerge`). `_.merge` is the dangerous one —
recursive, and it walks `__proto__` unless sanitized (the pollution
overlap).

## The kwargs-merge pattern

```python
# Flask / Django
user = User(**request.get_json())       # kwargs signature = schema
for k, v in request.json.items():
    setattr(user, k, v)                 # explicit — binds all
User.objects.create(**data)             # binds model kwargs
user.__dict__.update(data)              # direct dict merge — binds all
```

`**json` raises `TypeError: unexpected keyword 'role'` — the kwargs
signature IS the allowlist, and the error NAMES the rejected key. The
`setattr`/`__dict__.update` loops bind silently — no signature check.

## The allowlist pattern

```ruby
# Rails
User.create(params.require(:user).permit(:username, :password))
# vs
User.create(params[:user])              # unfiltered — everything binds
```

```php
// Laravel
User::create($request->all());          // $fillable/$guarded decides
$user->fill($request->all());
```

```csharp
// ASP.NET
[Bind(Include="Username,Password")]     // the allowlist
public IActionResult Register([FromBody] User user)   // absent → all
```

```js
// Express pick
User.create(_.pick(req.body, 'username', 'password'))
```

`permit`, `$fillable`, `[Bind]`, `pick`, `fields=` — same mechanism,
different stacks. The flat extras die; nested under an allowed parent
may survive.

## The strict-schema pattern

```python
# pydantic / marshmallow
class UserIn(BaseModel):
    username: str; password: str
    model_config = {"extra": "forbid"}   # 422 on unknown keys
```

```js
// Joi / zod
schema.validate(req.body)               // unknown → 400
zod.object({...}).strict().parse(...)
```

`additionalProperties:false`, `extra:forbid`, `.strict()` — the parser
kills extras before the binder. The `400`/`422` is the content-type
falsifier — the form path uses a different parser.

## The deep-merge pattern

```js
_.merge(user, req.body);               // recursive — nested survives
deepmerge(user, req.body);
user.profile = {...user.profile, ...req.body.profile};
```

PATCH handlers: `{"profile":{"role":..}}` merges into the existing
`profile` object — the flat allowlist covers `profile` as a unit while
the merge reaches the nested `role`. The merge DEPTH (1 level, 2,
recursive) decides how deep the tunnel reaches.

## The replace pattern (PUT)

```js
Object.keys(req.body).forEach(k => user[k] = req.body[k]);
// or
User.replaceOne({_id}, req.body);       // wholesale replace
```

PUT REPLACES — extras bind if the model accepts them; omissions reset
to defaults. The wipe is the footgun: `{role:admin}` alone on PUT
zeroes `username`/`password`.

## The nested-association pattern

```ruby
accepts_nested_attributes_for :profile   # user[profile_attributes]
                                         #   [role]=admin binds deep
```

```php
$user->profile()->update($request->profile);
```

The nested-association binder reaches the CHILD model's fields through
the parent's accepted key — `user[profile_attributes][role]` or
`{"profile":{"role":..}}`. The allowlist on the parent passes `profile`
wholesale to the child's (maybe absent) allowlist.

## The discriminator/polymorphic pattern

```js
// Mongoose discriminator
{_t: "AdminUser"}        // changes the sub-schema
{type: "admin"}          // some apps key the schema on it
```

`_t`, `__t`, `type`, `user_type` — the discriminator field selects
which schema the binder applies; binding it switches to the privileged
variant.

## The coercion pattern

Type coercion runs after binding: `"admin"`→String, `1`→Integer,
`true`→Boolean, `["admin"]`→Array. A strict-typed column rejects the
wrong JSON type while accepting the right one — `role:true` `400`s,
`role:"admin"` binds. The type is the second allowlist.
