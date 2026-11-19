# Workflow playbook — the full sequence as a runbook

## Stage 1: INVENTORY (the bundle set)

```bash
curl -s "$BASE/" -o entry.html
grep -oE 'src="[^"]+\.js[^"]*"' entry.html | sed 's/.*="//;s/"$//' | sort -u > scripts.txt
# + manifests
BUILD=$(grep -oE '"buildId":"[^"]+"' entry.html | head -1 | cut -d'"' -f4)
[ -n "$BUILD" ] && curl -s "$BASE/_next/static/$BUILD/_buildManifest.js"
curl -s "$BASE/asset-manifest.json" | python3 -m json.tool 2>/dev/null
curl -s "$BASE/sw.js" | grep -oE '"[^"]+\.js"' | sort -u
```

The bundle set = scripts.txt + every manifest-named lazy chunk.

## Stage 2: MAP (per bundle)

```bash
while read s; do
  b="$BASE${s#/}"
  curl -s "$b" | tail -c 300 | grep -oE 'sourceMappingURL=.+'
  curl -s -o /dev/null -w "$s.map %{http_code} %{ct}\n" "$b.map"
  curl -sI "$b" | grep -iE 'sourcemap'
done < scripts.txt
```

`200 application/json` → reconstruct; `text/html` → catch-all; `404` →
string mine.

## Stage 3: MINE

```bash
python3 tools/web/bundle_miner.py --url "$BASE/" --out recovered/
# + targeted greps on every bundle (see extraction-playbook.md)
# + the recovered-source grep when a map exists
```

## Stage 4: TRIAGE

Rank: live secret > hidden endpoint > flag > internal host > sink >
flag-shape > client-route > public. Dedupe endpoints across chunks.

## Stage 5: VERIFY

```bash
# endpoint -> curl live
curl -s -o /dev/null -w '%{http_code} %{ct}\n' "$BASE$ep"
# secret -> authenticate
curl -s -H "Authorization: Bearer $K" "$BASE/api/me"
# flag -> probe the gate
curl -s "$BASE$gated_ep"
# flag-shape -> pre-flag
python3 tools/hooks.py pre-flag <chal> --value '<c>' --source '<s>' --evidence '<e>'
```

## Stage 6: ROUTE

| Lead | Route |
|---|---|
| endpoint+id | `web-idor` |
| query | `web-sqli`/`web-nosqli` |
| fetch-URL | `web-ssrf` |
| file-path | `file-read-primitives` |
| template | `web-ssti` |
| key | `web-auth-session` |
| flag/admin | `web-logic-flaw`/`web-mass-assignment` |
| internal | `web-ssrf` |
| graphql | `web-graphql` |
| redirect | `web-open-redirect` |
| flag-shape | `pre-flag` |

## Stage 7: RECORD

Each lead: `string, source_file, verify_result, verdict`. Each dead
lead: the same + the falsifier. A clean "mined, nothing actionable" if
the route is dead.

## The bounded rule

One entry fetch, the manifests, the map probes, one `bundle_miner`,
targeted greps, one verify pass — then route. Do not re-mine; the
exploit is the routed class.
