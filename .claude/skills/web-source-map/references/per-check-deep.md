# Per-check (deep) — the verify decision per lead class

## Endpoint-lead checks

```bash
# the verify — is it real, or a client route / catch-all / dead path?
curl -s -o "$tmp" -w '%{http_code} %{content_type}\n' "$BASE$ep"
head -c 200 "$tmp"   # is it the SPA index? -> catch-all, not an endpoint
```

- `200`/`401`/`403`/`405` + non-index body → real endpoint
- `404` → dead client route — record negative
- `200` serving the index → a catch-all — record negative
- `401`/`403` → real but gated — still a target

## Secret-lead checks

```bash
# JWT — decode
echo "$CAND" | cut -d. -f2 | base64 -d 2>/dev/null | python3 -m json.tool
# key — authenticate
curl -s -H "Authorization: Bearer $CAND" "$BASE/api/me"
curl -s -H "X-API-Key: $CAND" "$BASE/api/me"
curl -s "$BASE/api/me?api_key=$CAND"
```

- decodes to real claims / authenticates → a live credential →
  `web-auth-session`
- fails/dead/publishable → dead — record negative

## Flag-lead checks

```bash
# probe the gated endpoint directly — server-enforced or client-only?
curl -s "$BASE$gated_ep"                       # as-is
curl -s "$BASE$gated_ep?debug=1"               # with a flag guess
curl -s -H "X-Debug: 1" "$BASE$gated_ep"       # a header flag
```

- a public response → client gate → a find → `web-logic-flaw`
- a `403` that stays `403` → server-enforced → dead — record negative

## Route-lead checks

```bash
# client route vs server endpoint
curl -s -o /dev/null -w '%{http_code}\n' "$BASE/route"      # the SPA path
curl -s -o /dev/null -w '%{http_code}\n' "$BASE/api/route"  # the API path
```

- `/api/x` real → a server endpoint → its class
- `/x` renders but `/api/x` 404s → a client-only route — record

## Flag-shape checks

```bash
python3 tools/hooks.py pre-flag <challenge> --value '<candidate>' \
  --source '<the source or response>' --evidence '<the verbatim excerpt>'
```

- passes + live/artifact → the flag
- candidate only → not a flag

## Internal-host checks

```bash
# is the internal host reachable? (usually not directly — an SSRF target)
curl -s --max-time 5 -o /dev/null -w '%{http_code}\n' "$INTERNAL" 2>/dev/null || echo "unreachable"
# route to web-ssrf for a server-side reach
```

## The record shape per check

Each check writes: `lead, source_file, verify_command, result, verdict`.
`live` (a target), `dead` (a negative), `unverifiable` (route to a
reach class).
