# Quick reference

## The pipeline

```bash
# 1. script inventory
curl -s "$BASE/" | grep -oE 'src="[^"]+\.js[^"]*"' | sort -u

# 2. mine everything (endpoints + secrets + map recovery)
python3 tools/web/bundle_miner.py --url "$BASE/" --out recovered/

# 3. map probe
curl -s -o m.json -w '%{http_code} %{content_type}\n' "$BASE/static/js/main.js.map"

# 4. targeted greps when no map
grep -oE '"/[A-Za-z0-9_./?=&{}:-]+"' bundle.js | sort -u          # endpoints
grep -oE 'eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+' bundle.js  # JWT
grep -oE '(api[_-]?key|secret|token)["'"'"'\s:=]+["'"'"'][^"'"'"']+' bundle.js
grep -oE '(feature|config|flag|debug)[._][A-Za-z_.]+' bundle.js  # flags
```

## bundle_miner key flags

| Flag | Use |
|---|---|
| `--url` | entry page; crawls `<script src>` one level |
| `--file` | a bundle on disk (repeatable) |
| `--map` | a source map on disk or URL (repeatable) |
| `--out` | write `sourcesContent` here |
| `--source-scheme` | `normalise` strips `webpack://`; `reject` refuses |
| `--skip-node-modules` | drop dependency sources |
| `--show-secrets` | print secret candidates |
| `--min-entropy`/`--min-secret-len` | secret filter tuning |
| `--context`/`--lookahead` | widen capture around a hit |
| `-H K: V` | extra request header (auth) |

## Verify before claiming

| Found | Verify |
|---|---|
| endpoint | `curl $BASE<ep>` returns a real response |
| secret | it authenticates / decodes |
| route | server responds, not a client-only path |
| flag shape | `pre-flag` gate |

## Route the lead

endpoint+id→idor · query→sqli/nosqli · template→ssti · fetch-URL→ssrf ·
file-path→file-read · key→auth-session · flag→logic/mass-assign ·
internal→ssrf · graphql→graphql
