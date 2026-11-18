# White-box hunt — finding the IDOR in source

The grep patterns and code shapes that name the check's position.

---

## 1. The fetch-then-return shape

```python
obj = Model.get(id)         # fetch by id
return obj                  # no owner check → IDOR
```

Grep for `.get(`, `findById(`, `find(`, `findBy(`, `query(`, `fetch(`,
`retrieve(`, `load(`, `read(` followed by a `return` without an owner
check.

## 2. The missing-check grep

```bash
# find fetches that don't check owner
grep -rn '\.get(' --include='*.py' | grep -v 'owner\|user\|auth\|perm'
grep -rn 'findById' --include='*.ts' --include='*.js' | grep -v 'owner\|user\|auth'
grep -rn 'findBy(' --include='*.ts' --include='*.js' | grep -v 'owner\|user\|auth'
grep -rn 'Model\.find' --include='*.ts' --include='*.js' | grep -v 'owner\|user\|auth'
grep -rn 'Order\.get\|User\.get\|Note\.get' --include='*.py' | grep -v 'owner\|user\|auth'
```

## 3. The "the check exists but wrong" shape

```python
obj = Model.get(id)
if request.args.get('user_id') == str(session.user_id):   # checks PARAM not obj
    return obj
```

Grep for `request.args.get`/`request.params`/`params[`/`request.GET`/
`req.query`/`req.params`/`req.body` compared to `session`/`current_user`/
`@login` — the comparison is to the *param*, not the object's owner.

## 4. The "the check is on the param" grep

```bash
grep -rn 'request.args.get' --include='*.py' | grep 'session\|user_id\|current'
grep -rn 'request.params' --include='*.ts' --include='*.js' | grep 'session\|user'
grep -rn 'req.query' --include='*.ts' --include='*.js' | grep 'session\|user'
grep -rn 'req.body' --include='*.ts' --include='*.js' | grep 'session\|user'
grep -rn 'params\[' --include='*.py' --include='*.rb' | grep 'session\|current'
```

## 5. The "the ORM scope missing" shape

```python
Order.find(id)                  # global find — no scope
Order.find_by(id: id)           # global find_by
Order.get(id)                   # global get
Order.query(id=id).first()      # unscoped query
Order.where(id=id)              # unscoped where
db.get(Order, id)               # ORM get
db.query(Order).filter(id=id)   # unscoped filter
session.query(Order).get(id)    # SQLAlchemy get
```

vs the scoped form:

```python
Order.find_by(id: id, user: current_user)
current_user.orders.find(id)
Order.query(id=id, user_id=session.user_id).first()
session.query(Order).filter(id=id, user_id=current_user.id)
```

The global form is the bug.

## 6. The "the middleware order" grep

```python
app.use('/api', authz)          # authz on /api/*
app.get('/api/users')           # guarded
app.get('/admin/users')         # NOT under /api
app.use('/admin', adminAuthz)   # mounted AFTER the route
```

Grep for `app.use(`/`app.get(`/`app.post(` ordering — a route defined
*before* its `use` is unguarded.

## 7. The "the decorator missing" grep

```python
@app.route('/admin/flag')
def admin_flag():               # no @requires_admin
    return flag
```

```bash
grep -rn '@app.route\|@bp.route\|@api.route\|@router.' --include='*.py' \
  | grep -v 'requires\|login\|auth\|permission\|admin'
```

A route without its authz decorator.

## 8. The "the check is on the param not the session" shape

```python
if request.args.get('owner') == request.args.get('user'):   # both params
    return obj
```

Both sides are request params — set them equal and pass.

## 9. The "the check trusts the object's claimed owner" shape

```python
if obj.owner == session.user.name:    # obj.owner is a STRING field
    return obj
```

`obj.owner` is a settable string — set it to your name at create, or
`admin`, and pass.

## 10. The "the check is on a different field" shape

```python
if request.args.get('user_id') == str(session.user_id):
    return obj          # checks ?user_id=, not obj.owner_id
```

