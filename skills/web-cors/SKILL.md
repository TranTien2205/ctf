---
name: web-cors
description: >
  Action-oriented depth skill for CORS misconfiguration. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: web-csrf.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [web, cors, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
evidence_level: catalogue
---
# CORS misconfiguration

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

repeat an authenticated request with a foreign Origin and read whether the origin is reflected alongside credentials

**Falsifier** — the observation that closes this class: the allowed origin is a fixed allowlist, or credentials are not permitted
## Recognise

The response carries an access-control origin header. The question is whether the
value is a fixed allowlist or an echo of whatever the request asked for, and
whether credentials are permitted alongside it.

## Confirm

1. Capture an authenticated baseline response without `Origin`.
2. Repeat the same request with a unique foreign `Origin`.
3. Inspect both the actual response and the preflight response, if the browser
   would preflight.

Confirmation requires the foreign origin to be reflected or accepted **and**
credentials to be allowed in a browser-usable response. A wildcard alone, or an
origin header on a public unauthenticated endpoint, is not enough.

## Operational probe

Capture both the actual response and the preflight when required:

```bash
curl -i -b "$COOKIE_JAR" \
  -H 'Origin: https://attacker.invalid' \
  "$BASE/api/profile"

curl -i -X OPTIONS -b "$COOKIE_JAR" \
  -H 'Origin: https://attacker.invalid' \
  -H 'Access-Control-Request-Method: GET' \
  "$BASE/api/profile"
```

Record `Access-Control-Allow-Origin`, `Access-Control-Allow-Credentials`,
allowed methods/headers, and whether the response carries authenticated data.
Confirmation requires a foreign origin that the browser accepts with
credentials **and** an authenticated response readable by that origin. A
reflected header without credentials or without a readable sensitive response
is surface evidence only.

## What to check beyond the wildcard

- A null origin, which sandboxed frames and some redirects produce.
- A prefix or suffix match rather than an exact one, which a lookalike hostname
  satisfies.
- A subdomain allowlist combined with any injection on a subdomain.

## Traps

- A wildcard origin cannot be combined with credentials by the browser, so a bare
  wildcard on a public endpoint is usually not exploitable.
- The preflight response and the actual response can differ; read both.
- Header presence is not browser exploitability: check whether the requested
  method/headers and credentials policy line up.
- Do not confuse CSRF with CORS: CSRF needs an attributable state change, while
  CORS needs browser-readable cross-origin response data.

## Routing

Shares signals with: `../web-csrf/`. Check those before committing to this one.

Depth, one named file at a time:

- `../ctf-web/auth-infra.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
