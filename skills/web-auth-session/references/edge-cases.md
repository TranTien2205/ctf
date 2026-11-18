# Edge cases — the corners where the standard check misses

The shapes that don't fit the checklist — one-off mechanisms, exotic
carriers, and the cases that need a custom probe.

---

## 1. The unsigned-but-required claim

A token's signature is verified but the verifier reads a claim the
*signer* never signed — a claim added by an upstream proxy. If the
proxy adds `X-User` based on a *different* token, the verifier trusts
the proxy's claim — a header-confusion second-order.

## 2. The dual-carrier session

The session exists in BOTH `Cookie` and `Authorization` — the
middleware checks `Cookie` (with SameSite), the API checks
`Authorization` (without). A `Bearer` replay bypasses the SameSite that
was supposed to protect the cookie path.

## 3. The cookie-encryption downgrade

A cookie is encrypted (Fernet, Laravel) — the verifier decrypts then
*decodes* the inner value without re-checking integrity. Forge the
inner value if the encryption's integrity check is bypassable, or
downgrade to a weaker inner format.

## 4. The `exp`/`nbf` race

A token with `exp == now` — the verifier's clock and yours differ by
seconds. Replay it in the gap where it's still valid on the server but
you computed it expired.

## 5. The token-type confusion

`refresh_token` replayed as `access_token` — different expiry, different
scope. If the verifier doesn't check `typ`/`token_use`, the refresh
token's longer life is the attack window.

## 6. The cross-realm token

`realm_access.roles` in Keycloak — a token from realm A replayed at
realm B where the role names collide. `realm` unchecked → cross-realm.

## 7. The nested JWT

`token` claim containing another JWT — the outer is verified, the inner
isn't (or vice versa). Forge the unverified layer.

## 8. The detached-signature JWS

`header.payload.` with `{"b64":false,"crit":["b64"]}` — the payload is
detached and sent elsewhere. The verifier may accept the detached form
with a manipulated payload.

## 9. The JWE-as-JWS confusion

A JWE (encrypted) token replayed where JWS (signed) is expected — or
the reverse. The `alg`/`enc` header confusion.

## 10. The `crit` header exploitation

`{"crit":["exp"],"exp":"ignored"}` — a `crit` extension that redefines
claim handling. If the verifier honors `crit` blindly, the claim
semantics change.

## 11. The `zip` compression oracle

`{"zip":"DEF"}` — the payload is deflated. A decompression bomb or a
zip-slip in the verifier's inflater.

## 12. The `x5c`/`x5t` certificate confusion

`x5c`/`x5t`/`x5u` headers carry or point to the cert — if the verifier
trusts the embedded cert for verification, a self-signed cert you
control signs the token.

## 13. The `cty`/`typ` downgrade

`typ:"JWT"` vs `cty:"JWT"` — a verifier checking one, an issuer setting
the other. The token passes a check it shouldn't.

## 14. The `aud` array-vs-string confusion

`aud:"target"` vs `aud:["target","admin"]` — a verifier doing
`aud === "target"` fails the array; one doing `aud.includes("admin")`
accepts the array. The claim's shape is the confusion.

## 15. The `sub` numeric-vs-string

`sub:1` vs `sub:"1"` — a verifier doing `sub == 1` loose-compares both;
a `sub === "1"` strict check needs the string. The type is the
confusion.

## 16. The claim-order exploitation

Duplicate JSON keys `{"role":"user","role":"admin"}` — a parser that
takes first vs last. The issuer's parser and the verifier's parser may
disagree — a key-order parser differential.

## 17. The unicode claim collision

`sub:"admin"` vs `sub:"\u0430dmin"` (Cyrillic a, U+0430) — visually identical, a
canonicalization-missing verifier sees them as different users. Or a
Unicode-aware check that normalizes — the homoglyph is the collision.

## 18. The null-byte claim

`sub:"admin\u0000"` — a C-string truncation makes the verifier see
`admin` where the length-aware store sees `admin\0`. The truncation is
the collision.

