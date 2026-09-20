---
name: web-open-redirect
description: >
  Action-oriented depth skill for Open redirect. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: web-ssrf, web-oauth-sso.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [web, open-redirect, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
evidence_level: catalogue
---
# Open redirect

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

one external destination in the redirect parameter, following the response Location header exactly

**Falsifier** — the observation that closes this class: the destination is validated against an allowlist or forced to a relative path
## Recognise

A parameter that names where to go next: a post-login destination, a callback, a
continue URL. The response is a redirect and the parameter is inside its
`Location` header.

## Confirm

Send one external destination and inspect the exact `Location` header without
following it. Repeat once with an encoded or parser-boundary form only if the
first result is inconclusive. Confirmation requires the server to emit a
redirect to the attacker-controlled destination.

## Why it matters in a chain

Alone it is low value. It becomes the chain when it feeds something that trusts
the destination: an OAuth redirect target, a server-side fetch, or a bot that
will visit whatever it is handed. See `../web-oauth-sso/` and `../web-ssrf/`.

## Traps

- A validator that only checks a prefix is satisfied by a hostname that starts
  with the allowed value. One that only blocks `//` is satisfied by backslashes
  or encoded forms, depending on which parser resolves the URL.
- A redirect that is immediately followed by a safe allowlist or a fixed
  relative path is not open; record the exact header before escalating.

## Routing

Shares signals with: `../web-ssrf/`, `../web-oauth-sso/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/ctf-web/auth-and-access.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
