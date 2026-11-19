# First hour (deep) — the full 60-minute runbook

## 0-10: scope + inventory + the direct oracle

- confirm authorized/owned/lab; note the spray bound
- `python3 tools/web/enum_probe.py --selftest`
- inventory every account-touching endpoint (form-surface.md)
- register YOUR account → known-good
- try the direct oracle: `GET /api/username-available?u=`,
  `GET /check-username?u=`, `POST /register` (taken-check) — a direct
  boolean confirms the class in one request

## 10-25: the per-form 3-request pair

```bash
for form in login register forgot-password forgot-username mfa; do
  python3 tools/web/enum_probe.py --url "$BASE/$form" \
    --body 'user={U}&pass=x' --known-user KNOWN --method POST 2>&1 | tail -8
done
# manual fallbacks for non-standard bodies
```

Per form: which channels separate the arms? Record `<form>: <channel>`.

## 25-40: confirm + the throttle

- re-run the oracle with a SECOND bad name → tracks the username-class
- the noise baseline (`bad1`==`bad2`) per form
- the timing baseline on content-uniform forms — N≥8 interleaved
- the bounded burst (8-15) → absent/threshold/lock/captcha
- if limited → `rate-limit-bypass.md` XFF/session/endpoint/method

## 40-55: the bounded candidate list

On a scoped target: 10-50 seeded names through the confirmed oracle.
`admin administrator root test service backup deploy ci jenkins gitlab
flag ctf` + the challenge-named + app-leaked. Each confirmed name
recorded with the verbatim oracle excerpt. NEVER a mass spray; NEVER
over the measured throttle.

## 55-60: record + route

- `enum: <form>: <channel>: <delta>` per oracle
- `throttle: <absent|at-N|bypassed-by-X>`
- each confirmed name → `web-auth-session`/`web-idor`/`web-logic-flaw`/
  `web-oauth-sso`
- every (form × channel) cell: LEAK / uniform / unmeasured
- a fully-closed form → `knowledge/attempts/` kill-map
- `../../field-notes.md` updated

## The hour's exits

- a verified account list + a routed next class → enum done
- a no-throttle/bypass + a confirmed name → credential-loop route
- a clean all-uniform → a real negative; the chain moves to the neighbor

The enum's job is the measurement; the hour ends at a routed name or a
recorded negative, not a repeated re-probe.
