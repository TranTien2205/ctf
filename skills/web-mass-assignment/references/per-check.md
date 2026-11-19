# Per-check — every guard a mass assignment has to pass

## Check 1 — the schema check

`additionalProperties:false`, `extra:forbid`, `.strict()` — the parser
rejects unknown keys with `400`/`422`. Bypass: the form path (different
parser), the update endpoint (different schema), nested under an
allowed parent.

## Check 2 — the allowlist check

`permit(...)`, `$fillable`, `[Bind(Include)]`, `pick`, `fields=` — the
binder drops unlisted keys silently. Bypass: nested tunnels, prefixed
params (`user[role]`), the second binder (`PATCH` wider than `POST`).

## Check 3 — the type check

`role` is `String`/`enum` — `role:true`/`role:1` coerce-fail. Bypass:
the right-typed variant (`"admin"` for String, `1` for enum-int,
`[{"id":1}]` for FK-array).

## Check 4 — the readonly check

`attr_readonly`, `readOnly:true`, `editable:false`, frozen columns —
the model rejects writes on declared-readonly fields. Bypass: the
nested-association path (child model's writable fields), the create
binder (readonly may apply only to updates).

## Check 5 — the serializer check

`toJSON`/`as_json`/`fields=` on the RESPONSE — the field stores but
never returns. Not a binder block — exercise the decision directly.

## Check 6 — the scope check

`default_scope`, `defaultScope` — the query hides fields (e.g.
`deleted` records). The field stores; the scope hides it. Second
representation or the decision exercise.

## Check 7 — the discriminator check

`_t`/`type`/`__t` may be guarded — `{"_t":"AdminUser"}` dropped.
Bypass: the field may bind through a different carrier or the
discriminator may be settable at create-time only.

## Check 8 — the association check

`accepts_nested_attributes_for` may require `profile_attributes` not
`profile`; `belongs_to` may reject foreign keys. Bypass: the right
association name, the right key shape (`role_ids[]` vs `role_id`).

## Check 9 — the ownership check

`PATCH /users/:id` on another's id — the ownership check `403`s before
the binder runs. Not a mass-assignment block — an IDOR block; probe
your own `me`.

## Check 10 — the method check

`PATCH` allowed but `PUT`/`POST` different; `GET`+params may not reach
the binder. The method permutation is a different code path entirely.
