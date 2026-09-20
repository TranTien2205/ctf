---
name: web-open-redirect
description: >
  Open redirect. Open after the router or tools/classify.py named this class.
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

One external destination, and read the exact `Location` header rather than
following it — the browser's final page hides what the server actually said.

## Why it matters in a chain

Alone it is low value. It becomes the chain when it feeds something that trusts
the destination: an OAuth redirect target, a server-side fetch, or a bot that
will visit whatever it is handed. See `../web-oauth-sso/` and `../web-ssrf/`.

## Traps

- A validator that only checks a prefix is satisfied by a hostname that starts
  with the allowed value. One that only blocks `//` is satisfied by backslashes
  or encoded forms, depending on which parser resolves the URL.

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
