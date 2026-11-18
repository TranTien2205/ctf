# Common mistakes — the failure modes

Thirty ways to burn the probe budget without learning anything.

---

## 1. Decoding is not verifying

`jwt.decode(token)` returns the claims for **any** bytes — seeing
`{"role":"user"}` doesn't mean the signature is checked. Sending the
same token back unchanged and calling it "verified" is the most common
false positive. The test is always: forge a *different* claim set and
check acceptance.

## 2. `alg=none` on the wrong endpoint

Testing `/api/me` (unauthenticated or loosely checked) with the forged
token proves nothing — the endpoint may not verify at all. Replay
against the endpoint that *rejects the original token's scope* (e.g.,
`/admin`, `/api/admin/users`).

## 3. `role:admin` in the body, confirmed by `200`

Mass-assign only counts if the role field lands on the model AND an
authz check reads it. Register with `{"role":"admin"}`, then **read**
`/api/me` and hit `/admin` — the `200` on register alone proves nothing.

## 4. "The cookie didn't have `Secure`" as the finding

Missing flags are surface signals — they feed other classes. A
`SameSite=None` cookie is *CSRF-relevant*, not an auth bypass on its own.

## 5. Fixation probe on your own browser

Setting `document.cookie="sid=EVIL"` in your own session then logging in
yourself proves the *server* accepted a fixed id — but doesn't prove
persistence after login. You must check whether the login rotated the
id.

## 6. Testing `redirect_uri` only on `/authorize`

The strict check might be at `/authorize` but the *callback* endpoint
accepts any `redirect_uri` when exchanging `code` → `token`. Try both
sides of the flow.

## 7. `state` "validated" means compared to itself

`state` echoed back is not validated — the check must be against a
server-side or signed value minted at `/authorize` time. Sending
`state=whatever` and seeing `state=whatever` back proves nothing.

## 8. Replay of an expired token as "exp bypass"

An expired token that still authenticates is a real bug. But "I sent
`exp:1970` in the forged token" is not — the forged token doesn't prove
the *signature path* is broken, just that you can sign.

## 9. Confusing "session cookie" with "session id"

Flask's `session` cookie is a *signed blob* containing the session data;
the attack is forge-the-blob (weak `SECRET_KEY`), not guess-the-id.
Django's `sessionid` is a *lookup key* into the server-side store; the
attack is guess/fixate the id. Same field name, different bug class.

## 10. Trying `kid=/dev/null` without checking `kid` is read

`kid` only reaches a key-lookup if the verifier honors it — many
libraries ignore `kid` entirely or use it only as a label. Check the
verify path in source first.

## 11. `jku` pointing at your host without checking the fetch

Some servers fetch `jku` once at startup, cache it, or pin the URL. If
your JWKS request never hits your host (check your access log), the
field isn't honored — pivot.

## 12. Brute-forcing a session id without bounding the space

A 128-bit id is not brute-forceable. Check entropy **first** — `id_sweep`
is for 32-64-bit numeric ranges and sequential ids, not random tokens.

## 13. `SameSite=None` on a cookie that needs `Secure`

Modern browsers **reject** `SameSite=None` without `Secure` — the
cookie never lands, so the "missing flag" is actually the browser
protecting the user. Confirm the cookie actually reaches the target.

## 14. Logout "doesn't work" because you replayed the pre-logout token

The fix for session fixation is rotate-on-login; if the app rotated
the id at login, your planted id is dead. Replay the *post-login* id
to test logout.

## 15. `Authorization: Bearer` in a Cookie-shaped test

Don't send `Authorization` when the app reads `Cookie`, or vice versa.
Check which carrier the endpoint expects by testing with a known-good
token in each.

## 16. Reset token "not bound" tested against your own account

Bind-check: use YOUR token to reset the VICTIM's password — swapping
token-and-same-email always works and proves nothing.

## 17. MFA skip tested on an endpoint that doesn't need MFA

`/api/me` might not be MFA-gated even though `/admin` is. Test the skip
on the endpoint that *requires* the completed flow.

## 18. Assuming the response status is the verdict

`200` on register ≠ role assigned; `302` on logout ≠ session killed;
`204` on reset ≠ password changed. Always verify the *effect* —
`/api/me`, a fresh login, the data itself.

## 19. Testing `state` with a valid state

If `state` was required at `/authorize`, sending `state=valid` to
`/callback` proves it was *expected* — not that it was *checked*. Send
`state=` (empty), `state=0`, `state=invalid`, `state=<attacker's>`.

## 20. A forged token rejected for a *different* reason

`401` can mean "sig invalid" OR "expired" OR "user not found" OR "aud
mismatch" — read the `errors[].message` or response body to know which.
A `kid` traversal fail looks identical to an expired token if you don't
read the reason.

## 21. `session_dissect` output treated as proof

The tool *names* the weakness; it does not exploit it. `weakness:
weak-signing-key` is a lead, not a verdict — you still need the forged
token accepted.

## 22. jwt_forge with claims in the wrong layer

`--claims '{"user.role":"admin"}'` writes a top-level key literally
named `user.role`, not `{"user":{"role":"admin"}}`. Nested claims need
real JSON nesting.

## 23. Not recording the falsifier

"Verify call pinned to EdDSA only" is a *result* — record `refutes`
so `decide.py` routes elsewhere. An unrecorded falsifier is a re-run
waiting to happen.

## 24. Sweeping `/admin/*` without the admin token

The admin surface is protected — after forging, replay it *with* the
forged token. Without it you're enumerating 401s.

## 25. Trusting the two-account diff without a third

`tokenA` vs `tokenB` differing in a suffix suggests sequential ids —
confirm with a third account before claiming predictability.

## 26. `Basic` auth tried only with `admin:admin`

Weak passwords go through `wordlists.md` too — `admin:password`,
`admin:123456`, `root:root`, `test:test` are in §1.

## 27. Not checking the token lands in `Set-Cookie` for GET too

A reset/magic-link token set as a cookie on the *GET* response (not just
the POST) means it leaks via Referer on any external subresource.

## 28. `jku` URL filtered but the filter is `contains("target.tld")`

`https://target.tld.attacker.tld/jwks.json` passes a naive `in` check —
try the host-suffix and `@`-userinfo tricks before declaring `jku` dead.

## 29. Stopping at the forged token

The token is the *primitive*. The flag is usually on `/admin` or inside
the admin's profile — one more step after the forge.

## 30. Verifying by reading the token back

`GET /api/me` with the forged token returning the claims you forged is
**circular** — the endpoint may just echo the token's contents. Confirm
against something the token *authorizes*: an admin listing, another
user's data, the flag field.
