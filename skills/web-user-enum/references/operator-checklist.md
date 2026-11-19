# Operator checklist — the pass, box by box

## Recon

- [ ] inventory every account endpoint (`form-surface-deep.md`)
- [ ] `bundle_miner`/`web-source-map` the front-end → grep
      `check|available|exists|username|users/|register|reset`
- [ ] every `<form>`, `<input name=`, `fetch(`/`.ajax`/`axios` endpoint
- [ ] headers — `X-RateLimit-*`, `Set-Cookie`, `Server`, framework

## Direct oracles

- [ ] `GET ?u=`/`check-username`/`available`/`exists`/`taken`/`user-exists`
- [ ] `GET /api/users/{id}` `200`/`404` + the object read
- [ ] `/api/users/`/`/wp-json/wp/v2/users` a public roster
- [ ] `?author=N` → `/author/<name>` (WP)
- [ ] GraphQL `userByEmail`/`checkUser`/`userExists`/`login`
- [ ] SSO `login_hint`/SAML `email` → IdP/local/`account_not_found`

## Per-form channels — the three arms each

- [ ] `/login` — body / status+`Location` / timing / side
- [ ] `/register` — the taken-check (which field leaks)
- [ ] `/reset`/`/forgot` — the send-side + redirect + timing
- [ ] `/check-*` — the direct boolean
- [ ] `/unlock`/`/reactivate`/`/confirm`/`/mfa`/`/otp`/`/invite`
- [ ] `/api/login`/`/oauth/token` — JSON error/code/`invalid_grant`

## Channel protocols

- [ ] body — the masked raw-byte diff, `b vs b2` empty
- [ ] status+`Location` — `-D -`, never follow
- [ ] timing — N>=8 interleaved, medians, jitter baseline, re-run
- [ ] side — `-sv` envelope, the cookie/header/send/lock

## Throttle

- [ ] the 15-req burst — `429`/`423`/delay/captcha/absent?
- [ ] the counter-key — IP/session/endpoint/method/param/case?
- [ ] the bypass — XFF/fresh/alias/method reset? record the reset
- [ ] the lock — on YOUR account only; record `locks at N`

## Names

- [ ] the seeded list through the confirmed oracle
- [ ] the app-leaked names (bundle/source/content fixtures)
- [ ] each verified name + its oracle excerpt recorded
- [ ] each negative name recorded too

## Close

- [ ] every (form × channel) cell `oracle`/`uniform`/`unmeasured`
- [ ] the coverage matrix complete — not just `/login`
- [ ] negatives recorded verbatim (`uniform: <form>:<channel>`)
- [ ] each oracle/name/throttle routed to the neighbor class
- [ ] `../field-notes.md` updated with the measured outcomes
- [ ] the budget respected — 5 probes/15min per mechanism class

## The honesty box

- [ ] no flag claimed without `hooks.py pre-flag` on a live response
- [ ] no oracle claimed from a single or unmasked response
- [ ] no spray run inside the enum's budget
- [ ] no victim account locked — own account only
- [ ] catalogue-honest — standard knowledge, not a local solve
