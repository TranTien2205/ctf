# Per-boundary — every boundary the bound field must cross

## Boundary 1 — parser

`body → object`. `additionalProperties:false` kills extras here —
`400`. Content-type falsifier; the form path uses a different parser.

## Boundary 2 — schema

`object → validated object`. `.strict()`, `extra:forbid`, `Joi/zod`
validation. `422`/named-error — kills extras the parser passed.

## Boundary 3 — binder

`object → model instance`. `permit`/`$fillable`/`pick`/`[Bind]` — the
allowlist. `200` + silent drop — the endpoint falsifier.

## Boundary 4 — type coercion

`bound value → typed attribute`. String/bool/int/enum/FK — the wrong
type coerces or `500`s. `role:"admin"` binds where `role:true` fails.

## Boundary 5 — readonly

`attribute → writable attribute`. `attr_readonly`, `readOnly`,
`editable:false` — rejects writes on declared fields.

## Boundary 6 — persistence

`instance → stored record`. Mongoose `strict` drops non-schema keys at
`save()` — the echo shows, the store doesn't.

## Boundary 7 — serializer

`record → response representation`. `toJSON`/`fields=`/`as_json` — the
field stores but never returns; serializer-hidden.

## Boundary 8 — decision

`stored field → gated decision`. `check_admin()` reads `user.role` —
the field must reach the decision the gate makes. The stored-but-inert
case is a field crossing boundaries 1–7 but not 8.

## The boundary-annotated map

| Boundary | Kills | Survives |
|---|---|---|
| parser | `400` on JSON | form/multipart path |
| schema | `422` named error | the schema-free carrier |
| binder | flat extras | nested/prefixed/typed |
| type | wrong-typed value | right-typed variant |
| readonly | declared-readonly | child-model fields |
| persistence | non-schema keys | schema paths (the model's own fields) |
| serializer | all responses | the decision exercise |
| decision | inert fields | the gate's real field |

## The order matters

A field crossing boundary 3 (binder) but dying at 6 (persistence)
shows `role` in the echo, absent in the read-back — the classic echo-
lie. A field crossing 6 but dying at 8 (decision) is inert — the read-
back shows it, the gate ignores it.
