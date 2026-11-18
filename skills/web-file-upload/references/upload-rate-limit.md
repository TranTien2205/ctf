# Rate-Limit & Lockout — the budget the app enforces

## The shape — the upload endpoint throttles you

- `429 Too Many Requests` on repeated uploads
- `403` after N failed uploads
- a per-user/per-IP quota
- a daily size cap

The limit decides how many payloads you can try — plan the probes around it.

## Detection — is there a throttle?

- repeated identical uploads → `429`/`403` after N
- `X-RateLimit-Remaining`/`Retry-After` headers
- slower response on rapid requests
- a `quota`/`limit`/`throttle` field in the response

## The bypass list — the standard escapes

- `X-Forwarded-For: 1.2.3.4` — spoof client IP — if the limit keys on
  XFF and the app trusts it
- `X-Real-IP`/`CF-Connecting-IP`/`True-Client-IP` — the same idea
- a different endpoint/verb — `POST`/`PUT`/`PATCH` on the same path —
  the limit may key on method
- a different path that hits the same handler — `/upload/` vs `/upload`
  vs `//upload` vs `/api/v1/upload` — path normalization differences
- `?param=`/`;jsessionid=`/`..;/` — URL-decorated path variants
- case changes `/Upload` — case-sensitive rate keys miss case-insensitive
  paths
- concurrent bursts — the rate limit is counted per-check-window; race
  past it — `race-and-temp-files.md`

## The "rate limit IS the challenge" — timing-based surfaces

- a upload-scan job runs on a timer — the file exists only during the
  scan window — the rate limit's the delay you need to work within
- `race-and-temp-files.md` — the scan window IS the race window

## The "quota is per-user" pivot

If the limit is per-user — a different session/token/user gets a fresh
budget — test the same payload under another account.

## The honest read — a real rate limit is a real budget

A hard limit that can't be bypassed means every probe must count — the
detection probes should be maximally informative, not repeated variants.

## Falsifiers

- no throttle exists — unlimited attempts

## Output to record

- the throttle mechanism + whether a bypass exists + how many probes it
  costs per attempt
