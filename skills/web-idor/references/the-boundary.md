# The boundary — where the check actually runs

The IDOR is defined by *where* the ownership check lives — or doesn't.

---

## 1. The check positions

```
[route] → [middleware/authz] → [controller] → [service] → [repo] → [db]
   ↑           ↑                   ↑             ↑          ↑
 mount-check  global-check      per-action     per-op     query-scope
```

The check can live at any layer; the bug is the layer that's *missing*
or *wrong*.

## 2. The mount-boundary

```
app.use('/api', authz)        — protects /api/* only
app.get('/api/users')         — guarded
app.get('/admin/users')       — NOT under /api — unguarded
app.get('/api/v2/users')      — under /api — guarded
app.get('/users')             — not under /api — unguarded
app.get('/internal/users')    — not under /api — unguarded
```

The mount prefix is the boundary — anything outside it is unguarded.

## 3. The decorator-boundary

```python
@requires_login
def profile(): ...

@requires_admin
def admin(): ...

def internal(): ...           # no decorator — unguarded
```

The decorator is the boundary; the undecorated function is the gap.

## 4. The controller-boundary

```python
class OrderController:
    def list(self):    self.require_owner(); ...
    def get(self):     self.require_owner(); ...
    def export(self):  ...   # no require_owner — the gap
```

One method in the controller skips `self.require_owner()`.

## 5. The service-boundary

```python
def get_order(order_id):
    order = repo.get(order_id)     # fetch
    if order.user_id != session.user_id:  # the check — in the service
        raise Forbidden
    return order
```

The check is in the service layer — a caller that bypasses the service
(a direct repo call) skips it.

## 6. The repo-boundary

```python
def get_for_user(id, user_id):
    return Order.filter(id=id, user_id=user_id).first()   # scoped query
def get(id):
    return Order.get(id)                                   # UNscoped
```

`get_for_user` scopes; `get` doesn't. The bug is a caller that uses `get`.

## 7. The query-boundary

```sql
SELECT * FROM orders WHERE id = ? AND user_id = ?    — scoped
SELECT * FROM orders WHERE id = ?                     — UNscoped
```

The `AND user_id = ?` is the boundary — its absence is the IDOR.

## 8. The ORM-boundary

```python
Order.find_by(id: id, user: current_user)             — scoped
Order.find(id)                                        — UNscoped
current_user.orders.find(id)                          — scoped via relation
Order.find_by!(id: id)                                — UNscoped
```

The scoped relation (`current_user.orders`) vs the global lookup
(`Order.find`) — the wrong call is the bug.

## 9. The GraphQL-boundary

```
type Query {
    me: User             — resolves to session.user (safe)
    user(id: ID): User   — resolves ANY id (the bug)
    node(id: ID): Node   — the Relay node access (the bug)
}
```

The field's resolver — `me` resolves to session; `user(id:)` resolves
any id. The bug is the `user(id:)`/`node(id:)` resolver without a check.

## 10. The "the boundary is the parent" shape

```
/tenants/7/users/42
```

`tenant_id == session.tenant` is checked; `user_id == session.user` is
checked *only relative to the tenant* — a `42` in tenant 7 vs a `42` in
your tenant. The child lookup may not scope to the parent.

## 11. The "the boundary is the relation" shape

`order.items` — the `order` is checked but `items` is joined without
scoping. `GET /orders/42/items` → the order check ran but the items
lookup is unscoped.

## 12. The "the boundary is the format" shape

```
GET /users/42        → 403
GET /users/42.json   → 200    # the .json handler skips the check
GET /users/42.xml    → 200
GET /api/users/42    → 200    # the /api mount is a different check
GET /users/42?format=json → 200
```

The `.json`/`.xml`/`format=` variant reaches a different code path —
the check is on the HTML path only.

## 13. The "the boundary is the method" shape

```
GET /users/42    → 403
PUT /users/42    → 200    # write path skips the check
PATCH /users/42  → 200
DELETE /users/42 → 204
POST /users/42   → 200
HEAD /users/42   → 200
OPTIONS /users/42 → 200
TRACE /users/42  → 200
```

The check is method-aware on `GET` only — the write/HEAD/OPTIONS path
skips it.

## 14. The "the boundary is the version" shape

