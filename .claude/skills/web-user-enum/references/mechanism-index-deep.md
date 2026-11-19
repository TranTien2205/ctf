# Mechanism index (deep) — the complete sub-mechanism catalogue

## Existence-oracle mechanisms

| # | Mechanism | The asymmetry | Channel |
|---|---|---|---|
| 1 | honest-error | `if not user: return "no such user"` | body/text |
| 2 | code-residual | a `error_code`/class/`data-`/hidden field differs | body/code |
| 3 | redirect-param | `Location: ?e=1` vs `?e=2` | status/redirect |
| 4 | status-code | `404`/`401`/`302`/`422` differs | status |
| 5 | hash-short-circuit | `verify()` on the real arm | timing |
| 6 | variance-gap | a fixed dummy-hash's lower stdev | timing/variance |
| 7 | cookie-artifact | a `Set-Cookie` on one arm | side |
| 8 | send-side-effect | the email/OTP fires only for real | side/send |
| 9 | lock-artifact | `423` only on a real row | side/lock |
| 10 | json-field | `{"error"}`/`{"exists"}`/`{"reason"}` differs | json |
| 11 | direct-boolean | a `check`/`available`/`exists` endpoint | direct |
| 12 | register-taken | `INSERT`/`unique`-conflict `"taken"` | register |
| 13 | reset-send | `send_reset` on the real arm | reset/send |
| 14 | graphql-resolver | `userByEmail`/`checkUser`/`login` typed | direct/graphql |
| 15 | rest-resource | `GET /api/users/{id}` `200`/`404` | direct/rest |
| 16 | state-message | `locked`/`pending`/`disabled` reveals | body/state |
| 17 | federated-redirect | `user@external` vs `user@local` SAML | redirect |
| 18 | crash-branch | a `user.hash`-on-`None` `500` | status/body |

## Throttle mechanisms

| # | Mechanism | The property |
|---|---|---|
| 19 | absent | no 429/423/captcha/delay in a bounded burst |
| 20 | threshold | `429`/`423` at a measured N |
| 21 | per-IP | counter keyed on source IP — XFF-spoofable |
| 22 | per-account | counter keyed on username — spray-under |
| 23 | per-session | counter keyed on session — fresh-session resets |
| 24 | per-endpoint | one route limited, an alias not |
| 25 | CAPTCHA | a challenge after N — bounds the loop |
| 26 | window | N-per-T that bounds but does not block |

## The catalogue-to-file map

Each mechanism has its channel-protocol file (`channel-*.md`), its
form file (`*-enum.md`), and its index entry here. The mechanism is the
named instance of an asymmetry; the corpus's files carry the protocol
to measure it.
