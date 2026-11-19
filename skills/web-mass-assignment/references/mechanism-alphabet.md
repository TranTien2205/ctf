# Mechanism alphabet — the mass-assignment sub-mechanisms, A–Z

## A — allowlist-absent

`create(req.body)`, `Object.assign`, `setattr` loop, `fill($request->
all())`, `**json` (wide signature). Every key binds — the bug is no
allowlist at all. Probe: flat `role`/`is_admin`/`balance`.

## B — binder-family

The stack's binder: Rails `permit`, Laravel `$fillable`, Django
`create(**)`/ModelForm, Spring bean binding, ASP.NET `[Bind]`,
Express `create`/`Object.assign`, Go `ShouldBind`/tags. Each has its
grammar and its gaps.

## C — content-type carrier

JSON / form / multipart — three parsers, three binders. `role`
rejected on JSON may bind on form. The carrier is the second
allowlist layer.

## D — deep-merge

`_.merge`, `deepmerge`, `Object.assign` nested — recursive merge
reaching `profile.role`, `settings.admin`, `metadata.flags`. The
nested tunnel; also the `__proto__` overlap.

## E — echo-artifact

The write response echoing bound-then-dropped fields (Mongoose
`strict`). The echo is the parser's promise; the read-back is the
store's truth.

## F — falsifier-depth

content-type → endpoint → binder-family → model → semantic. The kill-
map's layers; each closes a different cell set.

## G — gate-read

`check_admin()`, `verified_required`, `totals()`, `plan_required` —
the decision reading the bound field. The bound field's value is its
reach to a gate.

## H — hidden-field

`role`, `balance`, `verified` — model fields the form never renders.
The writable surface's invisible part.

## I — inert-field

`role:"admin"` stored, `/admin` `403` — the gate reads elsewhere. A
null result, not a finding.

## J — join-table / nested-association

`memberships`, `user_roles`, `groups` — child models reachable through
`accepts_nested_attributes_for` or `{"membership":{"role":..}}`.

## K — kwargs-signature

`User(**json)` — the signature IS the schema; `TypeError` leaks the
writable set.

## L — last-wins parser

`{"role":"user","role":"admin"}` — JSON takes last; `role=user&role=
admin` — first-vs-last parser semantics. The two-validator gap.

## M — method-permutation

`POST`/`PATCH`/`PUT`/`?_method=` — different binders per method.
`PATCH` merge wide, `PUT` replace, `POST` create tight.

## N — nested-tunnel

`{"profile":{"role":..}}`, `{"settings":{"admin":..}}` — the parent
allowlisted as a unit; the merge reaches the nested field.

## O — ownership / IDOR-adjacent

`author_id`, `owner_id`, `tenant_id` — binding another principal's id.
The field-write (here) vs the object-access (IDOR).

## P — prefixed params

`user[role]`, `user.role`, `User.Role` — the nesting conventions
reaching fields flat keys can't.

## Q — query carrier

`?role=admin` — `params`/`request.values` merging query into the binder.

## R — read-back / serializer-hidden

The store's truth vs the write's echo; the field that stores but never
serializes.

## S — strict-schema

`additionalProperties:false`, `extra:forbid`, `.strict()` — the parser
kills extras; the form path bypasses.

## T — type-coercion

String/bool/int/enum/FK — the model's TYPE as a second filter.
`role:1` vs `role:"admin"` vs `groups:[{id:1}]`.

## U — update-binder

`PATCH`/`PUT` — the wider allowlist; the deep-merge site; the replace
wipe.

## V — vector

the carrier shape: flat / nested / array / dup-key / prefixed / dotted
/ query / multipart / GraphQL / override.

## W — write-then-read

the 4-leg protocol: control → canary → read-back → exercise.

## X — (cross-cutting) the reach graph

`field → binder → model → gate → resource`. The exploit is the
shortest path.
