# First hour — the ordered 60 minutes

## Minutes 0-10: inventory + the direct oracle

- list every account-touching form (login/register/reset/check/mfa/api)
- register YOUR account → a guaranteed known-good
- probe the direct oracle first: `GET /api/username-available?u=`,
  `/check-username`, a register "taken" check — if it exists, the class
  is confirmed in one request

## Minutes 10-25: the three-request oracle per form

```bash
python3 tools/web/enum_probe.py --url "$BASE/<form>" \
  --body 'user={U}&pass=x' --known-user KNOWN --method POST
```

Per form: known-good vs known-bad vs repeated-bad, all four channels
measured. Record which channel(s) separate the arms per form.

## Minutes 25-40: confirm + throttle

- re-run the oracle with a SECOND bad name → confirm it tracks the
  username-class
- the bounded burst (8-15) → throttle absent / threshold / lock
- if limited → `X-Forwarded-For`/session/endpoint/method bypass probes

## Minutes 40-55: the bounded list + the confirmed names

On an authorized target: a small candidate list (10-20 seeded names:
`admin root test service backup deploy ci jenkins gitlab flag` + the
challenge-named ones) through the confirmed oracle → the verified
account names. Never a mass spray.

## Minutes 55-60: record + route

- `enum: <form>: <channel>: <delta>` per oracle
- `throttle: <absent|at-N|bypassed-by-X>`
- each confirmed name → `web-auth-session`/`web-idor`/`web-logic-flaw`/
  `web-oauth-sso`
- a uniform all-forms result → a recorded negative

## The hour's end-state

Either a verified account list + a routed next class, or a clean
"all forms measured uniform + throttle measured" — both are complete
outcomes. The enum's job ends at the measurement; the exploit is the
routed class.
