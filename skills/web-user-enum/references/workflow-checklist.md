# Workflow checklist — the pass, step by step

## Phase 0 — scope + inventory

- [ ] authorized/owned/lab; the spray bound noted
- [ ] `enum_probe --selftest` passes
- [ ] every account-touching endpoint listed
- [ ] known-good + two fake names prepared; the format resolved

## Phase 1 — the direct oracle

- [ ] `GET /check-username?u=` / `/available?u=` / `?email=` probed
- [ ] the register-taken check probed
- [ ] a direct-boolean hit → the class confirmed → skip to the list

## Phase 2 — the per-form pair

- [ ] known-good vs known-bad vs repeated-bad on EVERY account form
- [ ] `bad1`==`bad2` noise baseline per form
- [ ] the fields constant across the pair; CSRF handled

## Phase 3 — the per-channel measurement

- [ ] body: masked raw diff
- [ ] status + `Location`: code + param
- [ ] envelope: `-sv` cookies/headers/JSON-fields
- [ ] timing: N>=8 interleaved median (content-uniform forms)
- [ ] send-side: reset/mfa queue
- [ ] lock: N attempts → `423` on your own known-good

## Phase 4 — the oracle confirm

- [ ] the delta repeats on a re-run
- [ ] a SECOND bad name → same response shape (tracks the class)
- [ ] verbatim excerpts per confirmed channel
- [ ] a candidate account confirmed (its response matches known-good)

## Phase 5 — the throttle

- [ ] bounded burst (8-15) → absent / threshold / `423`/`429`/captcha
- [ ] the counter-key identified (IP/account/session/endpoint)
- [ ] the bypass set probed — XFF/session/endpoint/method/param/case
- [ ] the threshold or the bypass recorded verbatim

## Phase 6 — the bounded list

- [ ] scoped: 10-50 seeded names through the confirmed oracle
- [ ] each confirmed name recorded with the oracle excerpt
- [ ] no mass spray; no over-throttle

## Phase 7 — record + route

- [ ] `enum: <form>: <channel>: <delta>` per oracle
- [ ] `throttle: <absent|N|bypassed>` recorded
- [ ] each name → `web-auth-session`/`web-idor`/`web-logic-flaw`/`web-oauth-sso`
- [ ] every (form × channel) cell marked; a closed form → kill-map
- [ ] `../../field-notes.md` updated
