# Evidence playbook — the prove-it runbook

## The lead → proof sequence

```
a bundle string -> a live check -> a verdict -> a record
```

Every lead runs the same sequence; the verdict is one of `live`,
`dead`, `unverifiable`.

## The endpoint proof

```bash
resp=$(curl -s -w '\n%{http_code} %{content_type}' "$BASE$ep")
# real: 200/401/403/405 + a non-index body
# dead: 404, or a 200 serving the SPA index (catch-all)
```

The response bytes are the evidence — a `confirms` through `post-probe`
quotes the verbatim response excerpt:

```bash
python3 tools/hooks.py post-probe <chal> --hypothesis-id <h> \
  --class <class> --verdict confirms --evidence-kind class \
  --evidence '<verbatim excerpt>' --response '<the response bytes>'
```

## The secret proof

```bash
# JWT -> decode claims
echo "$K" | cut -d. -f2 | base64 -d 2>/dev/null
# key -> authenticate
curl -s -H "Authorization: Bearer $K" "$BASE/api/me" -o secret_resp
```

The unlocked response is the evidence — a verified secret's proof is
the data it returned.

## The flag proof

```bash
python3 tools/hooks.py pre-flag <chal> --value '<c>' \
  --source '<the source or response>' --evidence '<verbatim excerpt>'
```

A flag shape is a candidate until it passes `pre-flag` AND is read
from a live/artifact response.

## The flag-gate proof

```bash
# probe the gated endpoint as-is AND with the flag — if both 200, the
# gate is client-side
curl -s "$BASE$gated_ep" > g1
curl -s "$BASE$gated_ep?debug=1" > g2
diff -q g1 g2 && echo "server-enforced or identical"
```

A `200` as-is is a client-gate finding; a `403` both ways is a
server-enforced dead end.

## The provenance record

```json
{"lead": "/api/admin", "source": "main.js:1", "verify": "200 live",
 "verdict": "live", "route": "web-idor"}
```

Each lead carries `string, source_file, verify_result, verdict`. A
lead without provenance is not traceable; a finding without the live
check is not a finding.
