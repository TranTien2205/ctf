# Detection catalogue — the complete signal inventory

## Direct signals (probe-free or one-request)

| Signal | Class | Confidence |
|---|---|---|
| `GET /api/username-available?u=...` in the bundle | direct oracle | high |
| `/check-username`/`/available`/`/exists`/`/taken`/`/user-exists` | direct | high |
| `GET /api/users/{id}` `200`/`404` | REST oracle + `web-idor` | high |
| `query{userByEmail}`/`checkUser`/`userExists` | GraphQL oracle | high |
| `?author=N` → `/author/<name>` | the WP pattern | high |
| `/wp-json/wp/v2/users` | public user list | high |
| `{"exists"}`/`{"available"}`/`{"taken"}` in a response | direct | high |

## Form signals (the three arms)

| Signal | Channel |
|---|---|
| `"no such user"` vs `"wrong password"` | body/text |
| `error_code`/`err`/`code` `1001` vs `1002` | body/code |
| a CSS class/`data-`/hidden-input/comment diff | body/residual |
| `Location: ?e=1` vs `?e=2`, `?error=user` vs `?error=pass` | redirect |
| `404`/`401`/`302`/`422`/`423` differential | status |
| `Set-Cookie`/`X-` header/`attempts_remaining`/`emails` | side |
| `{"error":"user_not_found"}`/`{"exists"}`/`{"reason"}` | json |
| `{"data":{"userByEmail":null}}` vs `{id}` | graphql |
| a 50-300ms median delta (the bcrypt gap) | timing |
| a stdev gap on a fixed dummy-hash | timing/variance |
| `"username taken"`/`"email registered"`/`409` on register | register |
| `{"emails_queued":1}`/a send on reset | reset/send |
| `423 "locked"` on a real name at N | lock |
| `"account is locked"`/`"pending"`/`"disabled"` | state-message |
| `account_not_found`/`invalid_grant`/`invalid_client` | oauth/sso |
| `user@external` vs `user@local` SAML redirect | federated |
| a `500` only on the fake arm | crash-branch |

## Throttle signals

| Signal | Verdict |
|---|---|
| no `429`/`423`/delay in a 15-burst | absent |
| `429`/`423` at N | threshold |
| `X-RateLimit-*`/`Retry-After` header | a counter-key |
| a CAPTCHA after N | challenge control |
| `X-Forwarded-For`/fresh-session resets `429` | bypassed |
| an alias endpoint not limited | route-gap |
| a `GET`/JSON/method not counted | method/param-gap |

## The confidence ladder

- **direct** — a check/REST/GraphQL exists-endpoint — near-certain
- **form** — a three-arm differential on a channel — strong
- **timing** — a median delta + jitter baseline — statistical
- **send/lock** — a side-effect only on real — strong but slow
- **candidate** — a single or unmasked anomaly — re-send first

## The detection rule

A signal is a candidate until measured. The three arms + the channel's
protocol + a re-run is the verdict — never a single response, never a
message the app shows in its UI without the raw diff.
