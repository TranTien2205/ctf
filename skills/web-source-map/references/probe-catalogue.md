# Probe catalogue — the runnable probe inventory

## Inventory probes

```bash
# entry scripts
curl -s "$BASE/" | grep -oE 'src="[^"]+\.js[^"]*"' | sort -u
# modulepreload / preload hints
curl -s "$BASE/" | grep -oE '(href|src)="[^"]+\.(js|mjs)[^"]*"' | sort -u
# Next buildId + routes
curl -s "$BASE/" | grep -oE '"buildId":"[^"]+"'
curl -s "$BASE/_next/static/$BUILD/_buildManifest.js"
curl -s "$BASE/_next/static/$BUILD/_ssgManifest.js"
# asset/service-worker manifests
curl -s "$BASE/asset-manifest.json" | python3 -m json.tool
curl -s "$BASE/sw.js" | grep -oE '"[^"]+\.js"' | sort -u
curl -s "$BASE/manifest.json" | python3 -m json.tool
```

## Map probes

```bash
# the comment
curl -s "$B" | tail -c 300 | grep -oE 'sourceMappingURL=[^ ]+'
# the sibling
curl -s -o m.json -w '%{http_code} %{content_type}\n' "$B.map"
curl -s -o m.json -w '%{http_code} %{content_type}\n' "$B.js.map"
# the header
curl -sI "$B" | grep -iE 'sourcemap|x-sourcemap'
# the inline data: map
curl -s "$B" | grep -oE 'sourceMappingURL=data:[^ ]+' | tail -1
# /static/maps/
curl -s -o /dev/null -w '%{http_code}\n' "$BASE/static/maps/$(basename $B).map"
```

## The bundle fetch

```bash
while read s; do curl -s "$BASE${s#/}" -o "bundle_$(basename $s)"; done < scripts.txt
```

## bundle_miner probes

```bash
python3 tools/web/bundle_miner.py --url "$BASE/" --out recovered/
python3 tools/web/bundle_miner.py --file b.js --map b.js.map --out recovered/
python3 tools/web/bundle_miner.py --url "$BASE/" -H "Cookie: $C" --out recovered/
python3 tools/web/bundle_miner.py --file b.js --show-secrets --context 80 --min-entropy 4.0 --min-secret-len 20
```

## Verify probes

```bash
# endpoint — real or catch-all/dead?
curl -s -o "$tmp" -w '%{http_code} %{content_type}\n' "$BASE$ep"; head -c 100 "$tmp"
# secret — authenticates?
curl -s -H "Authorization: Bearer $K" "$BASE/api/me"
curl -s -H "X-API-Key: $K" "$BASE/api/me"
curl -s "$BASE/api/me?api_key=$K"
# JWT — decode
echo "$JWT" | cut -d. -f2 | base64 -d | python3 -m json.tool
# flag gate — client or server?
curl -s "$BASE$gated_ep"; curl -s "$BASE$gated_ep?debug=1"; curl -s -H "X-Admin: 1" "$BASE$gated_ep"
# flag shape — gate it
python3 tools/hooks.py pre-flag <chal> --value '<c>' --source '<s>' --evidence '<e>'
```

## Adjacent-disclosure probes

```bash
for p in /.git/HEAD /.env /.git/config /backup.zip /app.zip /src/ /config.js /env.js /static/maps/ /package.json /robots.txt /sitemap.xml /.DS_Store /web.config /README.md; do
  printf '%-20s ' "$p"; curl -s -o /dev/null -w '%{http_code} %{ct}\n' "$BASE$p"
done
```

## The per-probe record

Each probe writes: `target, command, result, verdict`. A probe without
its command and result is not traceable; a probe that confirms is a
finding, that fails is a recorded negative.
