# Mechanism catalogue — the complete sub-mechanism reference

## Existence-oracle mechanisms (18)

| # | Mechanism | The asymmetry | Channel | File |
|---|---|---|---|---|
| 1 | honest-error | `if not user: return "no such user"` | body/text | `channel-body.md` |
| 2 | code-residual | `error_code`/class/`data-`/hidden/comment differs | body/code | `channel-body.md` |
| 3 | redirect-param | `Location: ?e=1` vs `?e=2` | status/redirect | `channel-status.md` |
| 4 | status-code | `404`/`401`/`302`/`422` differs | status | `channel-status.md` |
| 5 | hash-short-circuit | `verify()` runs only on real | timing | `timing-oracle.md` |
| 6 | variance-gap | a fixed dummy-hash's lower stdev | timing/variance | `timing-oracle.md` |
| 7 | cookie-artifact | a `Set-Cookie` on one arm | side | `channel-side.md` |
| 8 | send-side-effect | the email/OTP fires only for real | side/send | `channel-side.md` |
| 9 | lock-artifact | `423` only on a real row | side/lock | `channel-side.md` |
| 10 | json-field | `{"error"}`/`{"exists"}`/`{"reason"}` | json | `api-enum.md` |
| 11 | direct-boolean | a `check`/`available`/`exists` endpoint | direct | `form-surface.md` |
| 12 | register-taken | `INSERT`/`unique`-conflict `"taken"` | register | `register-reset-enum.md` |
| 13 | reset-send | `send_reset` on the real arm | reset/send | `register-reset-enum.md` |
| 14 | graphql-resolver | `userByEmail`/`checkUser`/`login` typed | direct/graphql | `api-enum.md` |
| 15 | rest-resource | `GET /api/users/{id}` `200`/`404` | direct/rest | `api-enum.md` |
| 16 | state-message | `locked`/`pending`/`disabled` reveals | body/state | `edge-cases-deep.md` |
| 17 | federated-redirect | `user@external` vs `user@local` SAML | redirect | `per-target-deep.md` |
| 18 | crash-branch | a `user.hash`-on-`None` `500` | status/body | `common-mistakes-deep.md` |

## Throttle mechanisms (8)

| # | Mechanism | The property | File |
|---|---|---|---|
| 19 | absent | no 429/423/captcha/delay in a burst | `throttling.md` |
| 20 | threshold | `429`/`423` at a measured N | `throttling.md` |
| 21 | per-IP | counter keyed on source — XFF-spoofable | `rate-limit-bypass.md` |
| 22 | per-account | counter keyed on username — spray-under | `throttling.md` |
| 23 | per-session | counter keyed on session — fresh resets | `rate-limit-bypass.md` |
| 24 | per-endpoint | one route limited, an alias not | `rate-limit-bypass.md` |
| 25 | CAPTCHA | a challenge after N | `throttling.md`,`evasion-deep.md` |
| 26 | window | N-per-T bounds but does not block | `rate-limit-bypass-deep.md` |

## The catalogue rule

Every mechanism is a named, bounded, falsifiable measurement — the
pass runs each mechanism's channel protocol per form, and each result
is `oracle`/`uniform`/`unmeasured`. The mechanism is the named instance;
the channel is the measurement; the form is where it applies.
