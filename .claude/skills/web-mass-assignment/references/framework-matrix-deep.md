# Framework matrix deep — the binder internals per stack

## Express + Mongoose — the three binder shapes

```js
User.create(req.body);                    // schema paths only (strict)
Object.assign(user, req.body);            // EVERYTHING binds
user.set(req.body);                       // strict-respecting
const {role, ...rest} = req.body;         // destructure-stripping
_.pick(req.body, 'username');             // allowlist
```

`strict:true` (default): `role` sets on the instance, echo shows it,
`save()` drops it — the echo-lie. `strict:false` or `Object.assign`/
spread: everything binds. `timestamps` plugin adds `createdAt`/
`updatedAt`; `_t` discriminator selects the sub-schema.

## Express + Sequelize

```js
User.create(req.body);                    // all model attributes bind
User.update(req.body, {where:{id}});      // same on update
User.create(req.body, {fields:[...]});    // the allowlist
```

Binds every declared attribute — `role`, `isAdmin`, `balance` land if
they're columns. `paranoid` adds `deletedAt`; `defaultScope` hides
fields from queries while storing them.

## Flask + SQLAlchemy

```python
user = User(**request.get_json())         # TypeError on unknown keys
for k,v in request.json.items(): setattr(user,k,v)   # binds all
user.__dict__.update(request.json)        # direct dict merge — all
db.session.merge(user)                    # merge semantics
```

`**json` raises `TypeError: unexpected keyword 'role'` — the signature
IS the allowlist, the error leaks it. `setattr`/`__dict__.update` bind
silently. `request.values` = query+form union.

## Django

```python
form = UserForm(request.POST)             # Meta.fields = allowlist
User.objects.create(**request.data)       # kwargs — all model fields
request.user.__dict__.update(data)        # dict merge — all
user = User(**serializer.validated_data)  # serializer allowlist
```

HTML forms use `Meta.fields`; `/api/*` merges kwargs. `is_staff`,
`is_superuser`, `groups`, `user_permissions` — the privilege fields;
M2M takes `[{id:1}]` or `[1]` arrays.

## Rails

```ruby
User.create(params[:user])                          # unfiltered
User.create(params.require(:user).permit(:u,:p))    # allowlist
user.update(params.require(:user).permit(:name,:bio,:role))
                                                     # role in the set
accepts_nested_attributes_for :profile               # user[profile_
                                                     # attributes][..]
```

`permit` is the allowlist — but the DECLARED set may include `role`.
`user[...]` is the access convention; `user[profile_attributes][role]`
the nested tunnel.

## Laravel

```php
User::create($request->all());            // $fillable/$guarded decides
$user->fill($request->all());
$user->update($request->only('name','bio'));
```

`$fillable` = allowlist; `$guarded=[]` = unguarded; `$guarded=['id']` =
everything else fills. `is_admin`, `role`, `email_verified_at` are the
fields.

## Spring

```java
public User create(@RequestBody User user)      // bean binding: every
                                                 // settable property
public User update(@ModelAttribute User u)
```

Jackson + bean binding: `isAdmin`, `role`, `balance` bind if setters
exist. `@JsonIgnore`/DTO allowlists fix it — often absent. `BindingResult`
validates TYPES, not field admission.

## ASP.NET

```csharp
public IActionResult Register([FromBody] User user)
// [Bind(Include="Username,Password")] — the allowlist; absent → all
//   public setters bind (IsAdmin conventions)
```

"Over-posting" is this stack's name. Case-insensitive on property names
— `Role`/`role`/`ROLE`/`User.Role` all reach `Role`.

## Go

```go
var u User
json.NewDecoder(r.Body).Decode(&u)        // exported JSON-tagged fields
c.ShouldBindJSON(&u)                      // gin — tagged fields
var m map[string]interface{}              // unmarshal — passes anything
```

`json:"role"` tags bind; `interface{}`/map bodies pass anything
downstream. `form:"role"` tags for form binding.

## The per-stack quick grammar

| Stack | Flat | Nested | Array | Prefixed | Typed |
|---|---|---|---|---|---|
| Express/Mongoose | `role` | `{"user":{"role":..}}` | `["admin"]` | — | strict-drop vs bind |
| Express/Sequelize | `role` | — | `["admin"]` | — | all columns |
| Flask | `role` | — | — | — | `TypeError` leaks |
| Django | `is_staff` | — | `groups:[1]` | — | M2M shapes |
| Rails | `role` | `user[role]` | `user[role][]` | `user[..]` | `permit` |
| Laravel | `is_admin` | — | `role[]` | — | `$fillable` |
| Spring | `role`/`isAdmin` | `{"a":{"b":..}}` | — | — | bean setters |
| ASP.NET | `Role`/`role` | `User.Role` | — | `user.role` | case-insensitive |
| Go | `role` (tagged) | struct tags | `[]` | — | tags only |
