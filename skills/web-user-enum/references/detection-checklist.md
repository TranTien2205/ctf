# Detection checklist — the entry-measurement list

## The surface inventory

- [ ] login form located (endpoint + fields + CSRF)
- [ ] register form located
- [ ] reset/forgot-password located
- [ ] forgot-username / unlock / reactivate located
- [ ] check-username / available / user-exists endpoint checked
- [ ] api login/token/graphql endpoints located
- [ ] a user-resource `/api/users/{id}` located
- [ ] mfa/otp/send endpoints located

## The known-good

- [ ] your own account registered → guaranteed known-good
- [ ] a seeded/default name listed (`admin`, `root`, challenge-named)
- [ ] a provably-fake name prepared (`zzz-` + random)

## The first probes

- [ ] direct oracle tried: `GET /check-username?u=` / register-taken
- [ ] 3-request pair on `/login`: good/bad/repeated-bad
- [ ] the noise baseline measured (`bad1` vs `bad2`)
- [ ] all four channels measured on at least one form

## The detection record

- [ ] per-form oracle: `<form>: <channel>: <delta>` or `uniform`
- [ ] the cheapest-leak form identified
- [ ] the confusable boundary checked (auth-session/logic/sqli)

## Detection stop

- [ ] every account-touching form measured oracle-or-uniform
- [ ] the throttle measured (the second half)
- [ ] the findings recorded; the negatives recorded
