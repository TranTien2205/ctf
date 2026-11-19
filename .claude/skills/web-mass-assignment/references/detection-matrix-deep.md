# Detection matrix deep — the endpoint × field × carrier decision table, full

## The endpoint priority matrix

| Endpoint | Binder | Width | Surface | First probe |
|---|---|---|---|---|
| `PATCH /users/me` | update | WIDEST | all editable + priv | `role` flat |
| `PUT /users/:id` | replace | wide | binds or wipes | `role` + full body |
| `PATCH /profile` | merge | wide | profile + nested | `{"profile":{"role":..}}` |
| `POST /register` | create | narrow | form-declared | `role` flat |
| `PATCH /settings` | merge | wide | settings + nested | `{"settings":{"admin":..}}` |
| `POST /orders` | domain | medium | economic fields | `price`, `discount` |
| `POST /checkout` | domain | medium | totals | `total`, `discount` |
| `POST /import` | bulk | wide | unguarded | `role` |
| GraphQL `updateUser` | args | schema | spelled out | `role` arg |
| `POST /admin/users` | admin | widest | all fields | needs priv edge |

## The field-semantic × endpoint matrix

| Semantic | Register | PATCH /me | Orders | Profile | Memberships |
|---|---|---|---|---|---|
| privilege | `role`,`is_admin` | `role` FIRST | — | `profile.role` | `membership.role` |
| verification | `verified`,`is_active` | `verified` | — | — | — |
| economics | — | `balance` | `price`,`total` | — | — |
| plan | — | `plan`,`tier` | — | — | — |
| ownership | — | — | — | — | `tenant_id` |
| workflow | — | — | `status` | — | — |

## The carrier × endpoint matrix

```
               POST/reg  PATCH/me  PUT/:id  POST/orders  import  GQL
json/flat         P         P         P         P          P      args
json/nested       P         P         P         P          P      input
json/array        P         P         P         P          P      —
form/flat         P         P         P         P          P      —
form/prefixed     P         P         P         P          P      —
multipart         P         P         P         P          P      —
query ?role=      P         P         P         P          P      —
```

`P` = a probe-worthy cell; falsifier depth per cell decides the rest.

## The decision-coverage map

| Stored field | Gate to exercise | The decision |
|---|---|---|
| `role:admin` | `GET /admin`, `/api/admin/*` | role check |
| `is_admin:true` | same | boolean check |
| `permissions:[*]` | `POST /admin/users` | scope check |
| `verified:true` | `/flag`, `/verified-only` | verify gate |
| `balance:1e6` | `POST /purchase/flag-item` | balance check |
| `plan:pro` | `GET /premium` | plan gate |
| `price:0` | `POST /checkout` total | totals code |
| `status:shipped` | `GET /orders/:id` state | workflow |
| `author_id:1` | admin feed renders | authorship |

## The falsifier → remaining-cells map

| Observed | Dead | Open |
|---|---|---|
| `400` json/flat | json row, this endpoint | form, multipart, nested, PATCH, PUT, query |
| drop json/flat | flat keys, this endpoint | nested, prefixed, array, typed, other endpoints |
| drop all carriers | all binders, this endpoint | /import, GraphQL, /admin, override |
| no priv fields | user-model | other models' binders |
| inert `role` | `role` semantic | `is_staff`, `permissions`, JWT |

## The budget map

5 probes per mechanism cell, in priority:

1. `PATCH /users/me` `role` flat;
2. `PATCH /users/me` `{"profile":{"role":..}}` nested;
3. `PATCH /users/me` `verified`/`balance` — second semantic;
4. `POST /register` `role` — create binder;
5. content-type shift on the surviving endpoint.

A falsifier at any cell closes it; the "open" column is the queue.
