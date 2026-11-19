# Detection — the host-header surface, exhaustively

The complete map of where the host-header surface lives.

---

## 1. The host-header signals — a reflected host

```bash
# a reflected host — a canonical-URL sink
curl -s -D - -H 'Host: canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
#   the canonical URLs point to canary.example → a stored injection
curl -s -H 'Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
#   the page's links/scripts point to canary.example → a stored injection
```

## 2. The forwarded-header signals — a reflected forwarded header

```bash
# a reflected forwarded header — a canonical-URL sink
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
#   the reset link points to canary.example → an account takeover
curl -s -H 'X-Forwarded-Host: canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
#   the page's links/scripts point to canary.example → a stored injection
```

## 3. The rewrite-header signals — a middleware rewrite

```bash
# a middleware rewrite — a gated route reached
curl -i "$BASE/admin"                        # expect 403
curl -i -H 'X-Original-URL: /admin' "$BASE/" # 200 with the admin body = finding
#   a 200 on the gated route → the middleware rewrites the path → an ACL bypass
```

## 4. The per-surface signal map — which signals name which surface

```text
a 'Host:|X-Forwarded-Host|X-Host|X-Forwarded-Server|X-HTTP-Host-Override'
  → a host-header surface
a 'X-Original-URL|X-Rewrite-URL|X-Forwarded-Path|X-Forwarded-Prefix|X-Original-Path|X-Real-Path'
  → a rewrite-header surface
a 'Forwarded:|X-Forwarded-For|X-Forwarded-Proto|X-Forwarded-Scheme'
  → a forwarded-header surface
a 'canonical|link|script|location|set-cookie|reset|password|cache'
  → a host-header sink
a 'admin|internal|private|restricted|403|acl|middleware|rewrite'
  → a rewrite-header sink
```

## 5. The per-proxy host-map — which headers each proxy adds

```text
nginx      → Host, X-Forwarded-Host, X-Forwarded-Proto, X-Forwarded-Port,
            X-Forwarded-Server, X-Forwarded-User, X-Forwarded-Email
Traefik    → Host, X-Forwarded-Host, X-Forwarded-Proto, X-Forwarded-Port,
            X-Forwarded-Server
Apache     → Host, X-Forwarded-Host, X-Forwarded-Proto, X-Forwarded-Server,
            X-Forwarded-User
HAProxy    → Host, X-Forwarded-Host, X-Forwarded-Proto, X-Forwarded-User
Cloudflare → Host, CF-Connecting-IP, CF-Ray, CF-Visitor, X-Forwarded-For,
            X-Forwarded-Proto
CloudFront → Host, X-Amzn-Trace-Id, X-Forwarded-For, X-Forwarded-Host,
            X-Forwarded-Proto, CloudFront-Viewer-Country
Akamai     → Host, True-Client-IP, Akamai-Origin-Hop, X-Forwarded-For
Varnish    → Host, X-Forwarded-For, X-Forwarded-Host, X-Forwarded-Proto,
            X-Forwarded-Server, X-Forwarded-User
Squid      → Host, X-Forwarded-For
```

## 6. The per-surface check — which check for which surface

```bash
# the canonical-URL check — a reflected host
curl -s -D - -H 'Host: canary.example' "$BASE/robots.txt" | grep -i 'location\|set-cookie'
# the reset-link check — a reflected forwarded header
curl -s -D - -H 'X-Forwarded-Host: canary.example' "$BASE/reset" | grep -i 'location\|set-cookie'
# the rewrite check — a middleware rewrite
curl -i -H 'X-Original-URL: /admin' "$BASE/"
# the forwarded check — a forwarded header
curl -s -H 'Forwarded: host=canary.example' "$BASE/page" | grep -o 'canary[^"< ]*'
```

## 7. The per-surface falsifier — when the surface is dead

```text
a proxy that validates the Host against a server list → a 400 on a bad
host → a negative result, not a retry signal.
a proxy that strips the client-supplied forwarded header → the header
doesn't reach the app → the bypass fails → a different class.
a proxy that verifies the forwarded header it added → a client-supplied
header is rejected → the bypass fails → a different class.
a trust check that reads a different input → a different class.
```

## 8. The per-surface reach — the downstream

```text
the surface's reach is the downstream — a canonical URL the app's links
rewrite — a reset link the victim clicks — a cache key the cache stores —
a Location the proxy redirects — a Set-Cookie the app binds — a middleware
rewrite the app's route reads.
```

## 9. The per-surface budget — the probe limits

```text
5 probes or 15 minutes per mechanism class; 25 probes or 45 minutes
for the challenge. a spent budget → escalate: chain_match → reclassify
→ writeup_search → novel_plan → fanout_sweep → solver_handoff.
```

## 10. The detection's proof — the host-header confirm

```text
the host-header confirm:
1. a reflected host → the app's canonical URLs point to canary.example
2. a rewritten path → a 200 on the gated route → an ACL bypass
3. the host-header's reach is the downstream — a reset link, a cache
   key, a Location, a Set-Cookie, a middleware rewrite
```
