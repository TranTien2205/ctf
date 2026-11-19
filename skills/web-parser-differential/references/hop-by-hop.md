# Hop-by-hop — the Connection-header bypass, the verified card's shape

The core mechanic — naming the proxy's own header in `Connection` strips it.

---

## 1. The model — a proxy that adds a trusted header

```text
a reverse proxy (Traefik, nginx, a WAF) adds a header the application
trusts — an X-Real-IP, an X-Forwarded-For, an X-Internal — the app
uses it to decide whether the request is local or authenticated.
the Connection header controls which headers the proxy forwards —
hop-by-hop headers are stripped before forwarding.
```

## 2. The bypass — the proxy strips its own header

```text
the Connection header is a hop-by-hop control — the proxy strips the
headers it names before forwarding. name the proxy's OWN header in
Connection → the proxy strips its own header → the app sees a request
without it → a missing-header fallback.
```

```bash
# the verified card's first probe — send the restricted request twice
curl "$BASE/api/restricted"   # the normal request — the proxy adds its header
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Real-IP'   # the proxy strips X-Real-IP
#   the second request reaches the app without X-Real-IP → the missing-
#   header fallback → a local request → the trust check bypassed
```

## 3. The mechanics — why the proxy strips it

```text
the Connection header is a hop-by-hop control — a proxy strips the
headers it names before forwarding the request. a proxy that honors
Connection strips the header the client names — even the proxy's own
header — the app sees a request without the trusted header.
```

## 4. The missing-header fallback — the app's trust check

```text
the app's trust check reads the proxy's header — a missing header
hits a fallback — the app treats the request as local or skips the
trust check — a local request bypasses the authentication or the
restriction.
```

## 5. The verified card's shape — the token_required bypass

```text
the verified card's shape: a Traefik proxy adds X-Real-IP — the app
checks it for an authenticated-only route — naming X-Real-IP in
Connection strips it → the app treats the request as local → the
token_required check skipped → a restricted route reached.
```

## 6. The probe — the two-request check

```bash
# the card's first_confirming_probe — the two-request check
curl "$BASE/api/restricted"   # the normal request — the proxy's header present
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Real-IP'   # the proxy strips X-Real-IP
#   the second request reaches the app without X-Real-IP → a 200 vs a 401
```

## 7. The bypass's scope — which routes are reachable

```text
the bypass reaches any route the proxy's header gates — an
authenticated-only route, an internal route, a restricted endpoint —
the app's trust check reads the missing header's fallback.
```

## 8. The bypass's falsifier — when the header check doesn't depend

```text
the card's falsifier: 'both forms are rejected, so the trust check
does not depend on that header' — the header isn't the trust check's
input → a different class.
```

## 9. The hop-by-hop headers — the other Connection-controlled headers

```text
the Connection header controls hop-by-hop headers — a proxy strips
the headers it names:
Connection: keep-alive, X-Real-IP       → the proxy strips X-Real-IP
Connection: keep-alive, X-Forwarded-For → the proxy strips X-Forwarded-For
Connection: keep-alive, X-Forwarded-Host→ the proxy strips X-Forwarded-Host
Connection: keep-alive, X-Internal      → the proxy strips X-Internal
```

## 10. The per-proxy hop-by-hop map — which proxies honor Connection

```text
Traefik   → honors Connection — the card's stack
nginx     → honors Connection (a reverse-proxy or a forward-proxy)
Apache    → honors Connection
HAProxy   → honors Connection
Squid     → honors Connection
```

## 11. The hop-by-hop falsifier — a proxy that doesn't strip

```text
a proxy that doesn't honor Connection's strip → the header passes
through → the app's check reads it → the bypass fails → a different
class.
```

## 12. The hop-by-hop's use — the bypass's reach

```text
the hop-by-hop bypass reaches a route the proxy's header gates — a
trust-check bypass — the missing-header fallback treats the request
as local — a privileged route reached.
```
