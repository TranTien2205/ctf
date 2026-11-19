# Form surface (deep) — the full endpoint inventory

## The complete account-touching surface

### Auth-forms
`/login` `/signin` `/sign-in` `/auth` `/authenticate` `/session`
`/logon` `/connect` `/enter` `/access`

### Registration
`/register` `/signup` `/sign-up` `/create-account` `/join` `/enroll`
`/new-account` `/api/register` `/api/signup`

### Reset/recovery
`/forgot-password` `/reset` `/password-reset` `/recover` `/recovery`
`/reset-password` `/api/forgot` `/api/reset` `/forgot`
`/forgot-username` `/username-reminder` `/recover-username`

### Existence-checks (the direct oracles)
`/check-username` `/check_email` `/username-available` `/available`
`/user-exists` `/exists` `/taken` `/validate-username` `/check-user`
`/api/username-available` `/api/v1/check` `/api/users/check`

### Account-state
`/unlock` `/reactivate` `/enable` `/activate` `/confirm` `/verify-email`
`/resend-verification` `/invite-accept`

### MFA/OTP
`/mfa` `/2fa` `/otp` `/send-otp` `/verify-otp` `/totp` `/verify-code`
`/api/mfa` `/api/2fa` `/api/otp`

### Invite/contact
`/invite` `/invite-user` `/contact` `/refer` `/referral` `/request-access`
`/waitlist` `/beta-signup`

### API auth
`/api/login` `/api/auth` `/api/signin` `/api/token` `/api/session`
`/oauth/token` `/oauth/authorize` `/jwt` `/api/v1/login` `/api/v2/login`

### User resources
`/api/users` `/api/users/{id}` `/users/{id}` `/user/{name}` `/u/{name}`
`/api/user/{email}` `/profile/{name}` `/members/{name}` `/author/{name}`
`/?author=N` `/wp-json/wp/v2/users`

### GraphQL
`POST /graphql` — `query{userByEmail}` `query{checkUser}`
`query{userExists}` `query{user}` `mutation{login}` `mutation{signup}`
`mutation{requestPasswordReset}` `mutation{verifyUser}`

### SSO/federated
`/oauth/authorize` `Sign in with X` `/saml/login` `/sso` `/oidc`
`/auth/google` `/auth/github` `/auth/microsoft`

## The alias rule

The same logic under many routes — `/login`, `/login/`, `/api/login`,
`/api/v1/login`, `/auth`, `/signin`, `/session` — probe each alias; a
limiter/oracle may exist on one route but not another.

## The hidden-endpoint rule

The direct-oracle endpoint (`check-username`) is usually an AJAX call
the register page makes — grep the bundle (`web-source-map`) for
`check|available|exists|username` to find it; it is not a visible link.
