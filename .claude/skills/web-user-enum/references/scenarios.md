# Scenarios — the target-and-oracle pairings

## Scenario: a fresh CTF web app

An app with a login + register + reset + a JS bundle.
1. `web-source-map` → the bundle names `/api/check-username` — a direct
   oracle in one request
2. `enum_probe` on `/login` → a timing gap (bcrypt)
3. the register's `"taken"` → a second oracle
4. a 15-name seeded list → `admin`, `service` confirmed
5. `admin:admin` → a session → `web-auth-session`

## Scenario: a SPA + JSON API + no obvious oracle

A React app posting to `/api/login` — identical `{"error":"invalid"}`.
1. the masked JSON diff → `{"code":1001}` vs `{"code":1002}` — a code
   oracle the UI hides
2. or the timing baseline → a bcrypt gap
3. a confirmed `admin` → a weak password / the reset flow

## Scenario: a hardened enterprise app

A SSO/SAML front + a local login + heavy rate limiting.
1. the SAML `user@external` vs `user@local` redirect → the directory
   oracle
2. a `X-Forwarded-For` spoof → the per-IP throttle bypassed
3. a confirmed `admin` + a credential spray under the bypassed limit
   → `web-auth-session`

## Scenario: a REST API with a users resource

`GET /api/users/{id}` — `200` for a real id, `404` for a fake.
1. the `200`/`404` → a direct existence oracle + `web-idor`
2. an `id`/`name` sweep → the account list
3. a confirmed `admin` id → the admin's object + the role escalation

## Scenario: a GraphQL backend

`POST /graphql` — a `checkUser`/`userByEmail`/`login` resolver.
1. `userByEmail` `null` vs `{id}` → direct oracle
2. `login` typed error `"USER_NOT_FOUND"` vs `"INVALID_CREDENTIALS"`
3. a confirmed account → `web-graphql`/`web-auth-session`

## Scenario: a fully-hardened app

Every channel uniform on every form — the honest defense.
1. the variance read → a fixed dummy-hash's lower stdev
2. the send side-effect on reset → the queue count
3. a second form → check-username/register still leaks
4. or a real, all-uniform negative — record + move to `web-auth-session`

## The scenario rule

Every scenario starts at the DIRECT oracle (cheapest), falls to the
per-form channels, ends at the throttle + the bounded list. The enum
is the measurement; the route is the neighbor class.
