# Detection workflows — the three detection paths end to end

## Path 1 — the black-box path (no source)

```
1. GET /api/me | jq 'keys'                    → field inventory
2. bundle_miner --url <bundle> --out /tmp/b   → endpoint + source map
3. grep bundle for privilege fields           → candidates
4. PATCH /users/me {"role":"admin"}           → first probe
5. GET /api/me                                → read-back
6. falsifier depth → next carrier/endpoint    → widen or stop
```

The black-box path leans on read-backs and the bundle — no source to
read, the model is inferred from responses.

## Path 2 — the white-box path (source supplied)

```
1. find the binder call                      → `create(`, `Object.assign`,
                                                `fill(`, `**json`, `permit`
2. find the model                            → `role`, `is_admin`, `balance`,
                                                `verified` columns/fields
3. find the gate                             → `check_admin`, `require_role`,
                                                `verified_required`, totals
4. the allowlist check                       → `permit`, `$fillable`, `pick`,
                                                `[Bind]`, `fields=`
5. the reach graph                           → field → binder → decision
```

```bash
grep -rn 'create(req.body)\|Object.assign\|\.fill(\|\*\*request\|permit(' src/
grep -rn 'role\|is_admin\|balance\|verified\|is_staff' models/ src/
grep -rn 'check_admin\|require_role\|is_staff\|permission' middleware/ src/
```

The white-box path reads the binder's allowlist directly — the reach
graph (field → binder → decision) is visible in source.

## Path 3 — the hybrid path (source + live)

```
1. source → the binder's allowlist            → which fields it accepts
2. source → the model's fields                → which are privileged
3. live → the endpoint's actual behavior      → control/canary confirms
4. live → the decision's actual behavior      → the gate's real check
```

The hybrid path: source says `permit(:name, :bio)` but live `PATCH`
binds `role` anyway — the source's allowlist may be stale, or the
running code differs. Trust the LIVE behavior over the source.

## The endpoint-enumeration workflow

```bash
# the route list
grep -rn 'app.post\|app.patch\|app.put\|router.post\|@app.route' src/ routes/
grep -rn 'Route::\|Route::post\|Route::patch' routes/
grep -rn 'def .*request\|@csrf_exempt' views/

# the body-accepting subset — only these bind
grep -rn 'req.body\|request.data\|request.json\|params\[:' routes/ src/
```

Every route that reads `req.body`/`request.data`/`params` is a binder
candidate — the subset that writes a model is the surface.

## The field-enumeration workflow

```bash
# the model's fields — migrations, schemas, serializers
grep -rn 'add_column\|field(\|CharField\|Column\|type:' models/ db/ migrations/
grep -rn 'role\|admin\|balance\|verified\|staff\|perm\|price\|plan' \
  models/ db/ serializers/

# the form's declared fields — what the UI sends
grep -rn 'name=\|ng-model\|v-model\|input' templates/ static/ frontend/
```

The diff: `model fields - form fields` = the probe set.
