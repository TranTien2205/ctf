# Per-mechanism — the mass-assignment mechanisms, each as a unit

## Mechanism A — the merge-all binder

`Object.assign`, `setattr` loop, `create(req.body)`, `fill($request->
all())` — every key copied. The bug is ABSENCE of allowlist. Detect:
extra fields land flat. Falsifier: none at the binder — the model
falsifier or the check-set decides.

## Mechanism B — the kwargs signature

`User(**json)`, `Model.new(**params)` — the signature IS the schema.
`TypeError`/`ArgumentError` names rejected keys. Detect: `400` on
unknown keys. Bypass: the signature includes the dangerous field OR
the kwargs are filtered first (`params[:user]` vs `params.permit`).

## Mechanism C — the allowlist

`permit`, `$fillable`, `[Bind]`, `pick`, `fields=` — declared keys
only. The bug is the declared set being TOO WIDE (includes `role`) or
the nested tunnel (`profile` allowed → `profile.role` merges). Detect:
flat `role` dropped, `{"profile":{"role":..}}` lands.

## Mechanism D — the strict schema

`additionalProperties:false`, `extra:forbid`, `.strict()` — parser
kills extras. `400`/`422`. Bypass: the form path (different parser),
the update endpoint (different schema), the nested object (schema
validates the parent, not contents).

## Mechanism E — the deep merge

`_.merge`, `deepmerge`, `Object.assign` nested — recursive merge.
`{"profile":{"role":..}}` reaches `profile.role` the flat allowlist
can't drop. Detect: nested survives where flat died.

## Mechanism F — the nested association

`accepts_nested_attributes_for`, `profile()->update($request->profile)`
— the child's fields reachable through the parent's accepted key.
`user[profile_attributes][role]` or `{"membership":{"role":..}}`.
Detect: `profile`/`settings`/`membership` nested objects bind.

## Mechanism G — the discriminator switch

`_t`, `__t`, `type`, `user_type` — binding it selects the schema.
`_t:"AdminUser"` switches to the privileged variant — a different
surface. Detect: the field appears in the model but the sub-schema
switches.

## Mechanism H — the type coercion

String/bool/int/enum/FK coercion post-binding — the wrong type fails,
the right binds. `role:true` `400`s, `role:"admin"` binds;
`groups:"admin"` `500`s, `groups:[{"id":1}]` binds.

## Mechanism I — the method permutation

`POST`/`PATCH`/`PUT`/`?_method=` — different binders per method.
`PATCH` merge wide, `PUT` replace, `POST` create tight. Detect: same
field lands on `PATCH` where `POST` dropped it.

## Mechanism J — the serializer-hidden store

`toJSON`/`fields=`/`as_json` — the field stores, the response hides it.
The read-back is blind; the decision is the only evidence. Detect:
`GET` shows narrow keys but the gated route `200`s anyway.
