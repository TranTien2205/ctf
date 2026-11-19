# Mechanism catalogue — every mass-assignment mechanism, indexed

## The binder mechanisms

| # | Name | Shape | Bug | Detection |
|---|---|---|---|---|
| B1 | merge-all | `Object.assign`, `setattr`, `create(req.body)` | absent allowlist | extras land flat |
| B2 | kwargs-signature | `User(**json)` | wide signature | `TypeError` on unknown |
| B3 | allowlist | `permit`, `$fillable`, `[Bind]`, `pick` | declared-set too wide / nested | flat drops, nested lands |
| B4 | strict-schema | `additionalProperties:false` | parser kills extras | `400`/`422` |
| B5 | deep-merge | `_.merge`, `deepmerge` | nested tunnel | nested survives flat-drop |
| B6 | nested-association | `accepts_nested_attributes_for` | child reachable | `profile`/`membership` binds |
| B7 | discriminator | `_t`, `type`, `__t` | schema switch | `_t` binds |
| B8 | method-permutation | `POST`/`PATCH`/`PUT`/`?_method` | different binders | PATCH lands, POST drops |

## The carrier mechanisms

| # | Name | Shape | Reach |
|---|---|---|---|
| C1 | flat-JSON | `{"role":"admin"}` | merge-all, allowlist |
| C2 | nested-JSON | `{"profile":{"role":..}}` | deep-merge, association |
| C3 | array | `{"roles":["admin"]}` | array-typed fields |
| C4 | dup-key | `{"role":"user","role":"admin"}` | last-wins parsers |
| C5 | form-flat | `role=admin` | form binder |
| C6 | form-prefixed | `user[role]=admin` | Rails/PHP nesting |
| C7 | dotted | `user.role=admin`, `User.Role` | qs/.NET convention |
| C8 | query | `?role=admin` | params-union binder |
| C9 | multipart | `role=admin` multipart | third parser |
| C10 | GraphQL | `input:{role:ADMIN}` | args schema |
| C11 | override | `?_method=PUT` | routing-permutation |

## The field-semantic mechanisms

| # | Semantic | Fields | Gate |
|---|---|---|---|
| F1 | privilege | `role`,`is_admin`,`is_staff`,`permissions`,`groups` | `/admin`, scope checks |
| F2 | verification | `verified`,`is_active`,`approved`,`activated` | `/flag`, verify gates |
| F3 | economics | `price`,`total`,`discount`,`balance`,`credits` | checkout, purchase |
| F4 | plan | `plan`,`tier`,`subscription`,`features` | `/premium`, feature flags |
| F5 | ownership | `author_id`,`owner_id`,`tenant_id`,`org_id` | scoping, authorship |
| F6 | workflow | `status`,`state`,`step`,`review_status` | state machines |
| F7 | internals | `debug`,`is_system`,`service_account` | operator paths |

## The guard mechanisms

| # | Guard | Layer | Bypass |
|---|---|---|---|
| G1 | schema | parser | form path, nested contents |
| G2 | allowlist | binder | nested, prefixed, second binder |
| G3 | type | coercion | right-typed variant |
| G4 | readonly | model | create binder, association |
| G5 | serializer | response | decision exercise, 2nd repr |
| G6 | ownership | access | your own `me`/`id` |
| G7 | discriminator | schema | sibling discriminator fields |
| G8 | concurrency | version | bound `version`/`__v` |

## The mechanism-to-budget map

5 probes per cell, priority:

1. `PATCH /me` `role` flat (B1/B3);
2. `PATCH /me` `{"profile":{"role":..}}` nested (B5/B6);
3. `PATCH /me` `verified`/`balance` (F2/F3);
4. `PATCH /me` `role=admin` form (C5);
5. `POST /register` `role` flat (B1 create).
