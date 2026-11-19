# Detection index — signal-to-file map

## The entry signals

| Signal | Open |
|---|---|
| a login/register/reset/check form exists | `detection.md`, `form-surface.md`, `per-form.md` |
| a `check-username`/`available` endpoint | `form-surface.md`, `api-enum.md` |
| a JSON/GraphQL auth endpoint | `api-enum.md`, `per-endpoint.md` |
| a `?error=`/`?e=` on the login redirect | `channel-status.md` |
| a lockout/CAPTCHA/rate-limit observed | `throttling.md`, `rate-limit-bypass.md` |

## The channel signals

| Signal | Open |
|---|---|
| the error text differs | `channel-body.md`, `channel-body` diffs |
| the status/`Location` differs | `channel-status.md` |
| a timing gap exists | `timing-oracle.md`, `channel-side.md` |
| a cookie/header/JSON-field differs | `channel-side.md` |
| the send fires only for real | `channel-side.md`, `register-reset-enum.md` |
| a `423`/`429` on a real name | `channel-side.md`, `throttling.md` |

## The measurement signals

| Signal | Open |
|---|---|
| per-request noise in the diff | `channel-body.md`, `differentials-deep.md` |
| a one-off anomaly | `falsifiers.md`, `common-mistakes.md` |
| a sub-jitter timing delta | `timing-oracle.md`, `troubleshoot.md` |
| a masked/swallowed diff | `differentials-deep.md`, `troubleshoot.md` |

## The boundary signals

| Signal | Route |
|---|---|
| a JWT/session/token bug, uniform auth | `../web-auth-session/` |
| a broken business rule | `../web-logic-flaw/` |
| an injection in the username field | `../web-sqli/`/`../web-nosqli/` |
| a `200`/`404` user-resource read | `../web-idor/` |
| an SSO account-exists/pre-hijack | `../web-oauth-sso/` |