The check compares the *param* to the session, not the object's owner —
`?user_id=me` passes while `?id=victim` reads victim's object.

## 11. The "the check is on the bound field that's changeable"

```python
obj = Model.get(id)
if obj.user_id == session.user_id:    # obj.user_id is settable via update
    return obj
```

`PATCH /objects/42 {"user_id":<your_id>}` — reassign, then read.

## 12. The "the check is a JOIN" shape

```sql
SELECT * FROM objects WHERE id=? AND owner_id IN (SELECT id FROM users WHERE session_token=?)
```

If the `session_token` subquery matches another token (a stale one),
the join resolves to another's ownership.

## 13. The "the check is in a decorator that's skipped" shape

```python
@requires_owner
def get_object(id): ...

@route('/api/objects/<id>')
def api_object(id):
    return get_object(id)         # does the decorator run?
```

The decorator is on some routes; the route that skips it is the bug.

## 14. The "the authz middleware order" grep

```python
app.get('/admin/users')         # defined BEFORE app.use(admin)
app.use('/admin', adminAuthz)   # mounted after — doesn't protect it
```

Grep for `app.get`/`app.post`/`app.route` that appear *before* the
`app.use` for their prefix.

## 15. The "the mount prefix" shape

```python
api = Blueprint('api', __name__, url_prefix='/api')
@api.route('/users/<id>')       # /api/users/<id> — has the authz
def user(id): ...

@app.route('/users/<id>')       # /users/<id> — no prefix, no authz
def user2(id): return user(id)
```

## 16. The "the version" shape

```python
@app.route('/api/v1/users/<id>')   # v1 has authz
@app.route('/api/v2/users/<id>')   # v2 doesn't (new code path)
```

## 17. The "the function-level" shape

```python
@app.route('/admin/flag')           # the route exists
def admin_flag():
    if request.args.get('role') == 'admin':   # the check is a param
        return flag
    # or no check at all
    return flag
```

## 18. The "the role is a client value" grep

```bash
grep -rn 'request.args.get.*role\|request.headers.*role\|request.cookies.*role' \
  --include='*.py'
grep -rn 'req.query.*role\|req.headers.*role\|req.cookies.*role' \
  --include='*.ts' --include='*.js'
grep -rn "args.get\|params.get\|query.get\|body.get" --include='*.py' \
  | grep 'admin\|role\|staff\|root\|superuser\|internal'
```

## 19. The "the default is the override" shape

```python
user_id = request.args.get('user_id', session.user_id)   # the override
```

`request.args.get('user_id', ...)` — the default is the session, the
param wins.

## 20. The "the check is the *absence*"

```python
@app.route('/notes/<id>')
def note(id):
    return Note.get(id)          # NO check at all
```

A handler that fetches by id and returns — the absence of any
`session.user`/`current_user`/`owner` reference is the IDOR.

## 21. The "the check is on the route but not the method" shape

```python
@app.route('/users/<id>', methods=['GET'])
@requires_owner
def get_user(id): ...

@app.route('/users/<id>', methods=['PUT','PATCH','DELETE'])
def update_user(id):              # no @requires_owner on write
    ...
```

## 22. The "the check is on the format" shape

```python
def user(id):
    if request.accept_mimetypes['text/html']:
        check_owner()              # only on the HTML path
    return render_json(User.get(id))
```

## 23. The "the check is the mount" shape

```python
# a Blueprint's authz is per-mount
api = Blueprint('api', url_prefix='/api')
api.before_request(authz)          # authz on the /api mount only
```

Routes outside the Blueprint's prefix skip the `before_request`.

## 24. The "the check is the wrong object's check" grep

```python
def get_invoice(invoice_id):
    invoice = Invoice.get(invoice_id)
    check_owner(invoice.order.user_id)   # checks the PARENT's owner
    return invoice                       # invoice reachable if parent is public
```

The check is on the *related* object — the child is reachable when the
parent's check is loose.
