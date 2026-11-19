# Detection playbook — the runnable discovery sequence

## Step 1: the entry page

```bash
BASE="http://TARGET"
curl -s "$BASE/" -o entry.html
# the script inventory
grep -oE 'src="[^"]+\.js[^"]*"' entry.html | sed 's/.*="//;s/"$//' | sort -u > scripts.txt
cat scripts.txt
# the SPA / build markers
grep -oE '"buildId":"[^"]+"|__NEXT_DATA__|/_next/static/|/static/js/|/assets/index-' entry.html | sort -u
```

## Step 2: the manifests

```bash
# Next.js — every route + chunk
BUILD=$(grep -oE '"buildId":"[^"]+"' entry.html | head -1 | cut -d'"' -f4)
[ -n "$BUILD" ] && curl -s "$BASE/_next/static/$BUILD/_buildManifest.js"
# CRA/Vue — the asset inventory
curl -s "$BASE/asset-manifest.json" | python3 -m json.tool 2>/dev/null
# the service-worker precache
curl -s "$BASE/sw.js" | grep -oE '"[^"]+\.js"' | sort -u
```

## Step 3: the map probes

```bash
while read s; do
  b="$BASE${s#/}"
  echo "=== $s"
  curl -s "$b" | tail -c 300 | grep -oE 'sourceMappingURL=[^ ]*' 
  curl -s -o /dev/null -w "  .map -> %{http_code} %{content_type}\n" "$b.map"
  curl -sI "$b" | grep -iE 'sourcemap' 
done < scripts.txt
```

A `200 application/json` map → reconstruction; `text/html` → catch-all.

## Step 4: fingerprint the build

```bash
for s in $(cat scripts.txt); do
  curl -s "$BASE${s#/}" -o "/tmp/$(basename $s)"
done
grep -lE 'webpackChunk|__webpack_require__' /tmp/*.js    # webpack
grep -lE 'import\.meta|from\s*["'"'"'`]\./' /tmp/*.js     # Vite/ESM
grep -lE 'chunk-vendors|vue' /tmp/*.js                    # Vue
```

## Step 5: the decision

| Found | Next |
|---|---|
| a `200 json` map | `bundle_miner --map ... --out recovered/` |
| no map + readable strings | `bundle_miner --file ...` + greps |
| no map + opaque strings | `strings` + shape-grep |
| lazy chunks in manifest | fetch + mine each |

## Step 6: `bundle_miner` — the combined pass

```bash
python3 tools/web/bundle_miner.py --url "$BASE/" --out recovered/
python3 tools/web/bundle_miner.py --file /tmp/main.js --show-secrets --context 80
```

The output is the lead inventory — endpoints, routes, flags, secrets,
recovered sources.
