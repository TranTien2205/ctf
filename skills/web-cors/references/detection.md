# Detection — finding the CORS-readable surface

CORS misconfiguration is a READ primitive — the question is whether
a foreign-origin page can read an authenticated response. The
signals that name it.

---

## 1. The class in one line

```text
the server reflects or accepts a foreign Origin AND allows
credentials → a cross-origin page can fetch() the endpoint and READ
the response — the data on it is exfiltrable.
```

## 2. The positive signals — the ACAO/ACAC surface

```text
- Access-Control-Allow-Origin reflects the request's Origin → a
  reflected-origin response
- Access-Control-Allow-Origin: * → a wildcard — open but no-creds
- Access-Control-Allow-Credentials: true → a credentialed read
- Access-Control-Allow-Methods / Allow-Headers → the preflight surface
- Access-Control-Expose-Headers → readable response headers
- a JSON endpoint the front-end fetches cross-origin — the pattern
  exists
```

```bash
curl -i "$BASE/api/me" -H 'Origin: https://evil.com' | grep -i 'access-control'
# ACAO reflecting your origin + ACAC:true → the read is open
```

## 3. The baseline vs foreign-Origin test — the central probe

```bash
# 1. baseline — no Origin
curl -i -b "$CJ" "$BASE/api/me"
#    → response body; note ACAO absent or a fixed value

# 2. foreign Origin — is it reflected?
curl -i -b "$CJ" "$BASE/api/me" -H 'Origin: https://evil.com'
#    → ACAO: https://evil.com? → reflected (vulnerable shape)
#    → ACAO: * → wildcard (no credentials allowed — limited)
#    → ACAO: https://target.com → fixed allowlist (closed)
#    → no ACAO → not CORS-open

# 3. ACAC — are credentials allowed?
curl -i -b "$CJ" "$BASE/api/me" -H 'Origin: https://evil.com' | \
  grep -i 'access-control-allow-credentials'
#    → true → the read carries cookies — the real vuln
```

## 4. The tool — `cors_probe`

```bash
python3 tools/web/cors_probe.py --url "$BASE/api/me" --method GET \
  --headers 'Cookie: session=x' --headers 'Origin: https://evil.com'
# measures the Origin-reflection + credentials surface
```

## 5. The endpoint surface — where CORS matters

```text
CORS is only interesting on endpoints that return SENSITIVE data
under a session:
- a /api/me, /api/user — the session's identity
- a /api/flag, /api/secret — the flag
- a /api/data, /api/private — private data
- an endpoint that returns a CSRF token — the token-read unlocks
  CSRF
a public endpoint's CORS-open is not exploitable — nothing to read.
```

## 6. The "the front-end already does it" signal

```text
a front-end on app.target.com that fetches api.target.com cross-
origin → the app NEEDS CORS configured → the misconfig surface.
the subdomain/allowlist may be too permissive.
```

```bash
# the front-end's own cross-origin calls
grep -rnoE "fetch\(|axios|XMLHttpRequest|api\.|crossorigin" <src>/static/*.js | head -20
```

## 7. The three ACAO shapes — the verdict

| ACAO value | Exploitability |
|---|---|
| `ACAO: <reflected-origin>` + `ACAC: true` | FULL — a credentialed cross-origin read |
| `ACAO: *` | open but credentials blocked — a public read only |
| `ACAO: <fixed-list>` | closed for other origins |
| no ACAO | not CORS-open |
| `ACAO: null` | the opaque-origin case — a data:/sandboxed page |

## 8. The classify/chain boundary — is it CORS or a sibling

```text
a cross-origin READ of a response     → web-cors
a cross-origin WRITE (no read)        → web-csrf
JS in the target's origin             → web-xss (stronger)
the server fetching a URL             → web-ssrf
a side-channel measure                → web-xs-leaks
```

## 9. The first-probe decision

```text
the class signal present → the first probe is the foreign-Origin
reflection + ACAC read:
  curl -i -b "$CJ" "$BASE/api/me" -H 'Origin: https://evil.com'
the ACAO/ACAC pair answers the whole class in one response.
```
