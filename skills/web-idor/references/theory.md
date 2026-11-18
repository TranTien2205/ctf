# Theory — why the check fails

The mechanism-level explanation of each IDOR shape.

---

## 1. The fetch-then-return

```python
obj = Model.get(id)   # fetches ANY object — no scope
return obj
```

The database's `get(id)` is *global* — it takes the primary key and
returns the row. Ownership is a *second* step the developer must add
(`Model.get(id).where(user_id=...)` or `if obj.user_id != session.user`).
When the second step is absent, the fetch is unbounded.

**Why it happens**: the ORM's ergonomics — `Model.get(id)` reads like
the natural lookup, and "objects belong to users" is a *business rule*
the developer must wire in, not a default the framework enforces.

## 2. The check-after-fetch

```python
obj = Model.get(id)
if obj.user_id != session.user_id:
    return 403
return obj
```

The check compares the object's `user_id` to the session — the *safe*
shape. The bug variants:

- The check is conditional on `obj.public` — a public flag you can flip.
- The `obj.user_id` is a *string* the object claims (settable at create).
- The `session.user_id` is forgeable (weak JWT, mass-assign on `/me`).

## 3. The scoped query

```sql
SELECT * FROM objects WHERE id=? AND owner_id=?
```

The `AND owner_id` is the boundary — its absence is the IDOR. The
query is scoped *if* the developer wrote the `AND`; the ORM doesn't
add it for you.

## 4. The ORM-scope confusion

```python
Order.find(id)                       # global
current_user.orders.find(id)         # scoped via the relation
```

`Order.find(id)` reaches any row; `current_user.orders.find(id)` only
reaches the relation. The bug is the developer reaching for the global
`Order` class instead of the user's `orders` relation.

## 5. The mount-order boundary

```python
app.use('/api', authz)          # middleware on /api/*
app.get('/api/users')           # guarded
app.get('/admin/users')         # NOT under /api — unguarded
```

`app.use('/api', ...)` installs the middleware on the `/api` mount —
a route registered outside the prefix never runs it. The bug is the
prefix-scoping confusion.

## 6. The middleware-order boundary

```python
app.get('/admin/users')         # defined BEFORE app.use(admin)
app.use('/admin', adminAuthz)   # mounted after — doesn't reach the route
```

Express/Flask-Blueprint middleware applies to routes registered *after*
it — a route defined before `app.use` is unguarded.

## 7. The decorator-skip

```python
@requires_owner
def get_object(id): ...

@route('/api/objects/<id>')
def api_object(id):
    return get_object(id)     # does the decorator run?
```

The decorator wraps `get_object` — but `api_object` calls it as a plain
function. The decorator's check is on `get_object`, not on every caller.

## 8. The check-on-the-param bug

```python
if request.args.get('user_id') == str(session.user_id):
    return obj          # checks ?user_id=, not obj.user_id
```

The check compares the *request's* `user_id` to the session — not the
*object's*. `?user_id=me` passes while `?id=victim` reads victim's object.
The developer confused "the request's claimed user" with "the object's
bound user".

## 9. The both-are-params bug

```python
if request.args.get('owner') == request.args.get('user'):
    return obj          # checks owner==user, both are params
```

Both sides are request params — the check is trivially satisfied.

## 10. The claimed-owner bug

```python
if obj.owner == session.user.name:    # obj.owner is a STRING you set
    return obj
```

`obj.owner` is a free-form string set at create — the check compares a
claim, not a bound id. Set `owner` to your own name (or `admin`) and
pass.

## 11. The "the bound field is changeable" bug

```python
obj = Model.get(id)
if obj.user_id == session.user_id:
    return obj
```

`PATCH /objects/42 {"user_id":<your_id>}` — reassign the owner, then
read. The write-IDOR enables the read.

## 12. The GraphQL-resolver bug

```
type Query {
    me: User               — resolves to session.user (safe)
    user(id: ID): User     — resolves ANY id (the bug)
    node(id: ID): Node     — the Relay node access (the bug)
}
```

The `user(id:)`/`node(id:)` resolver takes the id argument and returns
the object — the resolver is a free lookup unless it checks the session.
The `me` resolver is safe by design (it returns session.user).

## 13. The scope-override bug

```python
def list_orders(request):
    user_id = request.args.get('user_id', session.user_id)
    return Order.filter(user_id=user_id)
```

`request.args.get('user_id', session.user_id)` — the param defaults to
the session but overrides it when present. The developer intended
"show your own orders by default, filterable by user_id" — but the
filter is unbounded.

## 14. The scope-flag bug

```python
scope = request.args.get('scope', 'own')
if scope == 'all':
    return Order.all()      # drops the WHERE
```

The `?scope=all` flag is a deliberate "show all" feature — the bug is
that it reaches a normal user.

## 15. The field-list bug

```python
fields = request.args.get('fields', 'id,name').split(',')
return {f: getattr(obj, f) for f in fields}   # reads ANY field
```

`?fields=`/`?include=`/`?select=` reads the named fields — `role`,
`secret`, `password_hash` — off the object. The field-list is the leak.

## 16. The mass-assign bug

```python
for k, v in request.json.items():
    setattr(obj, k, v)       # binds every field, including role/user_id
```

The update binds every body field — `role`, `is_admin`, `user_id` —
onto the model. The bug is the unfiltered bind.

## 17. The function-level bug

```python
@app.route('/admin/flag')
def admin_flag():
    return flag             # the route exists; no check
```

The route is registered but no authz decorator/middleware guards it —
the "hidden" admin function is reachable by anyone.

## 18. The normalization bug

```
location /admin { deny all; }         — the nginx rule
GET //admin/flag                     — the app normalizes // → /
GET /admin/../admin/flag             — the app resolves ../
GET /admin%2fflag                    — the app decodes %2f
GET /admin/flag/                     — the app strips the trailing /
```

The nginx `location /admin` matches the literal prefix; the app
normalizes the variants before routing — the variant reaches the route
past the rule. See `web-parser-differential`.

## 19. The second-hop bug

```
POST /export {"user_id":1}     — the first hop accepts your id
  → the job reads user 1's data with a service account
```

The first hop is *your* request (checked); the second hop is the
*backend's* (service account). The IDOR is the first hop accepting the
id and passing it to a privileged worker.

## 20. The carrier bug

```
GET /users/42              → the check is on the path id
POST /users {"id":42}      → the check is on the path id, not the body's
GET /users/42 X-User-Id: 1 → the check is on the path id, not the header's
```

The check is bound to *where* the id appears — a different carrier
(body, header, cookie, WS message, multipart field) bypasses it.

## 21. The type-coerce bug

```python
if str(id) == str(session.user_id):   # str() on both sides
    ...
```

`id` is `[1]`/`{"$ne":0}`/`"1"` — a non-scalar the `str()`/`==` mishandles,
or a NoSQL operator the query interprets.

## 22. The "the id is the flag" shape

The object the id names *is* the flag — `GET /flag`/`GET /admin/flag`/
`GET /objects/flag`/`?id=flag`. The class is "the route accepts the
flag-shaped id".

## 23. The "the check is a JOIN" bug

```sql
SELECT * FROM objects WHERE id=? AND owner_id IN
  (SELECT id FROM users WHERE session_token=?)
```

The join resolves the session token — a forged/stale/predictable token
joins to another's ownership. The boundary is the token lookup's
integrity.
