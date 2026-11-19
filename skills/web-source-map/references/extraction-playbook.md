# Extraction playbook — the mining runbook

## Phase A: the tool pass

```bash
python3 tools/web/bundle_miner.py --url "$BASE/" --out recovered/
```

Read the output in value order: endpoint inventory → secret candidates
→ route paths → feature flags → `process.env` refs → recovered sources.

## Phase B: the targeted greps (on every bundle)

```bash
# endpoints — the route table
grep -oE '"/(api|v[0-9]+|internal|admin|graphql|auth|user|file|upload|export|debug)[^"]*"' *.js | sort -u
grep -oE '(fetch|axios\.[a-z]+)\s*\(["'"'"'`][^"'"'"'`]+' *.js | sort -u
# secrets — the credential candidates
grep -oE 'eyJ[\w-]+\.[\w-]+\.[\w-]+|(AKIA|ASIA)[0-9A-Z]{16}|AIza[\w-]{35}|(ghp|gho|glpat|sk_live|pk_live|xox[baprs])[\w-]{8,}' *.js
grep -oE '(api[_-]?key|secret|token|password|client_secret|auth)["'"'"'\s:=]+["'"'"'][\w./+@=-]{6,}' *.js
grep -oE '-----BEGIN [A-Z ]+PRIVATE KEY-----' *.js
# params — the injection points
grep -oE '[?&][a-zA-Z_$]+=|[{,]\s*[a-zA-Z_$][a-zA-Z0-9_$]*\s*:' *.js | sort -u
# routes — the client paths
grep -oE 'path\s*:\s*["'"'"'`][^"'"'"'`]+' *.js | sort -u
# flags/config/env — the gates and values
grep -oE '(feature|flags|config|debug|internal|isAdmin)\.[a-zA-Z_.]+' *.js | sort -u
grep -oE '(REACT_APP|NEXT_PUBLIC|VUE_APP|VITE)_[A-Z_]+|process\.env\.[A-Z_]+' *.js | sort -u
# the flag shape
grep -oE '(flag|ctf)\{[^}]*\}' *.js
```

## Phase C: the recovered-source pass (if a map)

```bash
# the file inventory
ls recovered/
# comments — TODO/secret/flag/gate notes
grep -rniE '//\s*(TODO|FIXME|HACK|secret|password|key|flag|admin|internal|debug|remove|hardcode|temp)' recovered/
# sinks — the vuln's class
grep -rniE 'eval|new Function|innerHTML|dangerouslySetInnerHTML|document\.write|deserialize|pickle|exec|spawn|child_process|readFile|file_get_contents|render_template|__proto__|merge\(' recovered/
# endpoints — the call layer
grep -rnoE '(fetch|axios)\s*\(["'"'"'`][^"'"'"'`]+' recovered/
# the flag
grep -rnoE '(flag|ctf)\{[^}]*\}|const\s+FLAG' recovered/
```

## Phase D: the structure pass (map without content)

```bash
# the sources list — the app layout
python3 -c "import json;print('\n'.join(json.load(open('m.js.map'))['sources']))"
# probe the hosted source paths
for p in src/config/x.js src/api/auth.js; do curl -s -o /dev/null -w '%{http_code} ' "$BASE/$p"; echo "$p"; done
```

## Phase E: the adjacent pass

```bash
for p in /.git/HEAD /.env /config.js /env.js /backup.zip /src/ /robots.txt /sitemap.xml; do
  printf '%-18s ' "$p"; curl -s -o /dev/null -w '%{http_code} %{ct}\n' "$BASE$p"
done
```

## The output

A deduped lead list — endpoints, secrets, params, routes, flags, hosts,
flag-shapes, recovered-source sinks — each with its source file, ready
to verify and route.
