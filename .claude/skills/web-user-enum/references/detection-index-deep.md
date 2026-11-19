# Detection index (deep) — every signal to its file

## The surface signals

| Signal | File |
|---|---|
| a `<form action=/login>` | `detection.md`,`login-enum.md`,`form-surface.md` |
| a `<form action=/register>` | `register-reset-enum.md`,`per-form-deep.md` |
| a `<form action=/forgot>` | `register-reset-enum.md`,`per-form-deep.md` |
| a `check-username`/`available` link or AJAX | `form-surface.md`,`api-enum.md` |
| a `POST /api/login` in the bundle | `api-enum.md`,`per-surface-deep.md` |
| a `/graphql` endpoint | `api-enum.md`,`per-surface-deep.md` |
| a `/api/users/` route | `api-enum.md`,`web-idor` |
| a `Sign in with Google`/`SAML` | `web-oauth-sso`,`per-target.md` |
| a `ws://`/`wss://` auth frame | `web-websocket`,`per-target.md` |
| a `Basic`/`Authorization` prompt | `per-target.md` |

## The response signals

| Signal | File |
|---|---|
| `"no such user"`/`"wrong password"` | `channel-body.md`,`attack-shapes.md` |
| a `?e=`/`?error=`/`?msg=` redirect param | `channel-status.md` |
| a `404`/`401`/`302`/`422` differential | `channel-status.md` |
| `{"error":"user_not_found"}`/`{"exists"}`/`{"taken"}` | `api-enum.md`,`channel-body.md` |
| a `Set-Cookie` on one arm | `channel-side.md` |
| a `{"emails_queued":1}`/`{"sent"}` | `channel-side.md`,`register-reset-enum.md` |
| a slow `good` arm | `timing-oracle.md` |
| a `423`/`429` on a real name | `throttling.md`,`channel-side.md` |
| `"locked"`/`"pending"`/`"disabled"` | `edge-cases-deep.md`,`per-mechanism-deep.md` |
| a `500` only on bad-user | `common-mistakes-deep.md`,`per-mechanism-deep.md` |

## The throttle signals

| Signal | File |
|---|---|
| a `429`/`Retry-After` | `throttling.md`,`per-falsifier.md` |
| a `423`/`"locked"` | `throttling.md`,`channel-side.md` |
| a CAPTCHA after N | `throttling.md`,`evasion-deep.md` |
| `X-Forwarded-For` resets a `429` | `rate-limit-bypass.md` |
| an `X-RateLimit-Remaining` header | `throttling.md`,`per-target.md` |

## The confusable signals

| Signal | Route |
|---|---|
| a JWT/session/token flaw | `web-auth-session` |
| a broken workflow/business rule | `web-logic-flaw` |
| a `'`/`$ne` injection in the user field | `web-sqli`/`web-nosqli` |
| a `role`/`is_admin` bound param | `web-mass-assignment` |
