# Checklist (deep) — the exhaustive operator list

## Scope + inventory

- [ ] authorized/owned/lab confirmed — spray is scope-gated
- [ ] every account-touching endpoint listed:
  login/register/reset/forgot-user/check-user/unlock/mfa/invite/api/graphql/users
- [ ] a known-good named (own account / seeded / challenge-named)
- [ ] two different provably-fake names prepared
- [ ] `enum_probe --selftest` passes

## Per-form — the oracle

- [ ] the direct oracle tried (check-username / register-taken)
- [ ] known-good vs known-bad vs repeated-bad sent, fields constant
- [ ] CSRF re-fetched per request if required
- [ ] `bad1`==`bad2` noise baseline established
- [ ] body diff'd masked; the survivor classified (text/code/JSON/comment)
- [ ] status + `Location` compared (both, not just code)
- [ ] envelope (`-sv`) compared — cookies, headers, JSON sub-fields
- [ ] the send side-effect checked (reset/mfa)
- [ ] timing measured — N≥8, interleaved, median, if content uniform
- [ ] the variance checked if median is equalized

## Confirm

- [ ] the delta is on ≥1 channel and REPEATS
- [ ] a SECOND bad name → same response shape (tracks the class)
- [ ] a re-run → the delta reproduces
- [ ] the account-state messages checked (locked/pending/disabled)
- [ ] verbatim excerpts recorded per confirmed channel

## Throttle

- [ ] bounded burst (8-15) → absent / threshold / `429`/`423`/captcha/delay
- [ ] the counter-key identified (per-IP/account/session/endpoint)
- [ ] bypass probes — XFF / fresh-session / endpoint / method / param / case
- [ ] the threshold or the bypass recorded verbatim (a bypass IS a finding)

## Route + record

- [ ] each confirmed account → web-auth-session / web-idor / web-logic-flaw / web-oauth-sso
- [ ] a no-throttle / bypassed-limit recorded as a finding
- [ ] every (form × channel) cell marked LEAK / uniform / unmeasured
- [ ] a fully-closed form → kill-map written
- [ ] `../../field-notes.md` updated with the real measurement

## Do-not (the guardrails)

- [ ] no mass-username spray on a shared/victim target
- [ ] no oracle claimed from a single or unmasked response
- [ ] no rendered-page diff (raw bytes + envelope only)
- [ ] no "didn't see a limit" as "no limit" without a bounded burst
- [ ] no victim-account lock to prove the lock exists (use your own)
- [ ] no unbounded spray after a bypass (the bypass is the finding)
