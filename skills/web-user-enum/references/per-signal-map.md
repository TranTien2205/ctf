# Per-signal map — signal to channel to file, one line each

## The existence-oracle signals

| Signal | Channel | File |
|---|---|---|
| `"no such user"`/`"wrong password"` | body/text | `channel-body.md` |
| `error_code`/`err`/`code` | body/code | `channel-body.md` |
| class/`data-`/hidden/comment | body/residual | `channel-body.md`,`response-diffing.md` |
| `?e=`/`?error=`/`Location` param | redirect | `channel-status.md` |
| `404`/`401`/`302`/`422`/`423` | status | `channel-status.md` |
| a 50-300ms median gap | timing | `timing-oracle.md`,`timing-statistics.md` |
| a stdev/variance gap | timing/variance | `timing-statistics.md` |
| `Set-Cookie`/`X-`/`attempts`/`emails` | side | `channel-side.md`,`observability-side.md` |
| `{"error":"user_not_found"}`/`{"reason"}` | json | `api-enum.md` |
| `{"available"}`/`{"exists"}`/`{"taken"}` | direct | `api-enum.md`,`form-surface-deep.md` |
| `GET /api/users/{id}` `200`/`404` | rest | `rest-resources-deep.md` |
| `?author=N`/`wp-json`/`/author/<name>` | wp | `framework-matrix.md` |
| `query{userByEmail}`/`userExists` | graphql | `graphql-resolvers-deep.md` |
| `"USER_NOT_FOUND"`/`"INVALID_CREDENTIALS"` | graphql-typed | `graphql-resolvers-deep.md` |
| `"username taken"`/`"email registered"` | register | `register-reset-enum.md` |
| `{"emails_queued"}`/a send | reset/send | `register-reset-enum.md` |
| `423 "locked"` on a real name | lock | `account-lockout.md` |
| `"locked"`/`"pending"`/`"disabled"` | state | `mfa-and-state.md` |
| `invalid_grant`/`invalid_client` | oauth | `api-enum-deep.md`,`sso-and-federated.md` |
| `user@external`/`user@local`/`account_not_found` | federated | `sso-and-federated.md` |
| a `500`/`crash` on the fake arm | crash | `response-diffing.md` |
| autocomplete/search/mention/follow | second-order | `second-order.md` |

## The throttle signals

| Signal | Verdict | File |
|---|---|---|
| no `429`/`423` in 15 | absent | `throttling.md`,`throttle-taxonomy.md` |
| `429`/`423` at N | threshold | `throttling.md` |
| `XFF`/fresh/alias/method reset | bypassed | `rate-limit-bypass.md`,`rate-limit-bypass-deep.md` |
| `X-RateLimit-*`/`Retry-After` | counter-key | `throttle-taxonomy.md` |
| CAPTCHA after N | challenge | `evasion-deep.md` |
| `1/sec` window | bound | `rate-limit-bypass-deep.md` |
| per-worker counter | scope note | `distributed-and-cache.md` |
