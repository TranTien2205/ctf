# Mechanism map — the sub-mechanism → channel → file index

## The oracle mechanisms → channels → files

| Mechanism | Channel | File |
|---|---|---|
| the error names the field | body/text | `channel-body.md`,`login-enum.md` |
| a `error_code`/class/field | body/code | `channel-body.md` |
| a `?e=`/`?error=` redirect | status/redirect | `channel-status.md` |
| a `404`/`401`/`302` | status | `channel-status.md` |
| `verify()` on the real arm | timing | `timing-oracle.md` |
| a fixed dummy-hash variance | timing/variance | `timing-oracle.md`,`differentials-deep.md` |
| a `Set-Cookie` on one arm | side | `channel-side.md` |
| an email/OTP on real | side/send | `channel-side.md`,`register-reset-enum.md` |
| a `423` on real | side/lock | `channel-side.md`,`throttling.md` |
| `{"available"}`/`{"exists"}` | direct | `form-surface.md`,`api-enum.md` |
| `"taken"`/`409` register | register | `register-reset-enum.md` |
| a typed GraphQL error | direct | `api-enum.md` |
| a `200`/`404` REST | direct | `api-enum.md` |

## The throttle mechanisms → files

| Mechanism | File |
|---|---|
| absent (no bound) | `throttling.md` |
| threshold (locks/429 at N) | `throttling.md` |
| bypassed (XFF/session/endpoint reset) | `rate-limit-bypass.md` |
| CAPTCHA after N | `throttling.md`,`evasion-deep.md` |

## The map rule

A mechanism names the *shape*; the channel names the *measurement*;
the file carries the *protocol*. Read the channel file for HOW to
measure; read the mechanism file for WHAT it is; read the form file for
WHERE to apply it.
