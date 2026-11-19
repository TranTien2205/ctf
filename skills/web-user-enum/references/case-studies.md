# Case studies — the enumeration shapes, narrated

## Case 1: the honest error

`POST /login` — `admin` returns `"Wrong password"`, `zzz` returns `"No
account named zzz"`. The text is the oracle. A bounded name list →
`admin`, `service`, `backup` confirmed → `admin` takes `admin:admin` →
a session → `web-auth-session` for the post-login step. The enum was
link 1.

## Case 2: the uniform text, the bcrypt gap

`POST /api/login` — both arms return `{"error":"invalid"}` 200. But
`admin` averages 240ms, `zzz` 8ms across 12 interleaved samples —
`bcrypt.verify` runs only for a real user. The timing oracle confirms
`service` exists → the reset endpoint resets it (a predictable token) →
`web-auth-session`. The text was equalized; the hash was not.

## Case 3: the register leaks what login hid

`POST /login` is fully uniform — text, status, timing all equalized.
But `POST /register` returns `"username already taken"` for `admin`.
The register oracle enumerates `admin`, `root`, `ci` → a password spray
(one common password, under the per-account lock) → `ci:letmein` → a
service session. Coverage, not login-only, found it.

## Case 4: the check-username direct oracle

`GET /api/username-available?u=admin` → `{"available":false}` — a direct
exists-oracle, no credential, no throttle. One request per name → the
full account list → the spray/reset chain. The cheapest oracle when it
exists.

## Case 5: the reset's send side-effect

`POST /forgot-password` returns `"If that account exists…"` for both
arms — a uniform response. But `admin`'s email gets the reset link and
a random address does not — confirmed via the response's
`{"emails_queued":1}` vs `0`. The side effect is the oracle.

## Case 6: the lockout as the oracle

After 6 bad attempts, `admin` returns `423 "account locked"`; `zzz`
keeps returning `"invalid"` at 20. The lock only fires on a real row —
the lockout itself enumerates `admin`. Record `locks at 6 per-account`
+ `admin confirmed via lockout`.

## The pattern

Every case is: a channel the developer forgot to equalize. The honest
uniform-error is rare; a residual channel (timing, a cookie, a second
form, a side-effect, a lockout) almost always remains.
