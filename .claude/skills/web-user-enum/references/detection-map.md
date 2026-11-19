# Detection map — observable to channel to file

## Map every observable to its measurement

| You observe | Channel | Open |
|---|---|---|
| `"No such user"`/`"Wrong password"` text | body/text | `channel-body.md` |
| an `error_code`/`err`/`code` in the response | body/code | `channel-body.md` |
| a different CSS class/`data-`/hidden-input/comment | body/residual | `channel-body.md` |
| `Location: ?e=1` vs `?e=2`, `?error=user` vs `?error=pass` | redirect | `channel-status.md` |
| `404`/`401`/`302`/`422`/`423` differs | status | `channel-status.md` |
| a `Set-Cookie`/`X-` header on one arm | side/cookie | `channel-side.md` |
| `attempts_remaining`/`emails`/`user_exists` field | side/json | `channel-side.md` |
| a `{"error":"user_not_found"}`/`{"reason"}` | json | `api-enum.md` |
| `{"data":{"userByEmail":null}}` vs `{id}` | graphql | `api-enum.md` |
| `checkUser`/`userExists`/`check-username`/`available` | direct | `api-enum.md`,`form-surface.md` |
| `GET /api/users/{id}` `200`/`404` | direct/rest | `api-enum.md` |
| a 50-300ms median delta | timing | `timing-oracle.md` |
| a stdev gap on a fixed dummy-hash | timing/variance | `timing-oracle.md` |
| `"username taken"`/`409` on register | register | `register-reset-enum.md` |
| `{"emails_queued"}`/a send on reset | reset/send | `register-reset-enum.md` |
| a `302 /check-email` only on the real arm | reset/redirect | `register-reset-enum.md` |
| `423 "locked"` on a real name at N | lock | `channel-side.md` |
| `"account locked"`/`"pending"`/`"disabled"` | state-message | `edge-cases-deep.md` |
| `account_not_found`/`invalid_grant`/`invalid_client` | oauth | `api-enum.md`,`per-target-deep.md` |
| `user@external` vs `user@local` SAML redirect | federated | `per-target-deep.md` |
| a `500`/`crash` only on the fake arm | crash-branch | `common-mistakes-deep.md` |

## The throttle observables

| You observe | Verdict | Open |
|---|---|---|
| no `429`/`423`/`delay`/captcha in a 15-burst | absent | `throttling.md` |
| `429`/`423` at N | threshold | `throttling.md` |
| `X-RateLimit-*`/`Retry-After` header | a counter-key | `throttling-deep.md` |
| a CAPTCHA interstitial after N | challenge | `evasion-deep.md` |
| `X-Forwarded-For`/fresh resets `429` | bypassed | `rate-limit-bypass.md` |
| an alias endpoint not limited | route-gap | `rate-limit-bypass-deep.md` |
| `1/sec` window | a bound | `rate-limit-bypass-deep.md` |

## The measurement-order rule

Direct oracles first (one request, no baseline), then the per-form
channels body → status+loc → timing → side, then the throttle burst.
Every observable is a candidate until the three-arm verify confirms it.
