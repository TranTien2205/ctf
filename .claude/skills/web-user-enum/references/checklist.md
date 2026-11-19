# Checklist — the printable operator list

## Before

- [ ] the target is authorized/owned/lab — spray is scope-gated
- [ ] a known-good account named (yours, `admin`, a seeded name)
- [ ] every account-touching form listed (login/register/reset/check/mfa/api)

## Per form

- [ ] known-good vs known-bad vs repeated-bad sent, other fields constant
- [ ] CSRF token re-fetched per request if required
- [ ] body diff'd RAW + noise-masked
- [ ] status + `Location` compared
- [ ] envelope (`-sv`) compared — cookies, headers, JSON fields
- [ ] timing measured only if content uniform — N≥8, interleaved, median

## Confirm

- [ ] bad1==bad2 (noise baseline established)
- [ ] good!=bad on ≥1 channel (the oracle)
- [ ] a SECOND bad name → same as bad1 (tracks the username-class)
- [ ] the delta re-runs
- [ ] verbatim excerpts recorded per channel

## Throttle

- [ ] bounded burst (8-15) → absent / threshold / 429 / lock / captcha
- [ ] if limited: X-Forwarded-For / fresh-session / endpoint / method / param bypass probed
- [ ] the threshold or the bypass recorded verbatim

## Route

- [ ] each confirmed account → web-auth-session / web-idor / web-logic-flaw / web-oauth-sso
- [ ] a no-throttle / bypassed-limit finding recorded
- [ ] a uniform all-forms result → recorded negative

## Do-not

- [ ] no mass-username spray on a shared/victim target
- [ ] no claiming an oracle from a single response
- [ ] no diff of the rendered page (raw bytes only)
- [ ] no "didn't see a limit" reported as "no limit" without a bounded burst
