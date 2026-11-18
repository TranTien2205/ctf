# Verification surface — where the check happens and how to reach it

The verify call is the single line that decides everything. This file
maps where it lives and what reaches it.

---

## 1. The verifier types

| Type | Signature | The bypass |
|---|---|---|
| `jwt.decode(t)` no-verify | decode only | any claim |
| `jwt.decode(t, key)` HMAC | shared secret | weak key, alg=none |
| `jwt.decode(t, pubkey)` asymmetric | public verify | RS→HS confusion |
| `jwt.decode(t, keyfunc)` callback | dynamic key | `keyfunc` bug (kid/jku) |
| `jwt.verify(t, key)` | explicit verify | harder |
| `JWT.decode(t, key, true)` Ruby | third-arg verify | `false` skips |
| `Jwts.parser().parse()` Java | parser | `parseClaimsJws` vs `parse` |
| `jwt.Parse(t, keyfunc)` Go | callback | `keyfunc` nil for alg=none |
| `itsdangerous.loads()` | Flask | `secret_key` leak |
| `decrypt()`/`encrypt()` Laravel | `APP_KEY` | leak |
| `Marshal.load` + encrypt Rails | `secret_key_base` | leak |
| `securecookie.Decode` Go | hash/block keys | leak |
| `MachineKey.Unprotect` .NET | validationKey | leak |

## 2. The check's inputs — what reaches it

- The token from `Authorization: Bearer`/`Cookie`/`X-*`/query/body.
- The key from config/env/`kid`-lookup/`jku`-fetch/`x5u`-parse.
- The `alg` from the token header (or a pinned config).
- The claims from the decoded payload.

A forge wins when the verifier accepts — the signature matches the key
it used, OR the verifier skips the signature, OR the claims pass a
check the verifier doesn't actually enforce.

## 3. The algorithm-pinning question

Does the verifier pin `alg`, or take it from the header?

```python
# Pinned — confusion dead:
jwt.decode(t, pubkey, algorithms=['RS256'])
# Header — confusion live:
jwt.decode(t, pubkey, algorithms=header['alg'])
jwt.decode(t, pubkey)  # some libs default to header
```

The grep: `algorithms=` / `algorithm=` / `WithValidMethods` /
`valid_methods` / `allowed_algs`. If absent or header-derived →
confusion possible.

## 4. The keyfunc's bug

```go
// Go: keyfunc returning nil for alg=none → token accepted unsigned
keyfunc := func(t *jwt.Token) (interface{}, error) {
    if t.Method.Alg() == "none" { return nil, nil }
    return secret, nil
}
```

```python
# Python: keyfunc from kid lookup — traversal if not sanitized
def keyfunc(header):
    return open(f"/keys/{header['kid']}").read()
```

```javascript
// Node: jku fetch without whitelist
const keyfunc = (header, cb) => fetch(header.jku).then(...)
```

The `keyfunc`/`SigningKeyResolver`/`jwks_url` is where `kid`/`jku`/`x5u`
reach the key — a traversal or unwhitelisted fetch here is the forge.

## 5. The audience/issuer/subject checks

```
aud — who the token is for. Unchecked → cross-service replay.
iss — who minted it. Unchecked → any IdP's token.
sub — who it identifies. Unchecked → forge the user.
exp — expiry. Unchecked → old tokens live.
nbf — not-before. Unchecked → future tokens live.
iat — issued-at. Unchecked → can't detect staleness.
jti — token id. Unchecked → can't blocklist.
```

Each unchecked claim is a forge vector — `--claims` carries the
mismatch.

## 6. The signature-only verifier

Some verifiers check signature but NOT claims — a validly-signed token
with `role:admin` forged claims passes *if you can sign it*. The chain
is: get a signature on *any* claims (sign one yourself if you have the
key, or trick the issuer into signing your claims — e.g. a self-service
JWT issuer that signs whatever `sub` you post), then the verifier
accepts the forged claims.

## 7. The "the claim reaches a second check" shape

The first check is `signature`; the second is `role==='admin'` on the
claims. If the second is loose (`role==='admin' || role===1` —
numeric 1 passes), a forged `role:1` passes both. The strictness of the
*claim check* is as important as the signature.

## 8. The cache-of-trust

A session store caches `user_id → session` — a token verified once is
cached. A forged token's *first* verification may be the only check;
a replayed cache-hit skips re-verification. The forge needs one valid
first-verify (a stolen token, or the forge itself if the check is
racy).

## 9. The middleware-order verifier

The auth middleware runs `before` the route — but only on the routes
mounted after it. `app.use(auth)` after `app.get('/admin')` → `/admin`
is checked, `/api/admin` (mounted before) is not. The grep: middleware
`app.use`/`before_action`/`@app.before_request` position vs route
registration order.

## 10. The "which layer verifies" question

- WAF verifies → app trusts. WAF can be bypassed (path differential,
  header confusion) while app sees the "verified" request.
- App verifies → real check. The forge must beat the app's verifier.
- Both verify → the forge must beat both, or bypass the WAF's check
  to reach the app's.

## 11. The verify-timing gap

A token is verified at login, then the *claims* are cached for the
session duration — a claim-change mid-session isn't re-verified. Forge
by changing the claim between verifications (update the stored role,
not the token).

## 12. The multi-issuer confusion

`iss` unchecked → a token minted by the *public* IdP (Google, Auth0)
replays on the *internal* verifier that trusts the same key but a
different `iss`. Or a token for client A replays at client B (`aud`
unchecked).

## 13. The self-issued token

`POST /token {sub:"admin", secret:"guessable"}` — if the issuer accepts
anyone's claims and signs them (the issuer is a public service), the
signed token replays on the verifier. The issuer is the forge.

## 14. The "the signature IS the flag" edge

Some CTF challenges give a token whose *signature* is the flag — verify
it with the right key and the signature *is* the answer. `session_dissect`
reveals it.

## 15. The verification-map output

For every protected endpoint, record:

- Which verifier runs (signature-only, claims-check, middleware-order).
- Where the key comes from (config, kid, jku, leak).
- Which claims are checked (sub, role, aud, iss, exp, nbf, iat, jti).
- Whether `alg` is pinned or header-derived.
- Whether the check is first-order (the request) or second-order (the
  stored session).

The map is the attack surface — the forge targets the weakest check
in the chain.
