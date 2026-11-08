---
name: web-host-header
description: >
  Action-oriented depth skill for Host / forwarded-header attacks. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: web-parser-differential, web-cache-poisoning.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [web, host-header, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# Host / forwarded-header attacks

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

send the request twice, once with a controlled X-Forwarded-Host and once with a swapped Host — a reset-link or redirect reflecting your host is the signal

**Falsifier** — the observation that closes this class: no response element (Location, link, cookie domain, generated URL) is built from any attacker-controlled host header on either request
## Recognise

The app builds URLs or applies middleware ACLs from request headers it trusts:
`Host`, `X-Forwarded-Host`, `X-Forwarded-Server`, `X-Original-URL`,
`X-Rewrite-URL`, `Forwarded: host=`. Password-reset links, absolute redirects,
cookie domains and generated canonical URLs are the classic sinks; front-end
ACLs that honour `X-Original-URL` are the modern one.

## Confirm safely

Send the request twice: once with a canary host in the suspect header, once
with the header absent. The canary appearing in a Location, a generated link
inside the body, or a Set-Cookie domain is the signal — quote the reflecting
bytes verbatim.

For the ACL-bypass shape, the canary is a path that 403s when requested
directly: `X-Original-URL: /admin` returning the admin page is the finding.

## Headers worth a request each

| Header | What it poisons |
|---|---|
| `Host` | everything when the proxy ignores it — also try `Host: good` + `Host: evil` duplicated |
| `X-Forwarded-Host` / `X-Host` | generated URLs, reset links |
| `X-Original-URL` / `X-Rewrite-URL` | middleware rewrites + ACLs |
| `Forwarded: host=evil` | RFC 7239 form, often honoured where the others are not |

## Traps

- A reflected host in the response is only a lead; the finding needs the host
  reaching a decision (link the victim clicks, path the middleware applies,
  domain a cookie binds to).
- Password-reset poisoning requires a real reset flow — request a reset for
  your OWN account and inspect the delivered link. Do not reset other
  accounts.
- Some frameworks read `Host` only after validating it against a server list;
  a 400 on a bad host is a negative result, not a retry signal.

## Operational probe

```bash
curl -i -H 'X-Forwarded-Host: evil.example' "$BASE/reset"   # link sink
curl -i -H 'X-Original-URL: /admin' "$BASE/"                # middleware ACL
curl -i -H 'Host: evil.example' "$BASE/robots.txt"          # canonical-URL sink
```

`tools/web/host_probe.py` sweeps the same header set with one canary
marker and grades each response: `reflected-into-body` (link-generation
sink, verbatim excerpt attached) or `routing-delta` (status/signature
change vs baseline = vhost or middleware ACL routing).

## Routing

Shares signals with: `../web-parser-differential/`, `../web-cache-poisoning/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/web-host-header/references/README.md`
- `skills/web-host-header/references/header-pairs.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
