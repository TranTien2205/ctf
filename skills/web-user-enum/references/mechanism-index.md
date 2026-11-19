# Mechanism index — the sub-mechanism map

## The oracle mechanisms

| Mechanism | The asymmetry | File |
|---|---|---|
| text oracle | the error names account-vs-password | `channel-body.md` |
| code oracle | a `error_code`/class/field differs | `channel-body.md` |
| status oracle | a code/`Location` differs | `channel-status.md` |
| timing oracle | `verify()` runs only for real | `timing-oracle.md` |
| variance oracle | a fixed dummy-hash has lower stdev | `timing-oracle.md`,`differentials-deep.md` |
| cookie oracle | a `Set-Cookie` on one arm | `channel-side.md` |
| send oracle | the email/OTP fires only for real | `channel-side.md` |
| lock oracle | `423` only on a real row | `channel-side.md` |
| json oracle | a `error`/`exists`/`reason` field | `api-enum.md` |

## The form mechanisms

| Mechanism | File |
|---|---|
| login enum | `login-enum.md` |
| register enum | `register-reset-enum.md` |
| reset enum | `register-reset-enum.md` |
| direct-exists | `form-surface.md` |
| api/graphql enum | `api-enum.md` |
| unlock/mfa/invite enum | `form-surface.md` |

## The throttle mechanisms

| Mechanism | File |
|---|---|
| throttle-absent | `throttling.md` |
| throttle-threshold | `throttling.md` |
| throttle-bypass | `rate-limit-bypass.md` |

## The mechanism-to-channel map

Every mechanism resolves to one of the four channels — the mechanism is
the *named instance*; the channel (`channels.md`) is the *measurement
protocol*. The channel files carry the diff; the mechanism files carry
the shape.
