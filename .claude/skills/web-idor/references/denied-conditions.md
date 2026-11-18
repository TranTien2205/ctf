# Denied conditions — the falsifiers that close each route

The observations that close a probe branch. Each is recorded with
`hooks.py post-probe --verdict refutes`.

---

## 1. Ownership enforced (the class falsifier)

```
Identity B: GET /api/notes/1001 → 403 {"error":"Forbidden"}
or                              → 404
or                              → 200 {"id":1001,"owner_id":2,"text":"B-note"}
                                   # returns B's own object
```

The handler scopes to `session.user` — B can't reach A's object. The
route is closed for read-IDOR on this carrier. Record `refutes`.

## 2. The check-after-fetch held

```
B: GET /objects/42 → 403 {"error":"not the owner"}
```

The check ran, compared `obj.user_id` to `session.user`, denied. The
ownership model is enforced.

## 3. The scoped query

```
B: GET /objects/42 → 404 (the query was WHERE id=42 AND owner=B)
```

The query itself scoped — B's lookup can't even see the object. Closed.

## 4. The middleware ran

```
B: GET /admin/users → 403 {"error":"requires admin"}
or                   → 302 → /login (unauthenticated)
```

The authz middleware applied — function-level closed.

## 5. The format variant also checked

```
B: GET /users/1.json → 403
   GET /users/1.xml  → 403
   GET /users/1      → 403
```

Every format carries the same check — no variant escapes.

## 6. The method variant also checked

```
B: PUT/PATCH/DELETE /users/1 → 403
```

The check is on the object, not the method — write-IDOR closed.

## 7. The mass-assign filtered

```
B: PATCH /me {"role":"admin"} → {"role":"user"}   # unchanged
   PATCH /me {"role":"admin"} → 400 {"error":"role not permitted"}
```

The field is filtered — mass-assign closed for that field.

## 8. The bulk op checked

```
B: GET /users?ids=1,2,3 → [{"id":2,"owner_id":2,...}]   # only B's returned
   POST /bulk {"ids":[1]} → 403
```

The bulk is scoped — returns only B's objects.

## 9. The filter param ignored

```
B: GET /orders?user_id=1 → [{"id":1003,"user_id":2,...}]   # B's own
```

`?user_id=` was ignored — the collection is session-scoped. Closed.

## 10. The nested parent checked

```
B: GET /users/2/orders/42 → 403   # the parent check ran
   GET /users/1/orders/42 → 403   # even own parent, other's child — checked
```

The composite is fully checked — both parts bound.

## 11. The action also checked

```
B: POST /orders/1/cancel → 403
```

The action handler applied the check — action-IDOR closed.

## 12. The predictable-id exhausted

```
id_sweep over the full range → no hits beyond B's own
```

The space is swept; no other-attributable object found. The leak-source
is the next surface, not the sweep.

## 13. The recompute failed

`md5(email)`/`sha1(name)`/`uuid5(ns,name)` — recomputed for every known
name; no match. The id isn't name-derived.

## 14. The jwt/claim verify held

`sub:1` forged → `401`/`invalid signature` — the signature is the gate.
The IDOR-via-claim path closes (but `web-auth-session` may still win
on a weak key).

## 15. The hidden-carrier rejected

`X-User-Id: 1` → ignored; `?user_id=1` → ignored; `{"user_id":1}` in
body → ignored. The override doesn't bind.

## 16. The second-order not triggered

The stored XSS/bot-visit/job didn't fire — the second-order surface
isn't reachable on this target.

## 17. The "the object is public" negative

`GET /posts/1` → `200` but the post is *public* — the visibility flag
makes it intentionally readable. Visibility ≠ IDOR.

## 18. The "the response is empty" negative

`GET /users/1` → `200 {}` or `{"id":1}` — no attributable data. Not a
read.

## 19. The "the check is on the session, not the param" closure

`GET /me?user_id=1` → returns *your* data — the `me` route resolves via
session, the param is ignored.

## 20. The ledger entry

```bash
python3 tools/hooks.py post-probe "$C" --class web-idor \
  --hypothesis-id H1 --verdict refutes \
  --response '{"error":"Forbidden"}' --evidence '403'
```

A `refutes` with verbatim `--response` — the negative is the memory.
