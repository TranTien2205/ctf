# Detection deep — the field inventory, the binder fingerprint, the probe grammar

## The field inventory, exhaustively

The model's writable surface is the union of five sources. A field
present in ANY is a probe candidate:

### Source 1 — read-back responses

```bash
curl -s -b "$JAR" "$BASE/api/me" | jq 'keys'
curl -s -b "$JAR" "$BASE/api/users/9" | jq 'keys'
curl -s -b "$JAR" "$BASE/api/orders/9" | jq 'keys'
```

Every key is a candidate — including keys the serializer shows but the
form never renders (`created_at`, `internal`, `verified`,
`permissions`). The read-back is the model's self-description.

### Source 2 — bundle and sourcemap

```bash
python3 tools/web/bundle_miner.py --url <bundle> --out /tmp/bundle
grep -rn "role\|admin\|balance\|verified\|price\|discount\|plan\|tier" \
  /tmp/bundle/sources/
```

The front-end builds the object the back-end binds — the JS often
constructs `{username, role, plan}` where the rendered form sends only
`username`. Diff what the JS CONSTRUCTS vs what the form POSTs.

### Source 3 — validation errors

```bash
curl -X POST "$BASE/api/register" -H 'Content-Type: application/json' \
  -d '{"username":123,"password":"x"}'
# → {"errors":["username must be string","role must be one of:
#    user,admin","plan is invalid"]}
```

Strict validators list the schema when rejecting — an enumeration gift.

### Source 4 — docs and introspection

`/openapi.json`, `/swagger.json`, `/api/docs`, GraphQL
`{__schema{types{name fields{name}}}}`. The official model dump.

### Source 5 — sibling/admin views

The admin panel renders fields the public API hides; a staff-facing
`GET /admin/users` dumps the full record. Also: `OPTIONS`/`Allow`
headers and `?_method`/`?debug` params.

## The binder fingerprint

| Evidence | Binder | Probe grammar |
|---|---|---|
| `X-Powered-By: Express`, Mongoose stack | merge or strict-schema | flat JSON, nested `{"user":{"role":..}}` |
| `user[username]` param names, `X-Runtime` | Rails strong params | `user[role]=admin` |
| `laravel_session` cookie | `$fillable`/`$guarded` | flat + `role[]=admin` |
| `csrftoken`, Django errors | ModelForm vs `create(**data)` | flat JSON on API, form on views |
| `JSESSIONID`, Spring errors | bean binding | flat + nested props `{"address.city"}` |
| `.NET`, IIS headers | model binding `[Bind]` | `Role`, `user.role`, case-insensitive |
| `__debug`, Flask 500s | `**json` / `setattr` loop | flat JSON |

## The endpoint-vs-binder map

One model, several binders — each with a DIFFERENT allowlist:

| Endpoint | Typical binder | Width |
|---|---|---|
| `POST /register` | create — tightest allowlist | narrow |
| `PATCH /users/:id` | update — wider (editable fields) | WIDEST |
| `PUT /users/:id` | replace — binds or wipes | medium |
| `POST /admin/users` | admin create — widest | needs privilege edge |
| `POST /import` | bulk — often unguarded | wide |
| GraphQL mutation | args schema | spelled out |

## The probe grammar per binder type

- **merge-all** (`Object.assign`, `setattr` loop, `create(req.body)`):
  every key binds — flat extras land.
- **kwargs** (`User(**json)`): signature IS the schema — `TypeError`
  names rejected keys; nested objects become dict kwargs.
- **allowlist** (`permit`, `$fillable`, `[Bind]`, `pick`): flat extras
  die; nested under allowed parents may survive.
- **strict-schema** (Joi/zod/`additionalProperties:false`): `400` on
  unknown keys — kills the content-type; form path may bind anyway.

## What the fingerprint misses

- **version drift**: a Rails app may have `permit` on register but the
  admin controller unguarded — per-endpoint differences matter more
  than per-stack defaults.
- **middleware allowlists**: an Express `checkSchema` may strip extras
  before the route — the drop happens upstream of the model.
- **serializer-only views**: the field stores and is never returned —
  exercise it, don't read it back.
