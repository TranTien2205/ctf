---
name: web-csrf
description: >
  Action-oriented depth skill for Cross-site request forgery. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: web-xss, web-cors.
  Verified here by 2 chain card(s).
tags: [web, csrf, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: verified
---
# Cross-site request forgery

**Verified here.** Chains that prove this class:

- `knowledge/chains/htb-tornadoservice-bot-csrf-class-pollution.json`
- `knowledge/chains/htb-ssos-oauth-registration-race-cookie-swap-json-csrf.json`

Run `python3 tools/chain_match.py` before this skill: a matching
chain gives you the exact confirming probe that already worked.

## First probe

a cross-origin form whose content type the endpoint still accepts, submitted by the viewer you control

**Falsifier** — the observation that closes this class: the endpoint requires a token the attacker page cannot read or a content type a form cannot produce
## Recognise

A state-changing endpoint that accepts a request the browser will send with
credentials attached, and does not require a value the attacker page cannot read.
In CTF this is nearly always paired with a bot that visits a URL you submit.

## Confirm

Host a page that issues the request cross-origin and have the viewer load it.
Confirmation is the state change, observed from your own account or from the
endpoint's response afterwards.

## Reaching a JSON endpoint from a form

A form cannot set an arbitrary content type, but `text/plain` is allowed. The
body is `name` + `=` + `value`, so putting the opening of the JSON document in
the field name and closing it in the value produces a valid JSON body with no
encoding applied. Endpoints that parse the body by content sniff, or that accept
`text/plain`, are reachable this way.

## Traps

- Fire one route at a time. Two payloads at once — a form and a framed script,
  say — make success unattributable, and bot cycles are limited.
- Bot sessions are often re-created per visit, so a stolen credential dies fast.
  Verify it immediately.
- Check the cookie's same-site attribute before assuming the browser will attach
  it to a cross-origin request.

## Routing

Shares signals with: `../web-xss/`, `../web-cors/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/ctf-web/client-side.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Operational probe

Record a same-origin baseline first:

```bash
curl -i -b "$COOKIE_JAR" "$BASE/profile"
```

Then use one cross-origin form submission against an object you created:

```html
<form action="https://TARGET/change" method="POST" enctype="text/plain">
  <input name='{"name":"csrf-marker","ignore":"' value='"}'>
</form>
<script>document.forms[0].submit()</script>
```

Use only methods, fields, and content types observed in source or the live form.
A 200 or navigation is surface evidence. The class signal is an attributable
before/after state change, read back with a separate request. If JSON is required
and `text/plain` is rejected, record `inconclusive` instead of overclaiming.

For a bot challenge, submit one URL, wait for one bot cycle, then read the object
you own. Do not combine a state-change form with an XSS payload in one cycle.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
