# Mining toolkit — the commands and when each wins

## `bundle_miner` — the primary tool

`tools/web/bundle_miner.py` — crawls scripts, guesses maps, reconstructs
`sourcesContent`, inventories endpoints/routes/flags/secrets. Use it
before hand-grepping.

```bash
# the whole pipeline
python3 tools/web/bundle_miner.py --url http://TARGET/ --out recovered/
# a bundle/map on disk
python3 tools/web/bundle_miner.py --file main.js --map main.js.map --out recovered/
# session-gated
python3 tools/web/bundle_miner.py --url http://TARGET/ -H "Cookie: $C" --out recovered/
# secrets with context
python3 tools/web/bundle_miner.py --file main.js --show-secrets --context 80
```

Key flags: `--url`/`--file`/`--map`, `--out`, `--source-scheme`,
`--skip-node-modules`, `--show-secrets`, `--min-entropy`,
`--min-secret-len`, `--context`, `--lookahead`, `-H`, `--selftest`.

## curl — the fetch layer

```bash
curl -s "$BASE/"                                  # the entry page
curl -s -o m.json -w '%{http_code} %{ct}\n' "$B.map"  # a map probe
curl -sI "$B" | grep -i sourcemap                 # the header map
```

## grep — the mining layer

```bash
grep -oE '"/[A-Za-z0-9_./?=&{}:-]+"' b.js | sort -u      # endpoints
grep -oE 'eyJ[\w-]+\.[\w-]+\.[\w-]+' b.js               # JWT
grep -oE '(api[_-]?key|secret|token)["'"'"'\s:=]+["'"'"'][^"'"'"']+' b.js
grep -oE 'path\s*:\s*["'"'"'`][^"'"'"'`]+' b.js         # routes
grep -oE 'process\.env\.[A-Z_]+' b.js                  # env refs
grep -oE 'flag\{[^}]*\}' b.js                          # a flag shape
```

## strings — the obfuscation fallback

```bash
strings b.js | grep -oE '/[a-z0-9_./-]+|https?://\S+|flag\{[^}]*\}' | sort -u
```

## js-beautify / prettier — the reformat

```bash
npx js-beautify bundle.js -o pretty.js
npx prettier --write bundle.js
```

## python — the map decode

```python
import json
m = json.load(open('m.js.map'))
for s, c in zip(m['sources'], m.get('sourcesContent') or []):
    if c: print('===', s, '\n', c[:2000])
```

## jq / json.tool — the manifest parse

```bash
curl -s "$BASE/asset-manifest.json" | python3 -m json.tool
curl -s "$BASE/" | grep -oE '<script id="__NEXT_DATA__"[^>]*>[^<]+' | sed 's/.*>//' | python3 -m json.tool
```

## The verify layer — curl again

```bash
curl -s -o /dev/null -w '%{http_code} %{ct}\n' "$BASE$ep"          # endpoint?
curl -s -H "Authorization: Bearer $K" "$BASE/api/me"               # secret?
```

## The choice rule

`bundle_miner` for the inventory; grep for a specific token;
`strings`+grep for obfuscation; `js-beautify` to read structure; python
to decode a map by hand; `curl` to verify every lead.
