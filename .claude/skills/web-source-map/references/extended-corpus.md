# Extended corpus — additional mining patterns

## The manifest probes

```bash
# Next.js — every route + its chunk
curl -s "$BASE/_next/static/$BUILD/_buildManifest.js"
# CRA/Vue — the full asset inventory
curl -s "$BASE/asset-manifest.json"   # or precache-manifest.[hash].js
# the service worker's precache list
curl -s "$BASE/sw.js" | grep -oE '"[^"]+\.js"'
```

## The `__NEXT_DATA__` probe

```bash
# serialized props + config in the entry page
curl -s "$BASE/" | grep -oE '<script id="__NEXT_DATA__"[^>]*>.*</script>' | sed 's/.*>//;s/<.*//' | python3 -m json.tool
```

## The env-inlined config

```bash
grep -oE '(REACT_APP|NEXT_PUBLIC|VUE_APP|VITE)_[A-Z_]+("?\s*[:=]\s*"?)[^,"'\'']+' bundle.js
grep -oE 'process\.env\.[A-Z_]+' bundle.js | sort -u
```

## The call-graph grep — find what calls the endpoint

```bash
# the endpoint string's surrounding function context
grep -oE '.{80}/api/admin.{80}' bundle.js
# the fetch/axios call wrapping it
grep -oE '(fetch|axios)\([^)]*/api/admin[^)]*\)' bundle.js
```

## The auth-flow grep — where the client stores the credential

```bash
grep -oE 'localStorage\.(set|get)Item\([^)]*\)' bundle.js | sort -u
grep -oE '(Authorization|Bearer|token|jwt|session)["'"'"'\s:=]+' bundle.js | sort -u
grep -oE 'document\.cookie' bundle.js
```

## The comment hunt in recovered source

```bash
grep -rniE '(TODO|FIXME|HACK|BUG|secret|password|key|flag|debug|admin|internal|temp)' recovered/
grep -rnoE 'flag\{[^}]*\}' recovered/
```

## The sink hunt in recovered source

```bash
grep -rniE '(eval|innerHTML|dangerouslySetInnerHTML|deserialize|pickle|yaml\.load|exec|child_process|subprocess|os\.system|render_template|fwrite|file_get_contents|open\()' recovered/
```

Each recovered-source sink routes to its class — the map recovered the
spec; the sink is the vuln.
