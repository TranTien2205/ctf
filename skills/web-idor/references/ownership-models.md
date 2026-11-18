# Ownership models — the scoping the check should apply

The handler looks up the object — does it scope to *your* account? The
ownership model names the boundary.

---

## 1. The models

- **Single owner**: `object.user_id == session.user_id` — one user owns
  the object.
- **Tenant**: `object.tenant_id == session.tenant_id` — shared across a
  tenant's users.
- **Team/org**: `object.team_id in session.teams` — membership, not
  ownership.
- **Role-scoped**: `session.role >= required_role` — role gate, not
  object gate.
- **Public/private**: `object.public or object.user_id == session.user`
  — visibility flag.
- **Shared**: `object.id in session.shared_objects` — a share list.
- **ACL**: `session.user in object.acl` — per-object permission.
- **Ownership+role**: `object.user_id == session.user or session.is_admin`
  — admin bypass.

The bug is where the check is absent or checks the *wrong* field.

## 2. The check positions

```
handler(id):
    obj = db.get(id)                # 1. fetch
    if obj.user_id != session.user:  # 2. the check
        return 403
    return obj                       # 3. the data
```

The check can be:

- **At fetch**: `db.get(id, owner=session.user)` — scoped query, the
  safe form.
- **After fetch**: `if obj.user_id != session.user` — check-after-fetch,
  the common form.
- **In the query**: `WHERE id=? AND owner=?` — SQL-level.
- **In the ORM**: `Model.find_by(id:, user:)` — ORM-scope.
- **In the middleware**: `load_object` + `authorize` — two-step.
- **Missing**: `db.get(id)` — no check → IDOR.

## 3. The check-after-fetch bug

```python
# The common bug:
obj = db.get(id)                       # fetches ANY object
if request.method == 'GET' and obj.public:
    return obj                         # public read OK
if obj.user_id != session.user_id:
    return 403                         # ownership check — but only for private?
return obj
```

The check is conditional on `obj.public` — a `public` flag another user
set, or a flag you can flip via the update endpoint.

## 4. The tenant-boundary

`object.tenant_id == session.tenant_id` — all users in a tenant share
objects. The bug:

- `?tenant_id=other` overrides the session tenant.
- The session's tenant is settable via a header (`X-Tenant`).
- The object is in tenant A but the route resolves tenant B.
- `tenant_id` in the path is trusted over the session's.

## 5. The team/membership

`session.teams` is a list — the check `object.team_id in session.teams`.
The bug:

- `session.teams` is stale — you left the team but the session cached it.
- `object.team_id` is changeable via update.
- The check is `object.team_id == session.primary_team` but `primary_team`
  is user-settable.
- A `?team_id=` param overrides the membership check.

## 6. The public-flag trap

`object.public or owner` — the public flag is the boundary:

- `PATCH /objects/42 {"public":true}` — flip the flag (write-IDOR).
- The flag is checked on read but not on the flag's own update.
- `public` is the default for a create — everything is public.
- A `?include_private=true` param bypasses the public filter.

## 7. The shared-list

`object.shared_with` is a list of user ids/emails — the check is
`session.user in object.shared_with`:

- `POST /objects/42/share {"user":"you"}` — add yourself (write-IDOR).
- `?shared_with=you@t.tld` — a param that adds you.
- The share list is checked but the `shared_with` update isn't.
- `shared_with:["*"]`/`["all"]`/`["public"]` — a wildcard.

## 8. The ACL-per-object

`object.acl` is `{read:[u1], write:[u2], admin:[u3]}`:

- The read-ACL is checked on GET but the write-ACL on PUT is a different
  field — a partial check.
- `acl` is changeable via update — grant yourself.
- The `acl` field is a list — `acl[0]=you` adds you.

## 9. The ownership+role bypass

`obj.user_id == session.user or session.is_admin` — the `is_admin` is
the bypass:

- `is_admin` is a claim you forge (JWT) → see `web-auth-session`.
- `is_admin` is a body field you set (mass-assign) → see below.
- `is_admin` is a header you set (`X-Admin`).
- `is_admin` is computed wrong (`role === 'admin'` where role is a
  client field).

## 10. The "the check is on the wrong field" bug

```python
if request.args.get('user_id') == str(session.user_id):
    return obj          # checks the PARAM not the object
return 403
```

The check compares the *request param* to the session — not the
*object's* owner. `?user_id=me` passes while `id=victim` reads victim's
object.

## 11. The "the check is on the param, not the session" bug

```python
if request.args.get('owner') == request.args.get('user'):
    return obj          # checks owner==user in the REQUEST
```

Both are params — you set them equal → pass.

## 12. The "the check trusts the object's claimed owner" bug

```python
if obj.owner == session.user.name:
    return obj          # obj.owner is a STRING you set at create
```

`obj.owner` is a string field you set to your own name at create — or
to `admin` — the check compares a claim, not a bound id.

## 13. The "the bound field is changeable" bug

```python
obj = db.get(id)
if obj.user_id == session.user_id:     # obj.user_id is settable via update
    return obj
```

`PATCH /objects/42 {"user_id":<your_id>}` — reassign the owner → then
read it. The write-IDOR enables the read-IDOR.

## 14. The "the check is a JOIN that can be tricked" bug

```sql
SELECT * FROM objects WHERE id=? AND owner_id IN (SELECT id FROM users WHERE session_token=?)
```

If the `session_token` subquery matches another token (a stale/predictable
one), the join resolves to another user's ownership.

## 15. The "the check is in a decorator that's skipped" bug

```python
@requires_owner           # the decorator checks owner
def get_object(id): ...

@route('/api/objects/<id>')   # but this route calls it directly
def api_object(id):
    return get_object(id)     # does the decorator run?
```

The decorator/middleware is on *some* routes — the route that skips it
is the bug. Grep for which routes carry the check.

## 16. The "the check is on a different object" bug

```python
def get_order(order_id):
    order = Order.get(order_id)
    check_owner(order.user_id)         # checks the ORDER's owner
    return order

def get_invoice(invoice_id):
    invoice = Invoice.get(invoice_id)
    # no check_owner!
    return invoice                     # invoice is reachable even if order isn't
```

`/orders/42` is checked; `/invoices/{invoice_id}` (linked to the order)
isn't — the linked object is the path.

## 17. The model-vs-schema mismatch

The ORM model has `user_id` but the check is on `owner_id` — two field
names for the same thing. The check reads the wrong column.

## 18. The multi-tenant-key confusion

```python
obj = db.get(pk=(tenant_id, object_id))
```

The composite key is `(tenant, id)` — the handler may read `tenant_id`
from the session or from a `?tenant=` param. The param overrides.

## 19. The "soft-delete reveals" shape

`GET /objects/42` → 404 (soft-deleted), but `GET /objects/42?deleted=true`
or `/trash/42` returns it — the deleted object bypasses the normal check.

## 20. The "the owner check is on a different route" bug

`GET /users/42` checks owner, `GET /api/users/42` doesn't — the API
route and the HTML route have different middleware. Try both prefixes.
