# Case studies (deep) — the worked enumeration scenarios

## Case 1: the check-username one-shot

`GET /api/username-available?u=admin` → `{"available":false}`;
`?u=zzz-x` → `{"available":true}`. One request confirmed the direct
oracle. A 15-name seeded list → `admin`, `service`, `backup` confirmed.
`admin` took `admin:admin` → a session → the flag on the admin panel.
The whole exploit was the direct oracle + a default credential.

## Case 2: the uniform login, the timing gap

`POST /api/login` — `{"error":"invalid"}` 401 on both arms, identical
JSON. The text/status channels closed. But `admin` averaged 247ms,
`zzz` 8ms across 12 interleaved samples — the `bcrypt.verify` ran only
for a real user. The timing oracle confirmed `service`; the reset
endpoint's predictable token reset it → `web-auth-session`. The content
was equalized; the hash was not.

## Case 3: the register leaks what the login hid

`POST /login` fully uniform — text, status, timing, cookies all equal.
`POST /register` returned `"username already taken"` for `admin`. The
register oracle enumerated `admin`, `root`, `ci`. A password spray
(one common password, under the per-account lock of 5) → `ci:letmein`.
The hardened login did not protect the register — coverage, not
login-only.

## Case 4: the reset's hidden send

`POST /forgot-password` returned `"If that account exists, a reset
link was sent"` for both arms — a uniform response. But `admin`'s
response carried `{"emails_queued":1}` and `zzz`'s `0` — the send's
queue count was the oracle. A confirmed `admin` + a host-header
reset-poisoning → `web-host-header`. The uniform text hid a field.

## Case 5: the lockout as the oracle

After 6 bad attempts `admin` returned `423 "account locked"`; `zzz`
returned `"invalid"` at attempt 20. The lock only fires on a real row —
the lockout itself enumerated `admin`, `backup`, `deploy`. Record
`locks at 6 per-account` + the confirmed names; a per-account lock is
also a spray-under target (one password per account).

## Case 6: the GraphQL resolver

`query{userByEmail(email:"x@x.c"){id}}` → `{"data":{"userByEmail":null}}`
for fake, a real `{id:5}` for `admin@x.c`. The `login` mutation returned
`errors[].extensions.code:"USER_NOT_FOUND"` vs `"INVALID_CREDENTIALS"`.
Two resolvers, two oracles — the schema exposed both.

## The shared lesson

Every case is a channel the developer forgot to equalize. The honest
uniform message is rare; a residual — timing, a field, a send, a lock,
a second form, a resolver — almost always remains. The coverage pass
finds it; the login-only probe misses it.
