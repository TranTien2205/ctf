# Blind IDOR — the response tells you nothing, the side channel does

The endpoint returns `200`/`404`/`403` with an empty body — no object
data. The ownership signal has to come from a side channel.

---

## 1. The oracles

| Response | Signal |
|---|---|
| `200` | the id resolved — object exists AND accessible |
| `403` | the id exists but is forbidden — ownership enforced OR the object is real |
| `404` | the id didn't resolve — doesn't exist OR not yours |
| `400` | the id failed validation — wrong format |
| `302` | redirect — auth or object moved |
| `500` | the id reached a sink that crashed — partial check |
| timing | slow = object found+processed, fast = early-reject |
| length | long = object data, short = error |

A `403` on `id=1` but `404` on `id=99999` is an existence oracle — `1`
is a real (privileged) object, `99999` is not.

## 2. The existence oracle — `403` vs `404`

```
GET /api/users/1     → 403   (exists, forbidden)
GET /api/users/2     → 403   (exists, forbidden)
GET /api/users/3     → 403   (exists, forbidden)
GET /api/users/100   → 404   (doesn't exist)
GET /api/users/9999  → 404
```

`403` marks a real object; `404` marks nothing. This tells you *which*
ids exist — a useful map even without reading them.

## 3. The timing oracle

```
GET /api/users/1     → 120ms   (found, authz ran)
GET /api/users/99999 → 5ms     (early miss)
```

A slow response = the object was looked up; a fast = early miss. The
delta marks existence.

## 4. The length oracle

```
GET /api/users/1     → 1,234 bytes   (object data)
GET /api/users/99999 → 89 bytes      (error)
```

A longer response carries data — even if redacted, the length differs.

## 5. The write-side oracle

```
PUT /api/users/1 {"x":1}     → 200/204 (write hit)
PUT /api/users/99999 {"x":1} → 404     (no object)
PUT /api/users/1 {"x":1}     → 403     (exists, can't write)
```

A write `200`/`204`/`403` vs `404` — the write existence oracle. Test
writes only on your own objects or read-only probes.

## 6. The differential on the action

```
POST /api/orders/1/cancel     → 409 "already cancelled" — the object exists
POST /api/orders/99999/cancel → 404
POST /api/orders/1/cancel     → 403 — exists, forbidden
POST /api/orders/1/cancel     → 200 — ACTIONED — confirm the side effect
```

The action's error differs by object state — `already cancelled` proves
the order exists and you could reach its state.

## 7. The error-content oracle

```
GET /api/users/1     → "Forbidden: user 1 is not yours"
GET /api/users/99999 → "Not found"
```

The error text distinguishes "exists but forbidden" from "doesn't
exist" — a verbose error is the oracle.

## 8. The HTTP-method oracle

```
GET    /api/users/1 → 403
POST   /api/users/1 → 405 (method not allowed — object exists)
POST   /api/users/99999 → 404
```

`405` (method) vs `404` (not found) — the route resolved the id before
rejecting the method.

## 9. The header oracle

```
GET /api/users/1     → X-Total-Count: 1 / ETag / Last-Modified
GET /api/users/99999 → no such headers
```

A `ETag`/`Last-Modified`/`X-Count` header marks a real object.

## 10. The cache oracle

```
GET /api/users/1     → X-Cache: MISS → then HIT on repeat
GET /api/users/99999 → always MISS
```

A cached object exists; an uncached doesn't.

## 11. The second-order oracle

`POST /api/export {"user_ids":[1]}` → the export job sends an email/
webhook when done — the notification confirms the id was processed. Or
`POST /api/share` with another's id → the share link works → the id
exists.

## 12. The "the error leaks the next step" oracle

```
GET /api/users/1     → "Access denied. Contact admin@t.tld"
GET /api/users/99999 → "User not found"
```

The error naming the owner/admin/contact confirms the object.

## 13. The ambiguous-response disambiguation

When `200` is uniform (every id returns `200`), the response *content*
is the oracle:

- Does it contain A's attributable field?
- Does it contain *any* object (vs `{}`/`null`)?
- Does the `Content-Length` differ?
- Does a specific marker field appear?

`http_probe --evidence-regex` carries the marker — the response body,
not the status, is the proof.

## 14. The "all-403" shape

Every id returns `403` — the authz is enforced. The falsifier is met
for the read; try:

- A different method (PUT/PATCH/DELETE may differ).
- A different format (`.json`/`.xml`/`.csv`).
- A nested path (`/users/1/orders/42` — the parent may be unchecked).
- A bulk endpoint (`?ids=`).
- A `?user_id=` override on a collection.

## 15. The "all-404" shape

Every id returns `404` — the lookup is scoped to the session user
(can't even see other ids exist). The route is closed for read-IDOR;
try the collection endpoint, the filter param, or a different carrier.

## 16. The "the id is in a different object" edge

`/api/orders/42` is guarded, but the order's `invoice_id` is a separate
object reachable at `/api/invoices/{invoice_id}` — the *linked* id is
the reachable path. Follow the response's foreign keys.

## 17. The "you can't read but you can act" shape

`GET /orders/42` → 403, but `POST /orders/42/cancel` → 200 — the read
is guarded, the action isn't. An action-IDOR even when read-IDOR fails.

## 18. The "the existence oracle is the flag" edge

Some CTF challenges hide the flag behind `id=1` where `403` confirms
the admin object exists — the solve is finding the *other* carrier
(GraphQL `node`, the bulk endpoint, the second-order) that reads it.
