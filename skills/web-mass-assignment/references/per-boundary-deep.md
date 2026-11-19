# Per-boundary deep — each boundary's filter and bypass, formally

## Boundary 1 — the parser (`body → object`)

`additionalProperties:false`, `extra:forbid`, `.strict()` — unknown
keys `400`/`422` here.

- **Kills**: extras on that content-type.
- **Bypass**: the form/multipart path (different parser, maybe no
  schema); `text/plain`→coerced bodies; a schema-free sibling endpoint.

## Boundary 2 — the schema validator (`object → validated object`)

`Joi`/`zod`/`pydantic`/`marshmallow` — validates types AND admission.

- **Kills**: wrong-typed AND unknown keys — `"role must be one of:
  user, admin"` names the schema.
- **Bypass**: the validator validates the PARENT (`profile` as object)
  without checking contents; the form path's different validator.

## Boundary 3 — the binder (`object → model instance`)

`permit`, `$fillable`, `[Bind]`, `pick`, `fields=` — the allowlist.
`200` + silent drop.

- **Kills**: flat extras on that endpoint.
- **Bypass**: nested tunnels (`{"profile":{"role":..}}`), prefixed
  params (`user[role]`), the second binder (`PATCH` > `POST`), the
  declared-set-includes-`role` case.

## Boundary 4 — the type coercion (`bound value → typed attribute`)

String/bool/int/enum/FK — the wrong type coerces or `500`s.

- **Kills**: wrong-typed values.
- **Bypass**: the right type — `role:"admin"` (String), `role:1` (enum
  int), `groups:[{"id":1}]` (FK array), `verified:true`/`1`/`"yes"`.

## Boundary 5 — the readonly (`attribute → writable attribute`)

`attr_readonly`, `readOnly:true`, `editable:false`, frozen columns.

- **Kills**: writes on declared-readonly fields.
- **Bypass**: the create binder (readonly may be update-only); the
  nested-association path (child model's writable `role`); the
  discriminator switch (the privileged schema where the field IS
  writable).

## Boundary 6 — the persistence (`instance → stored record`)

Mongoose `strict` drops non-schema keys at `save()` — the echo shows,
the store doesn't.

- **Kills**: non-schema keys at save.
- **Bypass**: the field IS a schema path (just not a form field) —
  `role`/`is_admin`/`balance` declared in the schema bind and persist.

## Boundary 7 — the serializer (`record → response`)

`toJSON`, `fields=`, `as_json`, `default_scope` — hides fields from
representation.

- **Kills**: read-back visibility.
- **Bypass**: a second representation (`/api/users/:id` vs `/api/me`,
  the admin view, the detail page); or exercise the decision directly.

## Boundary 8 — the decision (`stored field → gated decision`)

`check_admin()`, `totals()`, `verified_required` — the gate reading
the field.

- **Kills**: fields crossing 1–7 but reaching no gate — inert.
- **Bypass**: the field the gate ACTUALLY reads (`is_staff`,
  `permissions`, a JWT claim, a join table).

## The boundary map

```
extra field → parser → schema → binder → type → readonly → persist → serialize → decide
              400      422      drop     500     reject     drop       hide        inert
              bypass:  bypass:  bypass:  bypass: bypass:    bypass:    bypass:     bypass:
              form     nested   nested   right-   assoc     schema     2nd repr    gate's
                      object   tunnel   typed    /create    path       /decision   field
```

A field crossing all eight is a finding; each boundary's kill is a
falsifier at that depth.
