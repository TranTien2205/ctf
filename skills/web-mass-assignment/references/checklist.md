# Checklist — the mass-assignment audit

## Field inventory

- [ ] `GET /api/me` / object detail dumped — every key listed
- [ ] `bundle_miner` output grepped for `role|admin|balance|verified|price|plan|permissions|groups`
- [ ] Validation errors triggered (wrong-type probes) — schema leaked?
- [ ] `/openapi.json`, `/api/docs`, GraphQL introspection checked
- [ ] Admin/sibling views checked for the full field set

## Endpoint inventory

- [ ] `POST /register` — create binder
- [ ] `PATCH`/`PUT /users/me` / `/:id` / `/profile` — update binder
- [ ] `POST /orders` / `/checkout` / `/billing` — domain objects
- [ ] `/import` / `/seed` / `/bulk` — bulk binders
- [ ] GraphQL mutations — args schema
- [ ] `/admin/*` — admin binders (privilege edge first)

## Probe cells

- [ ] `role` flat JSON on the widest endpoint
- [ ] `role` form-encoded (different parser)
- [ ] `{"profile":{"role":..}}` nested tunnel
- [ ] `verified`/`is_active` — second semantic
- [ ] `balance`/`price`/`discount` — economic semantic
- [ ] `permissions`/`groups`/`roles` — array/scope semantic
- [ ] `user[role]`/`user.role` prefixed (Rails/.NET)
- [ ] `role[]`/`roles:[..]` array shape
- [ ] `role:true`/`role:1` type variants
- [ ] `PATCH` vs `PUT` vs `POST` method permutation

## Evidence

- [ ] Control pair — `{u,p}` vs `{u,p,role}` — byte-diffed
- [ ] Read-back through a DIFFERENT endpoint (not the write echo)
- [ ] Decision exercised — gated route/total/state changed
- [ ] `post-probe confirms` with verbatim read-back evidence
- [ ] Inert/null results recorded with depth annotated

## Class boundary

- [ ] Bound FIELD on own object → here (not object ACCESS → IDOR)
- [ ] `__proto__`/`constructor` → `web-prototype-pollution` routed
- [ ] `$`-operator keys → `web-nosqli` routed
- [ ] Step-skip request → `web-logic-flaw` routed
