# Mass assignment deep — the binder internals per framework

`mass-assignment.md` covers the probe. This module is the binder
internals — what `create`/`update`/`bind` does with extra keys per
stack, and the exact probe grammar each exposes.

## Express + Mongoose

```js
// schema strict:true (default) — unknown fields DROPPED at set
const u = await User.create({...req.body, role: 'user'});
// schema strict:false — everything persists
// or the dangerous spread into a known-good object:
Object.assign(user, req.body);          // every key binds
```

- `strict` default drops extras → `role: user` read-back (falsifier).
- `Object.assign`/spread merges EVERYTHING → the bug.
- `__proto__` in `req.body` under some merge libs → prototype-level
  write (see `web-prototype-pollution` for that rabbit hole).
- `save()` after `set()` — `user.set(req.body)` respects strict too.

## Express + Sequelize

```js
User.create(req.body);                  // binds all attributes by default
User.update(req.body, {where:{id}});    // same on update
```

Sequelize binds whatever attributes exist in the model — extras ignored
but ALL model fields bindable, including `role`, `isAdmin`. The
`fields` option is the allowlist; its absence is the bug.

## Flask + SQLAlchemy

```python
user = User(**request.get_json())       # kwargs merge — every key
# or
for k, v in request.json.items():
    setattr(user, k, v)                 # explicit merge — same bug
```

`**request.json` raises `TypeError` on unknown keys (a soft allowlist —
the error NAMES the rejected field: `"unexpected keyword 'role'"` is a
falsifier with the schema attached). `setattr` loops bind silently —
including `role`, `is_admin`, `balance`.

## Django

```python
# ModelForm — Meta.fields IS the allowlist
form = UserForm(request.POST)           # only declared fields
# but the API path often bypasses forms:
User.objects.create(**request.data)     # kwargs merge
request.user.__dict__.update(request.data)   # direct merge — BUG
```

The safe path (ModelForm) and the merge path (`create(**data)`) often
coexist — the HTML form allowlists while the `/api/register` endpoint
merges. Probe both paths.

## Rails

```ruby
User.create(params[:user])                          # unfiltered — BUG
User.create(params.require(:user).permit(:u,:p))    # allowlisted
```

`permit` is the falsifier in code. `params[:user]` without `permit`
binds every key — and `user[role]=admin`/`user[role][]=admin` nested
params reach the model naturally. Mass assignment is Rails' original
named bug — the audit is `grep -rn "permit" app/controllers`.

## Laravel

```php
User::create($request->all());            // every column unless
                                          // $fillable/$guarded set
$user->fill($request->all());
```

`$fillable` = allowlist; `$guarded = []` = explicitly unguarded;
`$guarded = ['id']` = everything else fills. The audit:
`grep -rn "fillable\|guarded" app/Models`.

## Spring

```java
@PostMapping("/register")
public User create(@RequestBody User user) {...}
// or @ModelAttribute — binder binds every settable property
```

Jackson deserialization + bean binding: every property with a setter
binds — `isAdmin` if the property exists. `JsonIgnoreProperties` and
`@JsonIgnore` on setters are the allowlist equivalents.

## ASP.NET

```csharp
public IActionResult Register([FromBody] User user) {...}
// [Bind(Include="Username,Password")] is the allowlist
```

Model binding populates every public setter — `IsAdmin` properties are
the classic victim. Over-posting is this stack's name for the bug.

## Go

```go
var u User
json.NewDecoder(r.Body).Decode(&u)      // only JSON-tagged fields bind
```

`json.Unmarshal` binds exported tagged fields only — the struct's tags
ARE the schema; `interface{}` params reopen everything.

## The probe grammar per binding style

| Binder | Flat | Nested | Array | Dotted |
|---|---|---|---|---|
| merge-all JS | `role` | `{"user":{"role":..}}` | `role[]` | — |
| kwargs py | `role` | — | — | — |
| Rails params | `role` | `user[role]` | `user[role][]` | — |
| Laravel fill | `role` | — | `role[]` | — |
| Jackson | `role` | `{"role":..}` | — | — |

Match the grammar to the stack — the fingerprint is in the stack trace,
`X-Powered-By`, error shapes, or the handout's source.
