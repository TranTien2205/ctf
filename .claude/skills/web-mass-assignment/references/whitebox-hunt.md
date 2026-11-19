# White-box hunt — finding mass assignment in source

## The binder-call grep

```bash
grep -rn 'Object.assign.*req\.\|\.set(req\.\|create(req\.body\|create(.*body' src/
grep -rn 'User.create\|\.create(\|\.update(\|\.fill(\|\.save(' models/ routes/
grep -rn 'User(.*\*\*\|Model(.*\*\*\|setattr(' routes/ views/
grep -rn 'params\[:.*\]\|params.require\|\.permit(' controllers/
grep -rn '\$request->all()\|->fill(\|->update(' controllers/ models/
grep -rn '@RequestBody\|@ModelAttribute\|\[Bind' controllers/
grep -rn 'request.data\|request.json\|request.form\|request.values' views/
```

Every hit is a binder candidate; the ones WITHOUT an allowlist are the
mass-assignment sites.

## The allowlist grep — the defense

```bash
grep -rn 'permit(\|\$fillable\|\[Bind\|\.pick(\|fields=\|attr_accessible' \
  src/ controllers/ models/
grep -rn 'additionalProperties\|extra.*forbid\|\.strict()\|Joi\.\|zod\.' \
  src/ schemas/ validators/
```

Every allowlist found is a falsifier to verify — the declared set may
include the dangerous field (`permit(:name, :bio, :role)` is still
vulnerable if `role` is in the list).

## The model-field grep

```bash
grep -rn 'role\|is_admin\|admin\|balance\|verified\|is_staff\|perm' \
  models/ db/ migrations/ schemas/
grep -rn 't\.\(string\|boolean\|integer\)\s\+:\(role\|admin\|balance\)' \
  db/migrate/
```

The model's privileged fields — the probe set. `t.boolean :is_admin`,
`t.string :role`, `price`, `balance`, `plan` — every column is a
candidate writable field.

## The gate grep — what reads the field

```bash
grep -rn 'check_admin\|require_admin\|is_admin\|role.*admin\|permission' \
  middleware/ src/ controllers/ decorators/
grep -rn 'verified\|approved\|is_active\|email_verified' middleware/ src/
grep -rn 'total\|price\|balance\|checkout\|purchase' controllers/ src/
```

The decision map — the field → the check → the gate. The reach graph
is: `bindable field → gate that reads it → the gated resource`.

## The nested-association grep

```bash
grep -rn 'accepts_nested_attributes_for\|_attributes\|profile()->update' \
  models/ controllers/
grep -rn '_.merge\|deepmerge\|extend(' src/
```

The nested-tunnel sites — `accepts_nested_attributes_for` and the deep-
merge helpers.

## The discriminator grep

```bash
grep -rn '"_t"\|__t\|user_type\|type.*admin\|discriminator' models/ src/
```

The schema-switch fields.

## The source-vs-live gap

Source says `permit(:name, :bio)` but live `PATCH` binds `role` —
the running code may differ, or the allowlist is bypassed by a nested/
prefixed param. ALWAYS confirm the source's allowlist with a live
control/canary — the source is the map, the live response is the truth.
