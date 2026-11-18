# API auth — bearer, API keys, HMAC signing, and the machine-to-machine surface

Browser auth (cookie+CSRF) differs from API auth (header+token). This
file covers the machine-facing shapes.

---

## 1. Bearer token surface

```
Authorization: Bearer <token>
Authorization: Token <token>
Authorization: JWT <token>
Authorization: <token>
X-Auth-Token: <token>
X-Access-Token: <token>
X-Api-Token: <token>
X-Session-Token: <token>
?access_token=<token>
?token=<token>
?api_key=<token>
?apikey=<token>
?auth_token=<token>
?bearer=<token>
```

Bugs: token in query (logged), token accepted in multiple carriers
(confusion between user token and service token), `Bearer` scheme not
enforced (raw token also accepted).

## 2. API key surface

```
X-API-Key: <key>
X-Api-Key: <key>
Api-Key: <key>
apikey: <key>
api_key: <key>
Authorization: ApiKey <key>
Authorization: Api-Key <key>
?api_key=<key>
?apikey=<key>
?key=<key>
?api=<key>
```

Bugs:

- Key is `md5(email)` / `sha1(username)` / `uuid1()` — computable.
- Key in `.env`/repo/`client.js` — hardcoded, shared across users.
- Key grants "the app" scope, not "the user" — swapping user claims
  inside a request signed with the app's key.
- `api_key` vs `api_key_id` — the id is public, the key is secret; some
  endpoints accept the id.
- Key scoping: a read-only key accepted on a write endpoint.

## 3. HMAC request-signing

```
X-Signature: <hmac>
X-Sign: <hmac>
X-Sig: <hmac>
Authorization: HMAC <keyid>:<sig>
Authorization: Signature keyId="<k>",signature="<s>",headers="date host"
```

Signed material usually: `method\npath\ndate\nbody-hash` or
`string_to_sign`. Bugs:

- `date`/`timestamp` not checked → replay forever.
- `nonce` not checked → replay within window.
- Body hash not covered → tamper the body, keep the sig.
- Path/query not covered → swap the path.
- `keyId` injection → the `keyId` is a `kid`-style lookup → traversal/
  SQLi to return a key you know.
- Signature over a canonicalized form the server doesn't actually
  reproduce → sign a *different* canonicalization.
- `X-Signature` verified against `request.body` but the handler parses
  a different body (content-type confusion).

## 4. The service-token confusion

Apps issue *two* token families:

- **user token** — `aud=user`, `sub=<user_id>`, scope=user
- **service token** — `aud=internal`, `sub=<service>`, scope=admin

Bugs:

- `aud` unchecked → service token replayed on the user API → admin.
- `sub` unchecked → swap `sub` in a service token to a user.
- The `iss` unchecked → a token from the *public* IdP replayed on the
  internal verifier.
- `scope`/`scp` unchecked → `scope:"*"` or `scope:"admin"` in the token.

## 5. The public endpoint that isn't

```python
@app.route('/api/v1/public/status')     # public
@app.route('/api/v1/public/users')      # public?!
@app.route('/api/v1/internal/users')    # internal — check?
@app.route('/api/v1/admin/flag')        # check?
```

The path *implies* the boundary — the code decides it. `/api/v1/public/`
prefix may be auto-mounted without auth while `/api/v1/internal/` has
it; the `/public/` subtree that shouldn't be public is the bug.

## 6. GraphQL-over-API

`POST /graphql` with `Authorization: Bearer <t>` — the token authenticates
the *request*, but resolver-level authz is a separate layer:

```graphql
query { user(id:"1") { notes { flag } } }   # object check?
mutation { updateUser(id:"1", role:"admin") } # field check?
```

See `web-graphql` — the auth-token bugs compound with resolver-miss bugs.

## 7. WebSocket auth

`wss://api/ws?token=<t>` or the `Sec-WebSocket-Protocol: bearer.<t>` or
a first-message `{"type":"auth","token":"<t>"}`:

- Token in URL → logged/referrer.
- `Origin` not checked → cross-site WS hijack (`web-websocket`).
- Auth checked on CONNECT but not per-message → the auth'd CONNECT opens
  a channel, later messages carry no check.
- Token never re-checked after connect → revoke doesn't close the socket.

## 8. gRPC / internal-RPC auth

`authorization: Bearer <t>` metadata — same JWT bugs plus:

- `x-google-iam-authorization-token` vs `authorization` — two headers,
  different checks.
- Method-level authz (`/service.Admin/Method` unchecked).
- `x-forwarded-*` trust on the service mesh — spoof `X-Forwarded-For:
  127.0.0.1` for "internal" routes.
- mTLS assumed → the network is the auth; reachable service = no auth.

## 9. The swagger/openapi leak

`GET /swagger.json` `/openapi.json` `/api-docs` `/redoc` `/docs`
`/api/schema` — enumerates *every* endpoint including the ones not
linked. The endpoint list is the authz map — grep for `security:` /
`x-roles` / `x-admin` fields that name the intended boundary, then test
each endpoint for whether the boundary exists.

## 10. The "internal" API key in the bundle

`bundle_miner.py` finds `process.env.API_KEY`, `REACT_APP_API_KEY`,
`VITE_API_KEY`, `NEXT_PUBLIC_API_KEY` in the shipped JS. A
`*_PUBLIC_*` key is supposed to be public — but some apps ship a
*private* key by accident. Test the key: does it open `/admin`? Does it
beat the login?

```bash
python3 tools/web/bundle_miner.py --url "$BASE/app.js" --out /tmp/bundle
grep -rn "API_KEY\|api_key\|apikey\|SECRET\|secret\|TOKEN\|token" /tmp/bundle
```

## 11. Falsifiers

- `401` without a valid token — auth required.
- `403` with a valid low-priv token — authz applied.
- The `aud`/`iss`/`scope` claims verified — cross-service replay dies.
- The API key is per-user and rotates — not a shared app key.
- The public endpoints return only public fields — no leak.
- The WS channel re-checks auth per message — revoked tokens die.
