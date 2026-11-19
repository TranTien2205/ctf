# Detection signals — the raw observable, classified

## Text-class signals — the body

| The observed bytes | Signal | Channel |
|---|---|---|
| `"no such user"` / `"user not found"` | honest-error | body/text |
| `"wrong password"` for a real user | wrong-pw | body/text |
| `"invalid credentials"` (uniform) | equalized — hunt residual | body |
| `error_code=1001` vs `1002` | code-residual | body/code |
| `class="err-user"` vs `"err-pass"` | class-residual | body/residual |
| `data-reason="user"` vs `"pass"` | data-residual | body/residual |
| `<input type=hidden name=reason value=no_user>` | hidden-residual | body/residual |
| `<!-- user lookup failed -->` | comment-residual | body/residual |
| `"account is locked"`/`"pending"`/`"disabled"` | state-message | body/state |
| `"username already taken"`/`"email registered"` | register-taken | register |

## Status/redirect-class signals

| The observed | Signal |
|---|---|
| `Location: ?e=1` vs `?e=2` | redirect-param |
| `Location: ?error=user` vs `?error=pass` | redirect-param |
| `404` vs `401`/`200` | status-code |
| `302 /check-email` only on real | reset-redirect |
| `302 /author/<name>` on `?author=N` | WP-redirect |
| `302` to IdP vs local-login | federated |

## Envelope-class signals

| The observed | Signal |
|---|---|
| `Set-Cookie: auth_attempt=`/`error=`/`last_user=` | cookie-artifact |
| `X-Auth-Reason`/`X-Error-Code`/`X-User-Exists` | header-artifact |
| `attempts_remaining`/`emails_sent`/`user_exists` field | json-field |
| `{"error":"user_not_found"}`/`{"reason":"..."}` | json-error |
| a send (email/OTP) that fires only for real | send-side |
| `Retry-After`/`X-RateLimit-*` | counter-key |

## Timing-class signals

| The observed | Signal |
|---|---|
| `median(good)-median(bad) > 3x jitter` | verify-short-circuit |
| `stdev(good) > stdev(bad)` (equalized mean) | fixed-dummy variance |
| three timing bands (active/locked/fake) | state-timing |

## Lock-class signals

| The observed | Signal |
|---|---|
| `423 "locked"` on a real name at N | lockout-oracle |
| `401` forever on a fake (no lock possible) | no-counter-confirm |
| `"account is locked"` state-message | lock-state |

## Direct-class signals

| The observed | Signal |
|---|---|
| `GET ?u=` → `{"available":bool}` | direct-boolean |
| `/check-username`/`/exists`/`/taken`/`/available` | direct-endpoint |
| `GET /api/users/{id}` `200`/`404` | rest-resource |
| `/api/users/` a public roster | public-list |
| `query{userByEmail}` `null`/`{id}` | graphql-resolver |
| `query{userExists}` `bool` | graphql-boolean |
| `mutation{login}` `"USER_NOT_FOUND"`/`"INVALID"` | graphql-typed |
| `invalid_grant`/`invalid_client`/`error_description` | oauth-token |
| `account_not_found` SSO | federated |
| `?author=N`/`wp-json/wp/v2/users` | WP |

## Crash-class signals

| The observed | Signal |
|---|---|
| `500`/`crash` only on the fake arm | crash-branch |
| `{"detail":"user.hash on None"}` | crash-detail |

## The signal-to-file map

Each signal routes to its channel file — `channel-body`, `channel-status`,
`channel-side`, `timing-oracle`/`timing-statistics`, `api-enum`,
`register-reset-enum`, `graphql-resolvers-deep`, `rest-resources-deep`,
`sso-and-federated`, `account-lockout`, `observability-side`,
`detection-map`, `lead-grammar`.
