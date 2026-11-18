# Tooling — the repo's smuggling primitives

## `tools/web/crlf_probe.py` — the fold-matrix

```bash
python3 tools/web/crlf_probe.py --url "http://t/page?host={M}" \
  --value "example.com"
```

`--url` carries `{M}` marking the value slot — the probe fires the fold
matrix (`%0d%0a`, `%0d%0a%0d%0a`, lone `%0d`, lone `%0a`, `%250d`,
`%e5%98%8a`) into the slot — each variant graded against the baseline:
upstream-error text, folded-marker echo, or status delta.

Flags:

- `--url URL` — with `{M}` marking the injection slot
- `--param PARAM` — or a named param
- `--value VALUE` — the ordinary baseline value
- `--headers [HEADERS ...]` — extra headers
- `--timeout TIMEOUT`
- `--selftest` — prove the tool offline

## `tools/web/http_probe.py` — the request+response holder

```bash
python3 tools/web/http_probe.py --challenge <name> --url "http://t/" \
  --body "POST / HTTP/1.1 ..." --header "X-Test: 1"
```

Holds the request and the response together — emits the `post-probe`
command with `--response` pre-filled — the verbatim-excerpt requirement.

## `tools/web/variant_matrix.py` — the shape-sweep

```bash
python3 tools/web/variant_matrix.py --challenge <name> --url "http://t/" \
  --param host --families desync,crlf
```

One request per payload SHAPE — baseline-diffed — the live desync shape
ranks first.

## `tools/hooks.py` — the gate

```bash
python3 tools/hooks.py pre-probe <name> \
  --request "POST / HTTP/1.1 ..." --class web-request-smuggling \
  --hypothesis-id h1

python3 tools/hooks.py post-probe <name> \
  --request "POST / HTTP/1.1 ..." --verdict confirms \
  --evidence-kind class --class web-request-smuggling \
  --hypothesis-id h1 --evidence "<excerpt>" --response "<raw>"

python3 tools/hooks.py pre-flag <name> \
  --value "flag{...}" --source "response" --evidence "<excerpt>"
```

## `tools/state.py` — the ledger

```bash
python3 tools/state.py <name> --bug-class web-request-smuggling
python3 tools/state.py <name> --hypothesis "CL.TE via chunked fold"
python3 tools/state.py <name> --strategy-used chain_match
```

## `tools/decide.py` — the controller

```bash
python3 tools/decide.py <name>
```

Names the next step — `run_probe`, `novel_plan`, `switch_class`,
`verify_flag`, `record_solve`, `escalate`, `stop_report`.

## `tools/chain_match.py` — has this shape been solved

```bash
python3 tools/chain_match.py --record <name>
```

The `htb-weather-app-ssrf-crlf-request-smuggling-upsert` card — the
verified chain — the card's `first_confirming_probe` is the starting
probe.

## `tools/writeup_search.py` — the writeup shortcut

```bash
python3 tools/writeup_search.py "<challenge> <event>"
```

Once the name+event are known — the writeup names the desync pair.
