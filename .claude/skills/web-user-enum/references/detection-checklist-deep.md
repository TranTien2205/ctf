# Detection checklist (deep) — the exhaustive entry list

## The surface inventory — every endpoint

- [ ] `/login` `/signin` `/auth` `/session` — every login alias
- [ ] `/register` `/signup` `/create-account`
- [ ] `/forgot-password` `/reset` `/password-reset`
- [ ] `/forgot-username` `/username-reminder`
- [ ] `/unlock` `/reactivate` `/enable`
- [ ] `/check-username` `/available` `/username-available` `/user-exists` `/check-email` `/validate-username` `/api/v1/users/check`
- [ ] `/mfa` `/2fa` `/otp` `/send-otp` `/verify`
- [ ] `/invite` `/contact` `/refer` `/request-access`
- [ ] `/api/login` `/api/auth` `/api/token` `/oauth/token` `/jwt`
- [ ] `/api/users/{id|name|email}` `/users/{id}` `/user/{name}`
- [ ] `/graphql` — introspect for `checkUser`/`userByEmail`/`userExists`/`login`
- [ ] SSO/SAML — `/oauth/authorize`, a `Sign in with X` flow
- [ ] a `ws://`/`wss://` auth channel
- [ ] a `Basic`/`Authorization` realm

## The known-good

- [ ] your own account registered → guaranteed known-good
- [ ] a seeded name listed: `admin`/`root`/challenge-named/app-leaked
- [ ] TWO different provably-fake names prepared (`zzz-`, `qqq-`)
- [ ] the format resolved — `admin` vs `admin@x.c` vs `corp\admin`

## The first probes — cheapest first

- [ ] the direct oracle: `GET /check-username?u=` / `/available?u=` / `?email=`
- [ ] the register-taken check
- [ ] the login 3-request pair
- [ ] the reset send-side check
- [ ] the API/GraphQL exists-check
- [ ] the REST `200`/`404` check

## The noise + format

- [ ] `bad1` vs `bad2` — per-request noise identified and masked
- [ ] CSRF handled — fresh token per request if required
- [ ] session affinity for a comparable timing read
- [ ] a cache-bust param for a cached response

## The detection record

- [ ] per-endpoint: `oracle` (channel+delta) / `uniform` / `no-endpoint`
- [ ] the cheapest-leak oracle identified
- [ ] the confusable boundary checked — auth-session/logic/sqli/idor/oauth
- [ ] a coverage matrix — no (form × channel) cell left unmeasured
