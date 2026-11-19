# Detection matrix — endpoint × field × carrier decision table

## The endpoint priority

| Endpoint | Binder width | Field surface | First probe |
|---|---|---|---|
| `PATCH /users/me` | WIDEST | all editable + privileged | `role` flat |
| `PUT /users/:id` | wide | replace — binds or wipes | `role` + full body |
| `POST /register` | narrow | create allowlist | `role` flat |
| `PATCH /profile` | wide | profile fields + nested | `{"profile":{"role":..}}` |
| `POST /orders` | domain | economic fields | `price`, `discount` |
| `POST /checkout` | domain | totals | `total`, `discount` |
| `POST /import` | bulk | unguarded | `role` |
| GraphQL `updateUser` | schema | args = fields | `role` arg |
| `POST /admin/users` | widest | all fields | needs privilege edge |

## The field semantic × endpoint table

| Semantic | Register | PATCH /me | Orders | Admin |
|---|---|---|---|---|
| privilege (`role`,`is_admin`) | probe | probe FIRST | — | — |
| verification (`verified`) | probe | probe | — | — |
| economics (`price`,`balance`) | — | `balance` | `price`,`discount` | — |
| plan (`tier`,`plan`) | — | probe | — | — |
| ownership (`author_id`) | — | — | — | `created_by` |
| workflow (`status`) | — | — | `status` | — |

## The carrier × endpoint matrix

```
                  POST/reg  PATCH/me  PUT/:id  POST/orders  GQL
json/flat            P         P        P         P          args
json/nested          P         P        P         P          input obj
form/flat            P         P        P         P          —
form/nested(u[r])    P         P        P         P          —
multipart            P         P        P         P          —
query ?role=         P         P        P         P          —
```

`P` = probe-worthy cell. Falsifier depth per cell:

- `400` on json/flat → kills the json row for that endpoint;
- `200`+drop on json/flat → kills flat keys for that endpoint, all
  content-types (binder-layer);
- nested survives where flat died → depth difference is the signal.

## The decision-coverage table

| Stored field | Decision to exercise | The gate |
|---|---|---|
| `role:admin` | `GET /admin`, `GET /api/admin/*` | role check |
| `is_admin:true` | same | boolean check |
| `permissions:[*]` | `POST /admin/users` | scope check |
| `verified:true` | `GET /flag`, `GET /verified-only` | verify gate |
| `balance:1e6` | `POST /purchase/flag-item` | balance check |
| `plan:pro` | `GET /premium` | plan gate |
| `price:0` | `POST /checkout` → total | totals code |
| `status:shipped` | `GET /orders/:id` state | workflow gate |

## The falsifier-remaining table

| Falsifier observed | Cells still open |
|---|---|
| `400` on JSON | form, multipart, query |
| drop on POST /register | PATCH /me, PUT /:id, /import |
| drop on ALL flat | nested under allowed parent |
| drop on register+PATCH | GraphQL, admin, /import |
| stored but inert `role` | `is_staff`, `permissions`, JWT re-issue |
| no privileged fields anywhere | class dead |

## The probe-budget map

5 probes per mechanism cell — the cells in priority order:

1. `PATCH /users/me` `role` flat;
2. `PATCH /users/me` `{"profile":{"role":..}}` nested;
3. `POST /register` `role` flat (form if JSON dropped);
4. `PATCH /users/me` `verified`/`balance` semantic;
5. content-type shift on the surviving endpoint.
