# Framework matrix — every stack's binder and its mass-assignment posture

## Express + Mongoose

```js
User.create(req.body);                  // binds schema paths; strict
                                      // drops unknown keys by default
Object.assign(user, req.body);          // merges EVERYTHING — the bug
user.set(req.body);                     // strict-respecting
```

- `strict:true` (default): unknown keys set on instance but dropped at
  save — echo shows `role`, store never gets it → read-back falsifier.
- `strict:false` / `Object.assign` / `{...req.body}`: everything binds.
- The `timestamps` plugin adds `createdAt`/`updatedAt` — bindable fields
  nobody checks.
- Discriminator key `_t` — changes the sub-schema; may bind a privileged
  type.

## Express + Sequelize

```js
User.create(req.body);                  // binds all model attributes
User.update(req.body, {where: {id}});   // same on update
```

- Binds every declared attribute — `role`, `isAdmin`, `balance` all
  land if they're columns. `fields` option is the allowlist; absent
  = the bug. Update and create binders identical here.
- `paranoid` models add `deletedAt`; `defaultScope` may hide fields
  from serializers while storing them.

## Flask + SQLAlchemy

```python
user = User(**request.get_json())       # kwargs merge — TypeError on
                                        # unknown keys (soft allowlist)
for k, v in request.json.items():
    setattr(user, k, v)                 # explicit merge — binds all
```

- `**json` raises `TypeError: unexpected keyword 'role'` — names the
  rejected field; a falsifier that leaks the schema.
- `setattr` loops bind silently — `role`, `is_admin`, `balance`.
- `request.form`/`request.args` merged via `request.values` — the
  query+form union reaching the binder.

## Django

```python
form = UserForm(request.POST)           # Meta.fields — real allowlist
User.objects.create(**request.data)     # kwargs merge — binds all
request.user.__dict__.update(data)      # direct dict merge — binds all
```

- The HTML form allowlists; `/api/*` paths often merge. Probe BOTH.
- `is_staff`, `is_superuser`, `groups`, `user_permissions` are the
  privilege fields; `groups`/`user_permissions` are M2M — array or
  `[{id:1}]` shapes.

## Rails

```ruby
User.create(params[:user])                          # unfiltered — BUG
User.create(params.require(:user).permit(:u,:p))    # allowlist
```

- `permit` is THE falsifier — `grep -rn "permit" app/controllers`.
- `params[:user]` without `permit` binds every key; `user[role]=admin`
  is the canonical carrier (nested params are native).
- `attr_accessible` (old Rails 3) is the model-level allowlist.

## Laravel

```php
User::create($request->all());            // every column unless
$user->fill($request->all());             //   $fillable/$guarded set
```

- `$fillable` = allowlist; `$guarded=[]` = unguarded; `$guarded=['id']`
  = everything else fills. `grep -rn "fillable|guarded" app/Models`.
- `is_admin`, `role`, `email_verified_at` — the date field `verified`
  variants bind too.

## Spring

```java
public User create(@RequestBody User user)   // bean binding: every
                                            //   settable property binds
public User update(@ModelAttribute User u)   //   same on form posts
```

- Jackson + bean binding: `isAdmin`, `role`, `balance` bind if setters
  exist. `@JsonIgnore`/DTO allowlists are the fix — often absent.
- `BindingResult`/validation annotations check TYPES, not field
  admission.

## ASP.NET

```csharp
public IActionResult Register([FromBody] User user)
// [Bind(Include="Username,Password")] — the allowlist; absent → all
//   public setters bind, including IsAdmin conventions
```

- "Over-posting" is this stack's name for the class.
- `User.Role`, `user.role`, `role` case variants — the binder is
  case-insensitive on property names.

## Go

```go
var u User
json.NewDecoder(r.Body).Decode(&u)   // exported, JSON-tagged fields
```

- `json:"role"` tagged fields bind; untagged/`interface{}` params
  reopen everything — `map[string]interface{}` bodies pass anything
  downstream.
- `form:"role"` tags on form binding.

## The carrier grammar per stack

| Stack | Flat | Nested | Array | Prefixed |
|---|---|---|---|---|
| Express | `role` | `{"user":{"role":..}}` | `role[]`, `["admin"]` | — |
| Flask/Django | `role` | — | `[..]` | — |
| Rails | `role` | `user[role]` | `user[role][]` | `user[...]` |
| Laravel | `role` | — | `role[]` | — |
| Spring | `role`/`isAdmin` | `{"user":{"role":..}}` | — | — |
| ASP.NET | `Role`/`role` | `User.Role` | — | `user.role` |
| Go | `role` (tagged) | nested struct tags | `[]` | — |
