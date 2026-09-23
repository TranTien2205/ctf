---
name: web-parser-differential
description: >
  Action-oriented depth skill for Parser differential / proxy trust. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: web-request-smuggling, web-auth-session.
  Verified here by 1 chain card(s).
tags: [web, parser-differential, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
evidence_level: verified
---
# Parser differential / proxy trust

**Verified here.** Chains that prove this class:

- `knowledge/chains/htb-novacore-hopbyhop-cache-overflow-domclobber-polyglot-rce.json`

Run `python3 tools/chain_match.py` before this skill: a matching
chain gives you the exact confirming probe that already worked.

## First probe

send the same authenticated-only request twice, once normally and once with the proxy header named in the Connection header

**Falsifier** — the observation that closes this class: both forms are rejected, so the trust check does not depend on that header
## Recognise

A proxy, gateway or WAF sits in front of the application and the two disagree
about the same bytes. The application trusts something the proxy is expected to
set — most often a client-address header — and has a fallback for when it is
missing.

## Confirm

Send the same restricted request twice: once normally, once with the proxy's own
header named in the `Connection` header. A proxy that honours hop-by-hop
semantics strips its own header before forwarding, and the application's
missing-header fallback decides the request is local.

## The general question

Always ask: **what does the trust check read, and who is supposed to set it?**
The same shape appears with path normalisation, method casing, duplicate headers,
and content-length versus transfer-encoding. If the proxy and the backend
normalise differently, the rule the proxy enforces is not the rule the backend
applies.

## Traps

- Header spoofing alone usually fails when the check reads the socket peer rather
  than a header. Read which one it is before spending the budget.
- A rule that matches an unanchored pattern, or compares with containment rather
  than equality, is bypassable without any protocol trick at all.

## Routing

Shares signals with: `../web-request-smuggling/`, `../web-auth-session/`. Check those before committing to this one.

Depth, one named file at a time:

- `../web-triage/references/http-parser-differential.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
