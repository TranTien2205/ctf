# CTF shapes — the archetypes where IDOR appears

The challenge-shape → probe table. The shape names the id and the boundary.

---

## 1. The "view another's thing" app

A notes/files/orders/messages app where each user has private objects:

- Signal: `/api/notes/{id}`, `/files/{id}`, `/orders/{id}` — numeric or
  sequential id.
- Probe: two accounts, A creates, B reads A's id.
- Win: B reads A's private object → flag in the field.

## 2. The "admin's data" challenge

`GET /api/users/{id}` where `id=1` is admin — the flag is on admin's row:

- Signal: a `/users/{id}` endpoint, sequential ids.
- Probe: `id=1`/`id=0`/`id=admin` as a normal user.
- Win: the admin row returns `flag`/`secret`/`role`.

## 3. The "the invoice/report is a file" challenge

`?file=invoice_42.pdf` or `/download/report_42.pdf` — the filename is
the id:

- Signal: a download/report/invoice endpoint.
- Probe: `?file=../../etc/passwd` (traversal) or `?file=report_admin.pdf`
  or `?file=invoice_1.pdf` (adjacent).
- Win: another's file, or a flag file. See `file-idor.md`.

## 4. The "GraphQL node(id)" challenge

`query { node(id:"...") {...} }` — the Relay global id:

- Signal: `node(id:)` or `user(id:)` or `nodes(ids:)`.
- Probe: decode the b64, change `User:42`→`User:1`, re-encode.
- Win: the privileged object's field. See `graphql-idor.md`.

## 5. The "JWT sub is the user" challenge

The `sub`/`uid`/`user_id` claim names the user — change it:

- Signal: a JWT session.
- Probe: `jwt_forge --claims '{"sub":1,"role":"admin"}'` or a
  weak-secret re-sign.
- Win: the forged `sub` resolves to admin. See `web-auth-session`.

## 6. The "the API is versioned" challenge

`/api/v1/` is authz'd, `/api/v2/`/`/api/legacy/` is not:

- Signal: versioned prefixes.
- Probe: the same id on the other version.
- Win: the old version returns the object.

## 7. The "the mass-assign is the owner" challenge

`PATCH /me {"user_id":1}` or `{"role":"admin"}`:

- Signal: an update endpoint that echoes the bound fields.
- Probe: send the privileged field name.
- Win: `/api/me` shows the new role/owner. See `mass-assignment.md`.

## 8. The "the export/report leaks" challenge

`POST /export {"user_ids":[1]}` or `GET /report?for=1`:

- Signal: an export/report/download endpoint taking ids.
- Probe: another user's id.
- Win: the export contains their data / the flag.

## 9. The "the share link is the access" challenge

`/shared/{token}` where the token names a private object:

- Signal: a share/public-link feature.
- Probe: is the token predictable/sequential/enumerable?
- Win: another's shared object. See `predictable-ids.md`.

## 10. The "the bot visits as admin" challenge

An admin bot views a page you submit — the bot's session is the target:

- Signal: a `/report`/`/submit` that triggers a bot visit.
- Probe: stored XSS → steal the bot's session or its `id` → replay.
- The IDOR is in the *second* hop — see `second-order-idor.md`.

## 11. The "the bulk op skips the check" challenge

`POST /bulk {"ids":[1,2,3]}` or `GET /users?ids=`:

- Signal: a batch/bulk/export/multi endpoint.
- Probe: other users' ids in the bulk list.
- Win: the bulk returns all their objects.

## 12. The "the function is hidden" challenge

`/admin/users`/`/admin/flag` exists but isn't linked:

- Signal: the app has an admin role; the route is guessable.
- Probe: `GET /admin/*` as a normal user.
- Win: function-level access — see `function-level.md`.

## 13. The "the filter scopes" challenge

`?user_id=`/`?owner=`/`?author=`/`?created_by=` on a collection:

- Signal: a list endpoint with a filter param.
- Probe: `?owner=1` / `?user_id=admin` — the param overrides the scope.
- Win: the collection returns another's objects.

## 14. The "the id is a hash of a known" challenge

`id = md5(email)` / `sha1(username)` / `uuid5(ns, name)`:

- Signal: a long hex/id that maps to a name.
- Probe: recompute the hash for a known name (admin's email, the
  challenge author's handle).
- Win: predict another's id. See `predictable-ids.md`.

## 15. The "the OTP/reset id is the flag" challenge

`/reset?token={id}` or `/verify?code={id}` — the token names a session/
reset that carries privilege:

- Signal: a reset/verify/confirm endpoint.
- Probe: is the token predictable/bound to the wrong account?
- Win: account takeover. See `web-auth-session` (the class).

## 16. The "the multipart filename is the id" challenge

`filename="report_42.pdf"` — the filename carries the id:

- Signal: a multipart upload that stores by filename.
- Probe: `filename="../../etc/passwd"` or another user's filename.
- Win: traversal or overwrite. See `web-file-upload`.

## 17. The "the id is in the Referer" challenge

`Referer: /users/42` — a handler that reads it:

- Signal: the handler checks the Referer for the requesting resource.
- Probe: spoof `Referer: /users/1` to claim another's id.
- Win: the Referer's id is trusted.

## 18. The "the id IS the answer" edge

`/files/{flag}` — the id is the flag itself. The solve is finding the
route that accepts the flag as an id — the "IDOR" is the flag being a
valid object name.

## 19. The "two ids, one check" shape

`/api/tenants/7/users/42` — the route has tenant+user; the check is on
`tenant==session.tenant` but the `42` lookup ignores it. Or the check is
on `user==session.user` but the `7` is the tenant — a composite check
where only one part is bound.

## 20. The archetype → file table

| Signal | File |
|---|---|
| sequential int id | `sequential-enumeration.md` |
| uuid/ObjectId/snowflake | `uuid-analysis.md` + `predictable-ids.md` |
| b64 `Type:id` | `graphql-idor.md` + `identifier-formats.md` |
| REST endpoint | `api-idor.md` |
| filename/download | `file-idor.md` |
| collection/filter | `collection-filters.md` |
| bulk op | `api-idor.md` §5 |
| GraphQL | `graphql-idor.md` |
| JWT claim | `skills/web-auth-session/` |
| owner field update | `mass-assignment.md` |
| hidden function | `function-level.md` |
| second-order | `second-order-idor.md` |
| the check exists but loose | `ownership-models.md` |
| can't read but can act | `blind-idor.md` |
