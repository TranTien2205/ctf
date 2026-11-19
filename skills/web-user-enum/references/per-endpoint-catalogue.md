# Per-endpoint catalogue — every endpoint's full protocol

## `/login` — the headline form

- setup: the CSRF token + a fresh session jar
- channels: body (masked diff) → status+`Location` → timing (N>=8) →
  side (`-sv` + the lock)
- the common leaks: `"no such"`/`code`, `?e=` param, bcrypt gap,
  `attempts_remaining`, `423` on a real row
- `login-enum.md`/`login-enum-deep.md`

## `/register`/`/signup` — the built-to-reveal

- probe: `user=$KNOWN` vs `user=$FAKE` — `"taken"`/`409`/`{"exists"}`
- the AJAX check the page makes — `/check-username`/`/available`
- which field leaks — username OR email OR both
- a timing gap — the `unique`-constraint check
- `register-reset-enum.md`/`register-reset-enum-deep.md`

## `/forgot-password`/`/reset` — the send-side

- probe: `email=$KNOWN` vs `email=$FAKE`
- `"no account"`/`{"emails_queued":1}`/a `302 /check-email`/a timing gap
- the send itself — does YOUR email get the link?
- a `forgot-username` variant — `"we emailed your username"`
- `register-reset-enum.md`

## `/check-username`/`/available`/`/exists`/`/taken`/`/user-exists`

- the direct oracle — `GET ?u=$U` → `{"available":bool}`/`{"exists":bool}`
- the cheapest confirmation — one request, no baseline
- found via the bundle (`bundle_miner`/`web-source-map`)
- `api-enum.md`/`form-surface-deep.md`

## `/unlock`/`/reactivate`/`/activate`/`/confirm`

- `user=$KNOWN` vs `$FAKE` — `"unlocked"`/`"no locked account"`
- an account-state + exists oracle
- `edge-cases-deep.md`/`edge-cases-map.md`

## `/mfa`/`/2fa`/`/otp`/`/send-otp`/`/verify-otp`

- `user=$KNOWN` vs `$FAKE` — does the OTP send fire only for real?
- `"user not found"`/`{"otp_sent":bool}`/the send itself
- an `otp`-rate-limit — the send is a stronger throttle signal
- `channel-side.md`

## `/invite`/`/invite-user`/`/contact`/`/waitlist`

- `email=$KNOWN` vs `$FAKE` — `"already invited"`/`"already registered"`
- an email-exists oracle in the invite flow
- `edge-cases-deep.md`

## `/api/login`/`/api/auth`/`/oauth/token` — the JSON auth

- `{"username":"$U","password":"x"}` — the typed error/`code`/`reason`
- `invalid_grant` vs `invalid_client`/`error_description`
- the JSON-field hunt: `error_code`/`reason`/`attempts`/`exists`
- `api-enum.md`/`api-enum-deep.md`

## `/api/users/{id|name}`/`/users/{name}`/`/?author=N` — REST resources

- `GET /api/users/$U` — `200`/`404` (enum) + the object (`web-idor`)
- `?author=N` → `/author/<name>` — the WP redirect
- `/wp-json/wp/v2/users` — a public list
- `api-enum.md`

## `/graphql` — the resolvers

- `query{userByEmail}`/`checkUser`/`userExists` → `null`/`{id}`/`bool`
- `mutation{login}` → `errors[].code` `"USER_NOT_FOUND"`/`"INVALID"`
- `mutation{requestPasswordReset}` → the send-side
- introspection reveals the resolvers
- `api-enum-deep.md`

## `/sso`/`/saml`/`/oauth/authorize` — federated

- `login_hint`/`email` → IdP-redirect (federated) / local-redirect /
  `account_not_found` — a two-bit oracle
- `sso-and-federated.md`

## The endpoint rule

Every endpoint is a FORM — a separate cell in the coverage matrix.
Probe each on its live channels; an endpoint the inventory missed is a
cell that stays `unmeasured`. `form-surface-deep.md` is the full list.
