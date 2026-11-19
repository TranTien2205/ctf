# Playbook — the compact runnable sequence

## The whole pass, runnable

```bash
BASE="http://TARGET"

# 1. inventory
curl -s "$BASE/" -o entry.html
grep -oE 'src="[^"]+\.js[^"]*"' entry.html | sed 's/.*="//;s/"$//' | sort -u > scripts.txt
BUILD=$(grep -oE '"buildId":"[^"]+"' entry.html | head -1 | cut -d'"' -f4)
[ -n "$BUILD" ] && curl -s "$BASE/_next/static/$BUILD/_buildManifest.js"
curl -s "$BASE/asset-manifest.json" 2>/dev/null | python3 -m json.tool
curl -s "$BASE/sw.js" 2>/dev/null | grep -oE '"[^"]+\.js"' | sort -u

# 2. map probes
while read s; do
  b="$BASE${s#/}"
  curl -s "$b" | tail -c 300 | grep -oE 'sourceMappingURL=.+'
  curl -s -o /dev/null -w "$s.map %{http_code} %{ct}\n" "$b.map"
done < scripts.txt

# 3. mine
python3 tools/web/bundle_miner.py --url "$BASE/" --out recovered/
python3 tools/web/bundle_miner.py --file main.js --show-secrets --context 80

# 4. targeted greps
for s in $(cat scripts.txt); do curl -s "$BASE${s#/}" -o "/tmp/$(basename $s)"; done
grep -oE '"/(api|internal|admin|graphql|file|upload|export|debug)[^"]*"' /tmp/*.js | sort -u
grep -oE 'eyJ[\w-]+\.[\w-]+\.[\w-]+|(AKIA|AIza|ghp_|sk_live|pk_live)[\w-]{10,}' /tmp/*.js
grep -oE '(api[_-]?key|secret|token|password)["'"'"'\s:=]+["'"'"'][^"'"'"']+' /tmp/*.js
grep -oE 'path\s*:\s*["'"'"'`][^"'"'"'`]+' /tmp/*.js | sort -u
grep -oE '(feature|flags|config|debug)\.[a-zA-Z_.]+' /tmp/*.js | sort -u
grep -oE 'flag\{[^}]*\}' /tmp/*.js recovered/ -r

# 5. verify + route
#   endpoint -> curl live; secret -> Authorization probe; flag -> probe
#   the gate; flag-shape -> pre-flag; route each verified lead to its class
```

## The decision table

| Found | Do |
|---|---|
| `.map` + `sourcesContent` | read recovered source for sinks/keys/flag |
| endpoint string | `curl` live → real → its class |
| secret candidate | `Authorization`/decode → authenticates → auth-session |
| feature flag | probe the gated endpoint → client gate → logic |
| internal host | `web-ssrf` reach |
| flag shape | `pre-flag` |
| `.map` presence | probe `.git`/`.env`/backups |
| a lazy/admin chunk | fetch + mine it |

## The route map

endpoint+id→idor · query→sqli/nosqli · fetch-URL→ssrf ·
file→file-read · template→ssti · key→auth-session · flag/admin→logic ·
internal→ssrf · graphql→graphql · redirect→open-redirect ·
param-by-name→its class · flag-shape→pre-flag
