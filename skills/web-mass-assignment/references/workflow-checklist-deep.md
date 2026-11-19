# Workflow checklist deep — the engagement checklist, phase by phase

## Phase 0 — setup (5 min)

- [ ] `state.py <name> --category web --target <url>` run — challenge registered
- [ ] `classify.py "<obs>"` run — web-mass-assignment named or considered
- [ ] `chain_match.py --record <name>` run — any card match? (catalogue — none expected)
- [ ] `bundle_miner --url <bundle> --out /tmp/bundle` run — endpoints + sources extracted
- [ ] response headers read — stack fingerprinted

## Phase 1 — field inventory (10 min)

- [ ] `GET /api/me` (or object detail) — full key list captured
- [ ] `GET` on a sibling object (another user's public view) — diff'd
- [ ] bundle grepped — `role|admin|balance|verified|price|plan|perm|staff|group`
- [ ] wrong-typed probe sent — validation error's field list captured
- [ ] `/openapi.json` / `/api/docs` / `/swagger.json` checked
- [ ] GraphQL `__schema` introspection dumped (if applicable)
- [ ] admin/sibling views checked — the full field set
- [ ] the field list written to `../field-notes.md` — the probe set

## Phase 2 — endpoint map (5 min)

- [ ] `POST /register`, `/signup`, `/users` — create binder listed
- [ ] `PATCH`/`PUT /users/me`, `/:id`, `/profile`, `/settings` — update
- [ ] `POST /orders`, `/checkout`, `/cart`, `/billing` — domain objects
- [ ] `/import`, `/seed`, `/bulk`, `/migrate` — bulk binders
- [ ] GraphQL mutations — `createUser`, `updateUser`, `updateProfile`
- [ ] `/admin/*` — admin binders (privilege edge first)
- [ ] `GET` routes with params — the query carrier

## Phase 3 — binder fingerprint (5 min)

- [ ] binder family identified — merge-all / kwargs / allowlist / strict
- [ ] content-types accepted — JSON, form, multipart
- [ ] method permutations — POST, PATCH, PUT, `?_method=`
- [ ] nested support — `{"a":{"b":..}}` vs flat-only
- [ ] array support — `a[]`, `[..]` vs scalar-only
- [ ] prefix convention — `user[role]`/`user.role`/`User.Role` if applicable
- [ ] discriminator fields — `_t`, `__t`, `type`, `user_type`

## Phase 4 — the probe matrix (15 min)

- [ ] control request — documented body, captured to file
- [ ] canary 1: `role` flat JSON on the widest binder (`PATCH /me`)
- [ ] read-back 1 — `GET` a DIFFERENT endpoint
- [ ] canary 2: `{"profile":{"role":..}}` nested tunnel
- [ ] canary 3: `role=admin` form carrier
- [ ] canary 4: `verified`/`balance` — second/third semantic
- [ ] canary 5: `role[]`/`roles:[..]`/`groups:[{id:1}]` typed/array
- [ ] each falsifier depth annotated in `../field-notes.md`

## Phase 5 — decision exercise (10 min)

- [ ] `GET /admin` / `/api/admin/*` — role gate
- [ ] `GET /flag` / `/verified-only` — verify gate
- [ ] `GET /premium` — plan gate
- [ ] `POST /checkout` — totals gate
- [ ] `POST /purchase/flag-item` — balance gate
- [ ] `GET /api/flag` — the flag itself

## Phase 6 — record + close (10 min)

- [ ] `post-probe confirms` — verbatim read-back evidence
- [ ] `post-probe falsified` — per dead cell, depth-annotated
- [ ] `post-probe confirms` (impact) — the decision diff
- [ ] `pre-flag` — the flag against its live response
- [ ] `classify_solve.py --chain <id>` — promotes catalogue→verified
- [ ] `../field-notes.md` — mechanism, falsifiers, carriers, payloads
- [ ] background processes cleaned
