# Anti-patterns deep — mass-assignment moves that LOOK right but aren't

## 1. The echo-as-proof anti-pattern

```bash
curl -X POST ... -d '{"role":"admin"}' → {"id":9,"role":"admin"}
# "it stored!" — recorded as evidence
```

The echo is the parser's view — `role` appeared in the response because
it was SET on the instance, not because it SAVED. Mongoose `strict`
does exactly this. The only storage evidence is a `GET` through a
different endpoint.

## 2. The spelling-sweep anti-pattern

```bash
for f in role isAdmin admin is_admin ROLE isAdminFlag access_level \
         user_role admin_flag superuser; do curl ... -d "{\"$f\":1}"; done
```

Ten spellings, ONE semantic. The model answers the privilege semantic
— a falsifier on `role` covers `isAdmin`/`admin`/`ROLE` too. Probe
the SEMANTIC space (privilege, verify, econ, plan, ownership, workflow)
— each semantic needs the right field name, not all spellings.

## 3. The inert-finding anti-pattern

```bash
curl ... -d '{"role":"admin"}' → stored
# "admin obtained!" — reported
```

`role:"admin"` stored but `/admin` still `403`s — the gate reads
`is_staff`. The class bar verbatim: a stored field never read is NOT
a finding. The bound field must CHANGE a decision.

## 4. The single-carrier-conclusion anti-pattern

```bash
curl ... -H 'Content-Type: application/json' -d '{"role":"admin"}' → 400
# "schema rejects extras — class dead"
```

`400` on JSON kills the JSON CELL — `role=admin` form-encoded uses a
different parser. The falsifier's depth decides what remains; a
content-type falsifier leaves five carriers open.

## 5. The control-skip anti-pattern

```bash
curl ... -d '{"username":"x","role":"admin"}' → GET shows "role":"admin"
# "bound!" — but was "admin" the default?
```

The control pair (`{u,p}` vs `{u,p,role}`) attributes the diff.
Without it, `admin` could be the platform default — the canary-only
observation is ambiguous.

## 6. The two-field-canary anti-pattern

```bash
curl ... -d '{"role":"admin","verified":true}' → GET shows both changed
# which field caused which? unattributable
```

ONE extra field per canary — two fields make the diff unattributable.
Split into two canaries.

## 7. The register-only-audit anti-pattern

```bash
# only POST /register probed → "no mass assignment"
```

The `PATCH`/`PUT` update binder is usually the WIDE one — register
allowlists `[u,p]`; the profile-edit allowlist is wider because
"profiles are meant to be editable." Probe the update endpoint FIRST.

## 8. The writeup-payload anti-pattern

```bash
# copying a writeup's {"is_admin":true} onto a challenge using "role"
```

The writeup's field names are ITS schema's — the field inventory is
per-target. The writeup is a mechanism hint, not a payload source.

## 9. The another-user-probe anti-pattern

```bash
curl -X PATCH "$BASE/users/9" -d '{"role":"admin"}'    # another user's id
```

The IDOR-adjacent mistake + a rules violation. Probe your own `me`/`id`
only — the ownership boundary is the scope.

## 10. The cached-falsifier anti-pattern

```bash
curl "$BASE/api/me" → "role":"user"  # from a cached view
# falsifier recorded — but the cache is stale
```

Re-GET with `?cb=<rand>` or a second representation before recording
the falsifier — the cache can lie.

## 11. The PUT-wipe anti-pattern

```bash
curl -X PUT "$BASE/users/me" -d '{"role":"admin"}'   # → account broken
```

`PUT` REPLACES — the extras bind but the omissions zero. PUT needs the
FULL control body + extras, not the field alone.

## 12. The dictionary-blast anti-pattern

```bash
# 100 field names × one endpoint — 95 aren't on the model
```

The dictionary covers SEMANTIC space, not volume — `binding_probe.py`'s
default set is the high-frequency shortlist; the field inventory from
`GET`s is the real source. Probe semantics, not spellings.
