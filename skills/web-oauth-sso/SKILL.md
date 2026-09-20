---
name: web-oauth-sso
description: >
  Action-oriented depth skill for OAuth / SSO flow. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: web-auth-session, web-open-redirect.
  Verified here by 1 chain card(s).
tags: [web, oauth-sso, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
evidence_level: verified
---
# OAuth / SSO flow

**Verified here.** Chains that prove this class:

- `knowledge/chains/htb-ssos-oauth-registration-race-cookie-swap-json-csrf.json`

Run `python3 tools/chain_match.py` before this skill: a matching
chain gives you the exact confirming probe that already worked.

## First probe

walk the whole flow once and record every redirect, parameter and cookie set, before changing any of them

**Falsifier** — the observation that closes this class: the state parameter is bound to the session and the redirect target is a strict allowlist
## Recognise

An authorisation flow across two parties: an identity provider and the
application, joined by redirects, a code and a state parameter. Multiple session
cookies usually appear — one per party.

## Confirm

**Walk the whole flow once and record everything before changing anything**: every
redirect, every parameter, every cookie set and by whom. Most findings in this
class are visible in that transcript, and a change made before the transcript
exists is unattributable.

## What goes wrong

| Where | Shape |
|---|---|
| State parameter | not bound to the session, so a flow can be started by one party and finished by another |
| Redirect target | validated loosely, so the code is delivered somewhere it should not be |
| Account linking | identity matched on an address the attacker can also register |
| Two cookies | the application and the provider each set one, and swapping them at the right moment crosses the identities |

The last one is why the transcript matters: the exploit lives in the ordering of
cookie writes, not in any single request.

## Traps

- A registration step inside the flow can be raced; see `../web-race-condition/`.
- Changing a redirect target usually invalidates the code. Test the validation
  first with a harmless variation.

## Routing

Shares signals with: `../web-auth-session/`, `../web-open-redirect/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/web-auth-session/references/oauth-flow-issues.md`
- `skills/ctf-web/auth-infra.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
