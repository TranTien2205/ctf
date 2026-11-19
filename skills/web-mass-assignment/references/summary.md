# Summary — mass assignment in the shortest honest form

## What it is

A binder-layer bug: the framework maps request input into a model
object, and the mapping's coverage exceeds the form's declared fields.
The extra field lands on the model — and if it changes a decision
(privilege, verification, economics, plan), it's a finding.

## The mechanism

```
request body → parser → binder → model.save() → serializer → response
                  ↑ the bug lives here
```

The binder binds keys the form never declared — `role`, `is_admin`,
`balance`, `verified`, `price`, `discount`, `plan`, `permissions`.

## The two-observation confirm

1. **Storage**: `GET` through a DIFFERENT endpoint shows the field
   (`"role":"admin"` vs control `"user"`);
2. **Decision**: the gated route/total/state changes (`/admin` `200`).

Storage alone is a NULL result (inert field); decision alone is
attribution confusion.

## The endpoint priority

`PATCH /users/me` → `PUT /users/:id` → `POST /register` → `POST
/orders`/`/checkout` → `/import` → GraphQL → `POST /admin/*`.

## The field priority

`role`/`is_admin`/`isAdmin`/`is_staff` → `verified`/`is_active`/
`approved` → `balance`/`credits` → `price`/`discount`/`total` →
`plan`/`tier` → `permissions`/`groups`/`roles`.

## The carrier fallback

flat JSON → form → nested `{"profile":{"role":..}}` → prefixed
`user[role]` → array `role[]` → typed `role:1`/`role:true` → `PATCH` →
`PUT` → `?_method=` → GraphQL args.

## The falsifier depths

- `400` → content-type dead;
- `200`+drop → endpoint's flat cell dead;
- drop everywhere → binder-family dead;
- no privileged fields → class dead;
- stored+`403` → inert field; next semantic.

## The tool

```bash
python3 tools/web/binding_probe.py --url "$BASE/api/register" \
  --body 'username=p&password=x' --readback "$BASE/api/me"
```

## The boundary

`author_id:9` access → `web-idor`; `__proto__` → `web-prototype-
pollution`; `$`-operators → `web-nosqli`; step-skip → `web-logic-flaw`.

## The class bar

A stored field that is never read anywhere is NOT a finding — prove
the bound field changes a decision before citing it.