```
GET /api/v1/users/42 → 403   # v1 is checked
GET /api/v2/users/42 → 200   # v2 is not (new code path)
GET /api/legacy/users/42 → 200
GET /api/internal/users/42 → 200
```

The version/mount is the boundary — a different code path skips it.

## 15. The "the boundary is the proxy" shape

```
GET /admin/flag          → 403 (the nginx rule)
GET /api/admin/flag      → 200 (the app route, no nginx rule)
GET /internal/admin/flag → 200
GET //admin/flag         → 200 (double-slash normalizes past the rule)
GET /admin/../admin/flag → 200
GET /admin%2fflag        → 200
GET /admin/flag/         → 200
GET /admin/flag.         → 200
GET /admin/flag..        → 200
GET /admin/flag%00       → 200
GET /admin/flag%20       → 200
GET /admin/flag%09       → 200
GET /admin/flag%0a       → 200
GET /admin/flag%0d       → 200
GET /admin/flag%3f       → 200
GET /admin/flag%23       → 200
GET /admin/flag;         → 200
GET /admin/flag;param=1  → 200
GET /admin/flag.js       → 200
GET /admin/flag.json     → 200
GET /admin/flag.html     → 200
GET /admin/flag.xml      → 200
GET /admin/flag.asp      → 200
GET /admin/flag.aspx     → 200
GET /admin/flag.php      → 200
GET /admin/flag.jsp      → 200
GET /admin/flag.do       → 200
GET /admin/flag.action   → 200
GET /admin/flag.cgi      → 200
GET /admin/flag.pl       → 200
GET /admin/flag.py       → 200
GET /admin/flag.rb       → 200
GET /admin/flag/anything → 200
GET /admin/flag/*        → 200
GET /admin/flag/.        → 200
GET /admin/flag/..       → 200
GET /admin/flag/../flag  → 200
GET /admin/flag/./flag   → 200
GET /admin//flag         → 200
GET //admin//flag        → 200
GET /admin/%2e/flag      → 200
GET /admin/%2e%2e/flag   → 200
GET /admin/%2e%2e%2fflag → 200
GET /admin/%252e%252e%252fflag → 200
GET /admin/..;/flag      → 200
GET /admin/.;/flag       → 200
GET /admin/;/flag        → 200
GET /admin/;param/flag   → 200
GET /admin/flag;param    → 200
GET /admin/flag;param=1  → 200
```

The nginx `location /admin` rule vs the app's normalization — the
`//`, `;param`, `.json`, `%2f`, the case, the suffix — a normalization
the rule doesn't match is the bypass. See `web-parser-differential`.

## 16. The "the boundary is the carrier" shape

```
GET /users/42              → 403  # path checked
GET /users?id=42           → 403  # query checked
POST /users {"id":42}      → 200  # body NOT checked
GET /users/42 (X-User-Id: 1) → 200 # header NOT checked
```

The check is on the path/query carrier, not the body/header carrier —
the same id in a different carrier bypasses.

## 17. The "the boundary is the role" shape

```
GET /users/42 as member  → 403
GET /users/42 as admin   → 200
GET /users/42 as service → 200
```

The check is `session.role == 'admin'` — your role determines the
boundary. The bypass is reaching a `service`/`internal` role.

## 18. The "the boundary is the tenant" shape

```
GET /tenants/7/users/42 as tenant7-user  → 200 (same tenant)
GET /tenants/7/users/42 as tenant8-user  → 403 (cross-tenant)
GET /users/42?tenant=7                   → the tenant param overrides
GET /users/42 (X-Tenant: 7)              → the tenant header overrides
```

The tenant is the boundary — a `?tenant=`/`X-Tenant:` override.

## 19. The "the boundary is the scope flag" shape

```
GET /orders           → your orders
GET /orders?scope=all → ALL orders
GET /orders?all=true  → ALL orders
GET /orders?include_private=true → includes private
```

The `scope`/`all`/`include_private` flag widens the boundary.

## 20. The "the boundary is a JOIN"

```sql
SELECT * FROM objects WHERE id=? AND owner_id IN (SELECT id FROM users WHERE session_token=?)
```

The join resolves `session_token` — a forged/stale/predictable token
joins to another's ownership. The boundary is the session_token lookup.
