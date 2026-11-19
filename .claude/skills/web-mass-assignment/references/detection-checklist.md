# Detection checklist — the pre-probe audit

## The field inventory

- [ ] `GET /api/me` (or object detail) — full key list captured
- [ ] `GET` on a sibling object (another user's public view) — diff'd
- [ ] `bundle_miner --url <bundle> --out /tmp/bundle` run — sources extracted
- [ ] `grep -rn "role\|admin\|balance\|verified\|price\|plan\|perm" /tmp/bundle/sources/`
- [ ] wrong-typed probe sent — validation error's field list captured
- [ ] `/openapi.json` / `/api/docs` / `/swagger.json` checked
- [ ] GraphQL `{__schema{mutationType{fields{name args{name}}}}}` dumped
- [ ] admin/sibling views checked — the full field set

## The endpoint inventory

- [ ] `POST /register`, `/signup`, `/users` — create binder
- [ ] `PATCH`/`PUT /users/me`, `/:id`, `/profile`, `/settings` — update
- [ ] `POST /orders`, `/checkout`, `/cart`, `/billing` — domain objects
- [ ] `/import`, `/seed`, `/bulk`, `/migrate` — bulk binders
- [ ] GraphQL mutations — `createUser`, `updateUser`, `updateProfile`
- [ ] `/admin/users` POST/PUT — admin binder (privilege edge first)

## The binder fingerprint

- [ ] response headers read — stack identified
- [ ] error shape observed — merge vs kwargs vs allowlist vs strict
- [ ] content-types accepted — JSON, form, multipart
- [ ] method permutations — POST/PATCH/PUT/override
- [ ] nested support — `{"a":{"b":..}}` vs flat-only
- [ ] array support — `a[]`, `[..]` vs scalar-only
- [ ] prefix convention — `user[role]`/`user.role` if applicable

## The probe matrix

- [ ] control request sent and captured
- [ ] first canary: `role` flat JSON on the widest binder
- [ ] read-back through a DIFFERENT endpoint
- [ ] falsifier depth annotated — which cells remain live
- [ ] next cells queued — nested, form, PATCH, typed
