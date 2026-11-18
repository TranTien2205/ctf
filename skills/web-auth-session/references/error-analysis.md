# Error analysis — reading the response to route the next probe

The `errors` array, the status code, and the `WWW-Authenticate` header
are the routing surface. This file maps what you got → what to try next.

---

## 1. The status-code map

| Status | Meaning for auth | Next probe |
|---|---|---|
| `200` with data | endpoint reachable, token honored | verify the *role* — is this the user or the admin view? |
| `200` `{"user":null}` | endpoint exists, token valid, no authz applied | try `?id=2` / swap claims |
| `301`/`302` → `/login` | auth required, redirecting | you're unauthenticated — get a token first |
| `302` → `/admin` | you're being bounced somewhere | follow it; the target may not re-check |
| `400` `"invalid token"` | the JWT parse failed | check you sent the full `a.b.c`, no whitespace |
| `400` `"signature invalid"` | verification ran and failed | your secret/key is wrong — iterate secrets |
| `400` `"token expired"` | `exp` checked | replay a fresh token or forge `exp` |
| `400` `"audience invalid"` | `aud` checked | forge `{"aud":"<expected>"}` |
| `400` `"issuer invalid"` | `iss` checked | forge `{"iss":"<expected>"}` |
| `400` `"unknown kid"` | `kid` lookup ran but not found | your `kid` traversal path doesn't exist |
| `400` `"jku fetch failed"` | the JWKS fetch was attempted | your URL unreachable / filtered — try same-host |
| `401` generic, no body | authn failed, reason hidden | try the mechanism variants (none/kid/jku) one at a time |
| `403` `"forbidden"` | authenticated, but not authorized | you ARE logged in — escalate the claim, not the token |
| `403` `"insufficient_scope"` | OAuth scope | re-request with `scope=admin` etc. |
| `404` | wrong path | find the real endpoint (bundle, swagger, OPTIONS) |
| `405` | wrong method | try GET vs POST; some verify paths are method-gated |
| `429` | rate limited | slow down; lockout may be per-account — switch account |
| `500` + stack trace | server error | the stack often names the library+version — use it |
| `503` | proxy/upstream | retry; if persistent, the service is down — not auth |

## 2. The JWT-rejection body — which check failed

| Error text | Means | Fix |
|---|---|---|
| `"Signature verification failed"` | HMAC/RSA sig wrong | wrong secret / wrong pubkey bytes |
| `"The token is not yet valid"` | `nbf` in future | forge `nbf:0` |
| `"The token has expired"` | `exp` past | forge `exp` or replay fresh |
| `"Invalid audience"` | `aud` mismatched | forge `aud` to the API's name |
| `"Invalid issuer"` | `iss` mismatched | forge `iss` |
| `"Key ID not found"` / `"unknown kid"` | `kid` lookup ran | traversal path doesn't exist; try absolute `/dev/null` |
| `"JWKS fetch failed"` / `"jku error"` | `jku` fetch attempted | the server can't reach your host or filters it |
| `"Algorithm not allowed"` | `alg` not in allowlist | alg confusion dead — pivot |
| `"Token is malformed"` | parse failed | check b64 padding, header is valid JSON |
| `"Missing required claim"` | claim absent | add `sub`, `exp`, `iat`, `iss`, `aud`, `jti` |
| `"The 'sub' claim is required"` | `sub` missing | add it |
| `"Token revoked"` / `"jti already used"` | `jti` check | fresh `jti` each forge; can't replay |

## 3. Session rejection patterns

| Pattern | Means |
|---|---|
| 302 → `/login` with no other clue | you're anonymous — get a session |
| `{"error":"session expired"}` | server-side expiry; re-login |
| `{"error":"invalid session"}` | the sid doesn't resolve — wrong id, deleted, or IP-bound |
| `{"error":"session mismatch"}` | binding check failed (IP/UA/user-agent) |
| empty `Set-Cookie` on login | the app didn't issue one — check the body for a token to store yourself |

## 4. WWW-Authenticate — the scheme announcement

```
WWW-Authenticate: Basic realm="admin"
WWW-Authenticate: Bearer realm="api", error="invalid_token", error_description="..."
WWW-Authenticate: Bearer error="insufficient_scope", scope="admin"
WWW-Authenticate: Digest realm="x", nonce="...", algorithm=MD5, qop="auth"
```

The `error_description` is free text — it often names exactly what was
wrong (`"token expired"`, `"signature invalid"`).

## 5. The shape that means "you're in but not authorized"

`403` after a valid login is **the most informative response in the
class** — it says:

- The token verified. Don't touch the crypto.
- The user is *recognized* but lacks privilege.
- The next probe escalates the *claim*, not the token: forge
  `{"role":"admin"}`, swap `user_id`, hit a mass-assign endpoint, or
  find an endpoint that checks path-prefix only.

The opposite — `401` with a valid token — means the verify itself failed:
read the body/`WWW-Authenticate` for which check rejected it.

## 6. The error-is-the-oracle shapes

- **`user not found` vs `wrong password`** — username enum (→ web-user-enum).
- **Different timing** between user-exists and user-absent login →
  timing oracle.
- **Different headers** on success vs fail — `X-Authenticated: true` on
  one path only.
- **Different session id issued** on failed vs succeeded login — a
  "pre-session" vs "post-session" split can leak the valid-user oracle.

## 7. Stack-trace mining

A `500` stack trace in the response is a free fingerprint:

```python
Traceback (most recent call last):
  File ".../site-packages/jwt/api_jwt.py", line 88, in decode
File ".../site-packages/jwt/algorithms.py", line 234, in verify
jwt.exceptions.InvalidSignatureError
```

→ `pyjwt` version pinned; its `verify_signature` semantics are known —
alg confusion vs `options` bugs decided by which `decode` overload appears
in the trace.

## 8. The empty-body 401

When the server returns `401` with **no body and no `WWW-Authenticate`**,
the mechanism check happens in middleware *before* the handler — the
reason is in the server log you can't see. In that case, bisect the
mechanism: alg=none → kid → jku → secret — one probe each, record the
silence as "no new signal" per the ledger.
