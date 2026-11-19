# Lead grammar — every signal shape and what it claims

## The oracle-lead shapes

| Shape | Claims | Verify |
|---|---|---|
| `"no such user"`/`"wrong password"`/`"taken"` | a text oracle | masked diff repeats |
| `?e=1`/`?e=2`, `error=user`/`error=pass` | a redirect oracle | `Location` byte-diff |
| `404`/`401`/`302`/`422` differential | a status oracle | `-w` code, repeats |
| `{"error":"user_not_found"}`/`{"exists"}`/`{"taken"}` | a JSON oracle | JSON diff, repeats |
| `{"available":false}`/`{"exists":true}` | a direct oracle | `GET ?u=` boolean |
| a `Set-Cookie`/header/JSON-field diff | a side oracle | envelope diff |
| `{"emails_queued":1}`/`{"sent"}` | a send oracle | reset queue diff |
| a slow `good` arm | a timing oracle | N>=8 median + re-run |
| a `423` on a real name | a lock oracle | locks on real only |
| `{"userByEmail":{id}}`/`checkUser` | a GraphQL oracle | resolver `null` vs object |
| `"USER_NOT_FOUND"`/`"INVALID_CREDENTIALS"` | a typed-error oracle | `errors[].code` diff |
| a `500` only on bad-user | a crash oracle | repeats on re-send |
| `invalid_grant`/`invalid_client` | an oauth oracle | token error diff |
| `account_not_found` (SSO) | a federated oracle | redirect/`Location` diff |
| `locked`/`pending`/`disabled` msg | a state oracle | state-message diff |

## The throttle-lead shapes

| Shape | Claims | Verify |
|---|---|---|
| no `429`/`423`/delay in 15 | throttle absent | the bounded count |
| `429`/`423` at N | a threshold | the N |
| `X-Forwarded-For`/fresh resets `429` | bypassed | the reset verbatim |
| a CAPTCHA after N | a throttle | the N + the interstitial |
| an `X-RateLimit-*` header | a counter-key | the header |
| a per-second window | a bound | N per T measured |

## The verdict grammar

Every lead is `oracle`/`uniform`/`unmeasured`/`candidate`:

- `oracle` — a repeated, channel-identified delta → route
- `uniform` — a measured-identical channel → a recorded negative
- `unmeasured` — a gap → probe it or mark it a gap
- `candidate` — a one-off anomaly → re-send first

## The name-lead

A confirmed account name is the enum's output — `enum: <form>: <channel>:
<name> confirmed` → routed to `web-auth-session`/`web-idor`/`web-logic-flaw`/
`web-oauth-sso`. The name is a target, not a finding in itself.