## 19. The whitespace claim

`sub:" admin"`/`sub:"admin "`/`sub:"admin\n"` — a `trim()`-missing
verifier sees them as `admin`. Or a `trim()`-present verifier sees
them as different.

## 20. The case claim

`sub:"ADMIN"`/`sub:"Admin"`/`sub:"aDmIn"` — a `toLowerCase()`-missing
verifier sees them as different; a `strcasecmp` sees them as same.

## 21. The array-index claim

`role:["user","admin"]` — a `role[0]==='admin'` check reads [0]; a
`role.includes('admin')` reads any. The index-access is the confusion.

## 22. The object-shape claim

`role:{name:"admin"}` vs `role:"admin"` — a `role==='admin'` check
fails the object; a `role.name==='admin'` check passes it.

## 23. The missing-claim default

No `role` claim → the verifier defaults `role="user"` — or crashes into
a permissive error path. The absent-claim default is the edge.

## 24. The extra-claim overflow

`{"role":"user", ...200 more claims..., "isAdmin":true}` — a verifier
that stops reading after N claims misses the buried `isAdmin`.

## 25. The claim-injection via issuer

`POST /token {sub:"admin"}` — the issuer signs whatever `sub` you post
(self-service). The signed token is a valid signature on forged claims.

## 26. The replay-across-environment

A token minted in `dev`/`staging`/`test` replays on `prod` — same key,
different env. The `iss`/`aud` env-tag unchecked.

## 27. The pre-rotation token

A token signed before the key rotation — the old key still verifies.
The verifier's key-rotation grace period is the window.

## 28. The introspection-vs-stateless

The verifier checks `token.active` via introspection — a stateless JWT
with `active:true` forged in claims bypasses the introspection if the
verifier reads the claim instead of calling the introspection endpoint.

## 29. The `azp`/`client_id` swap

`azp:"client-A"` vs `client_id:"client-A"` — a verifier checking one
field while the issuer sets the other. The field-name confusion.

## 30. The `at_hash`/`c_hash` skip

`at_hash`/`c_hash` not verified — a swapped `access_token`/`code` is
bound to the wrong `id_token`.

## 31. The `nonce` replay

`nonce` unchecked → an `id_token` replayed in a different flow.

## 32. The `auth_time` backdate

`auth_time` unchecked → an `id_token` claiming an ancient login is
accepted as fresh.

## 33. The `acr`/`amr` claim-false

`amr:["mfa"]` forged in a token where the verifier trusts the claim —
the MFA it never happened is claimed.

## 34. The token-binding miss

`cnf`/`x5t#S256`/`DPoP` binding absent — a stolen token replays from
any client (no sender-constraining).

## 35. The `session_state`/`sid` confusion

`sid`/`session_state` in the `id_token` vs the cookie session — the
two session ids aren't checked for binding.

## 36. The "the token is the session" dual-role

The JWT IS the session — destroying the server-side session doesn't
revoke the JWT (stateless). The JWT replays until `exp`.

## 37. The "the session is the token" inverse

The session id IS a JWT — the server stores it, and the JWT's claims
are the session data. Modifying claims without a key doesn't work, but
the *stored* session is server-side — the JWT is a key into the store,
not the store itself.

## 38. The dual-verifier gap

The WAF verifies `signature`; the app verifies `claims`. The WAF's
verify is on a different token-format than the app's — a token that
passes the WAF's format-check fails the app's claim-check, or vice
versa. The gap is between the two verifiers' assumptions.

## 39. The "no verify needed" path

`/health`/`/status`/`/metrics`/`/public/*` — endpoints mounted outside
the auth middleware. The flag may be on a "public" route that leaks it,
or the auth middleware's coverage is incomplete.

## 40. The wildcard-route escape

`app.use('/api/*', auth)` — a route that doesn't match `/api/*` (e.g.
`/API` or `/api`) escapes the auth middleware. The wildcard's shape is
the gap.
