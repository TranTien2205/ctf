# Falsifiers — what kills a mass-assignment hypothesis and at what depth

The class falsifier from SKILL.md: **the server ignores or rejects
every undocumented field — the stored object is byte-identical to the
control submission**. But falsifiers fire at different depths, and the
depth decides what remains open.

## The depth table

| Depth | The result | What it kills | What stays open |
|---|---|---|---|
| content-type | `400 unknown property` on JSON | extra fields on the JSON path | form/multipart binder, other methods |
| endpoint | `200` + field dropped on read-back | extra fields on THIS endpoint's binder | `PATCH`/`PUT` on same model, nested paths |
| binder-family | drop on JSON AND form AND PATCH | the model's binders across carriers | sibling endpoints sharing the model |
| model | no privileged fields exist anywhere | the whole class on this app | nothing — class dead |
| semantic | field stores but changes no decision | that FIELD as a finding | other fields, other decisions |

## Falsifier 1 — strict schema rejection

`400 "unknown property: role"`, `400 "additional properties not
allowed"`, `TypeError: unexpected keyword argument`.

- **Kills**: extra fields on that content-type + endpoint.
- **Open**: the form/multipart path (different parser, different
  allowlist); `PATCH`/`PUT` (different binder); nested keys under
  allowed parents.
- **Reading**: a schema that NAMES the rejected field is still leaking
  the schema — `"role must be one of: user, admin"` tells you the field
  exists and its type.

## Falsifier 2 — the silent drop (allowlist)

`200`, write echoes or doesn't, read-back shows `role:"user"` — the
binder consumed the request and discarded the extra key. `pick()`,
`permit()`, `$fillable`, `[Bind(Include)]`, `fields=` all produce this.

- **Kills**: flat extra fields on that endpoint.
- **Open**: nested under an allowed parent (`{"profile":{"role":..}}`
  where `profile` is legit); the update binder (`PATCH` allowlists
  differ — the profile is meant to be editable); array/coercion paths.

## Falsifier 3 — the stored-but-inert field

`role:"admin"` STORES — read-back confirms — but `/admin` still `403`s.
The gate reads a different field: `is_staff`, `permissions`, a separate
admin table, a JWT claim minted elsewhere.

- **Kills**: that field as a decision-changer.
- **Open**: the field the gate ACTUALLY reads — find it in the gate's
  code or by diffing a real admin's record; other decisions the stored
  field might drive (display, totals).

## Falsifier 4 — the model-level absence

`GET` responses show no privileged fields on ANY object — the model is
genuinely narrow (role lives in a separate `admins` table, permissions
in a join table).

- **Kills**: the class on this app — nothing privileged to bind.
- **Open**: nothing on this surface; the bug is elsewhere.

## The pair discipline

A falsifier is only valid against a CONTROL. `role:"user"` on read-back
means nothing if the control also shows `role:"user"` — wait, that's
the point: the control SHOWS the default; the canary must differ. If
control and canary are byte-identical on read-back → the falsifier
fired (SKILL.md's exact wording).

## The near-miss traps

- **echo-only**: write response shows `role:"admin"`, read-back shows
  `"user"` — echo artifact, not storage. Falsifier.
- **type-error**: `role:true` dropped while `role:"admin"` would bind —
  one wrong-type probe ≠ the field dead; one right-type retry is
  legitimate.
- **cache**: read-back served a stale view — re-GET with cache-buster
  before recording the falsifier.

## Recording

```bash
python3 tools/hooks.py post-probe <ch> \
  --request "POST /register role=admin" \
  --verdict falsified --class web-mass-assignment \
  --hypothesis-id <id> --evidence-kind class \
  --evidence 'readback "role":"user" identical to control' \
  --response "$(cat readback.json)"
```

A falsifier with depth named (`endpoint`, `content-type`, `model`)
tells the next session exactly which cells remain open.
