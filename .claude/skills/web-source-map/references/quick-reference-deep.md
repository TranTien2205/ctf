# Quick reference (deep) — the full command sheet

## The inventory

```bash
curl -s "$BASE/" | grep -oE 'src="[^"]+\.js[^"]*"' | sort -u            # scripts
curl -s "$BASE/" | grep -oE '"buildId":"[^"]+"' | head -1               # Next buildId
curl -s "$BASE/_next/static/$BUILD/_buildManifest.js"                   # Next routes
curl -s "$BASE/asset-manifest.json" | python3 -m json.tool             # asset list
curl -s "$BASE/sw.js" | grep -oE '"[^"]+\.js"' | sort -u               # precache
```

## The map probes

```bash
curl -s "$B" | tail -c 300 | grep -oE 'sourceMappingURL=.+'            # comment
curl -s -o m.json -w '%{http_code} %{ct}\n' "$B.map"                   # sibling
curl -sI "$B" | grep -i sourcemap                                      # header
echo '<b64>' | base64 -d > m.json                                      # inline
```

## `bundle_miner`

```bash
python3 tools/web/bundle_miner.py --url "$BASE/" --out recovered/
python3 tools/web/bundle_miner.py --file b.js --map b.js.map --out recovered/
python3 tools/web/bundle_miner.py --url "$BASE/" -H "Cookie: $C" --out recovered/
python3 tools/web/bundle_miner.py --file b.js --show-secrets --context 80
```

## The greps

```bash
# endpoints
grep -oE '"/(api|v[0-9]+|internal|admin|graphql|auth|file|upload)[^"]*"' b.js | sort -u
grep -oE '(fetch|axios\.[a-z]+)\s*\(["'"'"'`][^"'"'"'`]+' b.js | sort -u
# secrets
grep -oE 'eyJ[\w-]+\.[\w-]+\.[\w-]+' b.js
grep -oE '(AKIA|AIza|ghp_|glpat|xox[baprs]|sk_live|pk_live)[\w-]{8,}' b.js
grep -oE '(api[_-]?key|secret|token|password)["'"'"'\s:=]+["'"'"'][^"'"'"']+' b.js
# params + routes
grep -oE '[{,]\s*[a-zA-Z_$][a-zA-Z0-9_$]*\s*:' b.js | sort -u
grep -oE 'path\s*:\s*["'"'"'`][^"'"'"'`]+' b.js | sort -u
# flags/config/env
grep -oE '(feature|flags|config)\.[a-zA-Z_.]+' b.js | sort -u
grep -oE '(REACT_APP|NEXT_PUBLIC|VUE_APP|VITE)_[A-Z_]+' b.js | sort -u
grep -oE 'process\.env\.[A-Z_]+' b.js | sort -u
# flag + comments
grep -oE 'flag\{[^}]*\}' b.js
grep -rniE '//.*(TODO|secret|flag|password|admin|debug|internal)' recovered/
```

## The verify

```bash
curl -s -o /dev/null -w '%{http_code} %{ct}\n' "$BASE$ep"              # endpoint?
curl -s -H "Authorization: Bearer $K" "$BASE/api/me"                   # secret?
echo "$JWT" | cut -d. -f2 | base64 -d                                  # JWT decode
```

## The route map

endpoint+id→idor · query→sqli/nosqli · fetch-URL→ssrf ·
file-path→file-read · key→auth-session · flag/admin→logic/mass-assign ·
internal→ssrf · graphql→graphql · flag-shape→pre-flag
