# Summary deep — the complete mass-assignment picture

## The mechanism

```
request body → parser → binder → model.save() → serializer → response
                  ↑           ↑
             schema       the bug:
             check      coverage > declared
```

The binder maps request input to model attributes; mass assignment is
the mapping's coverage exceeding the form's declared fields. The extra
field — `role`, `is_admin`, `balance`, `verified`, `price`, `plan` —
lands on the model; if a decision reads it, it's a finding.

## The two-observation confirm

1. **storage** — `GET` through a DIFFERENT endpoint shows the field;
2. **decision** — the gated route/total/state changes.

Storage alone = inert (null result); decision alone = attribution
confusion. The class bar: a stored-but-unread field is NOT a finding.

## The surface

| Layer | The surface | The probe |
|---|---|---|
| endpoints | `PATCH /me` > `PUT` > `POST /register` > orders > import > GQL > admin | the widest binder first |
| fields | privilege > verify > econ > plan > ownership > workflow | the semantic, not spelling |
| carriers | flat > nested > form > prefixed > array > typed > PUT > override > query | the falsifier drives |

## The binder families

- **merge-all** (`Object.assign`, `setattr` loop, `create(req.body)`):
  everything binds — the bug is absence;
- **kwargs** (`User(**json)`): signature = schema; `TypeError` leaks;
- **allowlist** (`permit`, `$fillable`, `[Bind]`, `pick`): flat drops;
  nested/second-binder tunnels;
- **strict schema** (`additionalProperties:false`, `extra:forbid`):
  `400`; the form path bypasses;
- **deep merge** (`_.merge`, `deepmerge`): nested tunnels;
- **nested association** (`accepts_nested_attributes_for`): child
  model fields reachable;
- **discriminator** (`_t`, `type`): schema switch;
- **type coercion**: right-typed variant reaches.

## The falsifier depths

`400` → content-type dead (try form); `200`+drop → endpoint dead (try
nested/`PATCH`); drop everywhere → binder-family dead (try `/import`/
GraphQL/`/admin`); no privileged fields → class dead; stored+`403` →
inert field (next semantic).

## The carrier fallback

`role` flat JSON → `role=admin` form → `{"profile":{"role":..}}` nested
→ `user[role]=admin` prefixed → `roles:["admin"]` array → `role:1`/
`role:true` typed → `PATCH` → `PUT` → `?_method=` → `?role=` query →
GraphQL args.

## The class boundary

`author_id:9` access → `web-idor`; `__proto__`/`constructor` →
`web-prototype-pollution`; `$set`/`$ne` operators → `web-nosqli`;
step-skip request → `web-logic-flaw`; forged token → `web-auth-session`.

## The tool

```bash
python3 tools/web/binding_probe.py --url "$BASE/api/register" \
  --body 'username=p&password=x' --readback "$BASE/api/me"
```

## The honest-null rule

A stored field that changes nothing is a NULL result — record it,
don't cite it. The finding is the CHANGED DECISION, not the stored
bytes.

## The class status

**Catalogue** — nothing in this toolkit has solved one. Everything
here is published knowledge; the first solve promotes it to verified
and writes the first field-note.
