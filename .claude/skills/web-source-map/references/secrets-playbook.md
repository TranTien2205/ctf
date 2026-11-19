# Secrets playbook — the candidate-to-finding runbook

## Step 1: extract the candidates

```bash
python3 tools/web/bundle_miner.py --file b.js --show-secrets --context 80
# + the greps
grep -oE 'eyJ[\w-]+\.[\w-]+\.[\w-]+|(AKIA|ASIA)[0-9A-Z]{16}|AIza[\w-]{35}|(ghp|gho|glpat|sk_live|pk_live|xox[baprs])[\w-]{8,}' b.js
grep -oE '(api[_-]?key|secret|token|password|client_secret|auth)["'"'"'\s:=]+["'"'"'][\w./+@=-]{6,}' b.js
```

## Step 2: filter by context

`--context`/`--lookahead` shows the assignment a candidate lives in — a
`apiKey = "..."`/`Authorization: Bearer ...` is a real position; a
comment, a variable name, or a hash position is a false positive.

## Step 3: classify by shape

| Shape | Class |
|---|---|
| `eyJ...` | a JWT/session |
| `AKIA`/`AIza`/`ghp_`/`glpat`/`xox`/`sk_` | a cloud/service key |
| `-----BEGIN` | a private key |
| `apiKey`/`secret`/`token`/`password` assign | a generic credential |
| `postgres://`/`mongodb://`/`internal.svc` | an internal target |
| `pk_live_`/`NEXT_PUBLIC_`/Firebase `apiKey` | publishable — likely not a leak |

## Step 4: verify each

```bash
# a JWT — decode
echo "$CAND" | cut -d. -f2 | base64 -d 2>/dev/null | python3 -m json.tool
# a key — authenticate
curl -s -H "Authorization: Bearer $CAND" "$BASE/api/me"
curl -s -H "X-API-Key: $CAND" "$BASE/api/me"
curl -s "$BASE/api/me?api_key=$CAND"
# a service key — the provider's auth endpoint
curl -s -H "Authorization: token $CAND" https://api.github.com/user  # GitHub
curl -s -H "PRIVATE-TOKEN: $CAND" https://gitlab.com/api/v4/user      # GitLab
```

## Step 5: the verdict

| Result | Verdict | Route |
|---|---|---|
| decodes to real claims / authenticates | live credential | `web-auth-session` |
| fails auth / dead | dead key | record negative |
| publishable (`pk_`/`NEXT_PUBLIC_`) | public config | record, not a leak |
| internal host/string | a reach target | `web-ssrf` |
| `flag{`/const FLAG | a flag candidate | `pre-flag` |

## Step 6: the record

Each candidate: `string, source_file, shape, verify_result, verdict`.
A live one routes to `web-auth-session`; a dead/publishable one is a
recorded negative.

## The honesty rule

A secret candidate is not a leak — it is a leak only when it verifies.
A high-entropy string presented as a credential without the live check
is a false claim; the verify IS the finding.
