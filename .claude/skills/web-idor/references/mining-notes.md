# Mining notes — the lessons IDOR batches taught

The operational heuristics that survived contact.

---

## 1. Two identities is the whole class

Every "IDOR" claim from a single account is suspect — the object was
probably yours. Register two accounts *first*; the probe is B reading
A's object.

## 2. The attributable marker

`200 {"id":42}` is not a read — `{"id":42,"owner_id":1,"email":"a@t.tld",
"text":"A-secret"}` is. The marker must name *A's* data, not just an id.

## 3. The `200` ≠ read

`200 {}` — an empty wrapper. `200 {"id":42}` — an echo. `200` on a
*public* object — intentionally readable. Only `200` carrying private
attributable data proves the read.

## 4. The `404` is ambiguous

`404` can mean "doesn't exist" or "denied-but-disguised". A `404` isn't
the falsifier — the *differential* (`403` on an existing id, `404` on a
missing one) is the oracle.

## 5. Sweep after checking

The two-identity probe on one known id is the cheapest decisive test;
`id_sweep` over a range is the enumeration step *after* the class is
proven. Don't invert the order.

## 6. The id's format first

`id=VXNlcjo0Mg==` — it's b64 `User:42`. Sweeping `id=1,2,3` misses the
real id; decode before assuming the format.

## 7. The carrier is the bug

`?id=42` → 403 but `{"id":42}` → 200 — the check is on the query, not
the body. Map *every* carrier before declaring the check present.

## 8. The method is the bug

`GET` → 403 but `PUT`/`PATCH`/`DELETE`/`HEAD`/`OPTIONS` → 200 — the
check is method-aware on GET only. One method's `403` isn't the class's.

## 9. The format is the bug

`.json`/`.xml`/`?format=` — the format variant reaches a different code
path. The check is on the HTML path.

## 10. The mount is the bug

`/api/users/42` checked, `/users/42` not — the Blueprint/mount prefix
carries the authz.

## 11. The version is the bug

`/api/v1/` checked, `/api/v2/`/`/api/legacy/`/`/api/internal/` not —
a new mount without the authz.

## 12. The param is the bug

`?role=admin`/`?user_id=1`/`?owner=1`/`?scope=all`/`?include_private=true`
— a query param overrides the session scope.

## 13. The header is the bug

`X-User-Id: 1`/`X-Role: admin`/`X-Admin: true`/`X-Internal: true` —
a client header overrides.

## 14. The cookie is the bug

`Cookie: role=admin`/`Cookie: user_id=1`/`Cookie: is_admin=1` — a client
cookie overrides.

## 15. The body is the bug

`{"user_id":1}`/`{"role":"admin"}`/`{"is_admin":true}` — a body field
binds to the model (mass-assign).

## 16. The claim is the bug

JWT `sub:1`/`uid:1`/`role:admin` — the claim names the user; a weak/
none signature lets you forge it.

## 17. The nested is the bug

`{"user":{"role":"admin"}}`/`{"user[role]":"admin"}`/`user.role` —
the nested key reaches the field.

## 18. The separator is the bug

`user\u002erole`/`user\u005crole`/`user\uff0erole` — the dot/colon/
backslash is encoded; a parser that splits on `.` misses it but the
binder sees `user.role`.

## 19. The array is the bug

`?id[]=1`/`?id[0]=1`/`{"id":[1]}` — the array-wrapper changes the check's
operand type.

## 20. The coerce is the bug

`id="1"`/`id=1.0`/`id=0x1`/`id=+1`/`id= 1`/`id=1%00`/`id='1'` — the
check compares a string; the param coerces to the int differently.

## 21. The operator is the bug

`{"id":{"$ne":0}}`/`{"id":{"$gt":0}}`/`{"id":{"$in":[1]}}`/`{"id":{"$regex":".*"}}`
/`{"id":{"$where":"1==1"}}` — a NoSQL operator in the id field.

## 22. The bulk is the bug

`?ids=1,2,3`/`POST /bulk {"ids":[...]}`/`POST /export {"user_ids":[...]}`
— the bulk op skips the per-object check.

## 23. The parent is the bug

`/users/42/orders/1001` — the `42` is checked, the `1001` isn't. Or the
`42` is *your* id but the `1001` is another's order.

## 24. The action is the bug

`POST /orders/42/cancel`/`.../refund`/`.../export`/`.../share` — the
action handler skips the owner check.

## 25. The field-list is the bug

`?fields=role,secret`/`?include=role`/`?expand=user.role`/`?populate=`
/`?select=`/`?only=`/`?pick=`/`?columns=`/`?projection=`/`?attrs=`/
`?properties=`/`?output=`/`?output_fields=`/`?response_fields=`/
`?return=`/`?returns=` — the column-picker leaks privileged fields.

## 26. The leak is the enumeration

The uuid v4 isn't sweepable — but the *collection* leaks it
(`GET /api/users` returns every `id`), a `?ids=` bulk returns them, a
GraphQL `edges` dumps them, a referer carries one. The leak-source is
the enumeration path.

## 27. The second-order is the read

`POST /export {"user_id":1}` → the job reads it with a service account.
The *first* hop accepts your id; the *second* reads it privileged.

## 28. The WS is a different path

The HTTP middleware doesn't run on the WS upgrade — the messages after
the upgrade are a different code path, often unguarded.

## 29. The "the check is the param" confusion

`?user_id=me` returns *your* object — the param was ignored, the session
resolved `me`. The `user_id` param being *present* isn't proof it binds.

## 30. The "the error is the map"

`"Cast to ObjectId failed"` → it's a Mongo ObjectId.
`"badly formed hexadecimal UUID"` → Python uuid.
`"invalid literal for int"` → Python int.
`"'role' is not fillable"` → Laravel fillable.
`"Strong parameter violation"` → Rails strong-params.
`"Mass assignment to 'role' not permitted"` → the guard exists.
`"did you mean 'role'"` → the field name.
The error names the format/field/guard — the map to the real shape.
