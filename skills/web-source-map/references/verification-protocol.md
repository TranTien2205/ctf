# Verification protocol — every lead gets a live check

## The rule

A bundle string is a *claim the client makes*, not a fact about the
server. Every lead is verified live before it is a target, and the
result is recorded. The verification IS the finding.

## The endpoint verify

```bash
# is the endpoint real?
code=$(curl -s -o "$tmp" -w '%{http_code}' "$BASE$ep"; )
# 200/401/403/405 -> exists; 404 -> dead client route; a 200 that is the
# SPA index -> a catch-all, not an endpoint
file "$tmp"; head -c 200 "$tmp"    # confirm it is not the index page
```

A real endpoint: `200`/`401`/`403`/`405` with a non-index body. A dead
one: `404`, or a `200` serving the index.

## The secret verify

```bash
# a JWT — does it decode to real claims?
echo "$CAND" | cut -d. -f2 | base64 -d 2>/dev/null | python3 -m json.tool

# a key — does it authenticate?
curl -s -H "Authorization: Bearer $CAND" "$BASE/api/me"
curl -s -H "X-API-Key: $CAND" "$BASE/api/me"
```

A verified secret returns data it should not / authenticates. A dead
one returns `401`/nothing.

## The flag verify

```bash
# is the gated endpoint reachable without the client gate?
curl -s "$BASE/api/admin"
# 200 (with the flag set or not) -> the gate was client-only -> a finding
# 403 stays 403 -> the server enforces -> the gate is real -> not a bypass
```

A client-side gate that the server does not enforce is a finding; a
server-side gate is a dead lead for the bypass.

## The route verify

A client route (`/admin`) vs a server endpoint (`/api/admin`): probe
both — the client path is SPA-only, the API path is real. The map names
the client path; the API prefix is the probe.

## The internal-host verify

An internal URL is a target only through a reach — an SSRF surface or a
reachable internal host. A `http://internal.svc` the browser cannot
reach is a *target for SSRF*, not directly verifiable — route it.

## The record

Each lead: `string, source_file, verify_result, verdict`. The verdicts:
`live` (a target), `dead` (a recorded negative), `unverifiable` (route
to a reach class). Every lead ends in one.
