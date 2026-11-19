# Hop-by-hop deep — the Connection-header mechanics, exhaustively

The complete mechanics — how Connection controls which headers the proxy forwards.

---

## 1. The Connection header — the hop-by-hop control

```text
the Connection header is a hop-by-hop control — it names the headers
that apply to THIS connection only — a proxy strips the named headers
before forwarding the request to the next hop. the headers it names
are hop-by-hop; the rest are end-to-end.
```

## 2. The strip mechanics — what the proxy removes

```text
a proxy that honors Connection strips the headers it names:
- the standard hop-by-hop headers (Connection, Keep-Alive,
  Proxy-Authenticate, Proxy-Authorization, TE, Trailer,
  Transfer-Encoding, Upgrade)
- the headers named IN Connection (a client-supplied list)
a client-supplied Connection: keep-alive, X-Real-IP strips X-Real-IP —
even the proxy's own header.
```

## 3. The strip's scope — which headers the proxy strips

```bash
# the strip — a client-supplied Connection names the headers to strip
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Real-IP'
#   the proxy strips X-Real-IP → the app sees a request without it
```

## 4. The strip's reach — which headers are stripable

```text
any header the proxy forwards is stripable — a client-supplied
Connection names any header — the proxy strips it before forwarding —
even the proxy's own added header.
```

## 5. The strip's falsifier — a proxy that doesn't strip

```text
a proxy that doesn't honor Connection's strip → the header passes
through → the app's check reads it → the bypass fails → a different
class.
```

## 6. The strip's use — the trust-check bypass

```text
the strip's use: name the proxy's own header in Connection → the
proxy strips it → the app sees a request without the trusted header
→ a missing-header fallback → a local request → the trust check
bypassed.
```

## 7. The verified card's shape — the token_required bypass

```text
the verified card's shape: a Traefik proxy adds X-Real-IP — the app
checks it for a token_required route — naming X-Real-IP in Connection
strips it → the app treats the request as local → the token_required
check skipped → a restricted route reached.
```

## 8. The strip's per-proxy map — which proxies honor Connection

```text
nginx      → honors Connection — a strip
Traefik    → honors Connection — a strip
Apache     → honors Connection — a strip
HAProxy    → honors Connection — a strip
Squid      → honors Connection — a strip
Cloudflare → a per-rule config — some strips
Varnish    → a per-VCL config — some strips
```

## 9. The strip's per-header map — which headers to strip

```text
X-Real-IP          → the proxy strips X-Real-IP → a local-vs-remote check bypass
X-Forwarded-For    → the proxy strips X-Forwarded-For → a local-vs-remote check bypass
X-Forwarded-Host   → the proxy strips X-Forwarded-Host → a host check bypass
X-Internal         → the proxy strips X-Internal → an internal-route check bypass
X-Admin            → the proxy strips X-Admin → an admin check bypass
X-Original-URL     → the proxy strips X-Original-URL → a path check bypass
X-Forwarded-Scheme → the proxy strips X-Forwarded-Scheme → a scheme check bypass
X-Forwarded-Proto  → the proxy strips X-Forwarded-Proto → a proto check bypass
```

## 10. The strip's check — the two-request test

```bash
# the two-request check — does the proxy strip its own header
curl "$BASE/api/restricted"   # the normal request — the proxy's header present
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Real-IP'   # the proxy strips X-Real-IP
#   the second request reaches the app without X-Real-IP → a 200 vs a 401
```

## 11. The strip's edge — a keyed-header fallback

```text
an app that requires the proxy header → a missing header → a 400/401
→ no missing-header fallback → the strip doesn't bypass → a different
class.
```

## 12. The strip's edge — a non-header check

```text
a trust check that reads a different input (a session, a token, a
signature) → the header isn't the check's input → the strip doesn't
bypass → a different class.
```
