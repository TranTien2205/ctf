---
name: web-race-condition
description: >
  Action-oriented depth skill for Race condition / TOCTOU. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: web-logic-flaw.
  Verified here by 2 chain card(s).
tags: [web, race-condition, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: verified
---
# Race condition / TOCTOU

**Verified here.** Chains that prove this class:

- `knowledge/chains/htb-apexsurvive-profile-race-template-literal-xss-template-overwrite-rce.json`
- `knowledge/chains/htb-ssos-oauth-registration-race-cookie-swap-json-csrf.json`

Run `python3 tools/chain_match.py` before this skill: a matching
chain gives you the exact confirming probe that already worked.

## First probe

two interleaved requests, not a flood: the point is to land the second commit inside the window, and a flood hides which one did

**Falsifier** — the observation that closes this class: the read and the write happen inside one transaction or behind one lock

**Blast radius** — read before any write on a shared instance: racing a shared resource can corrupt it for other players; race an object you own
## Recognise

Check and act are separated. A balance is read then debited, a token is issued
then re-read, a limit is counted then incremented — and nothing holds a lock
across the gap.

In source the tell is two awaits, or a read and a write, on the same record
across different functions.

## Confirm

**Two interleaved requests, not a flood.** The goal is to land the second commit
inside the window; a flood succeeds without telling you which request did it, and
a result you cannot attribute is not evidence.

Send A and B so their windows overlap, then read the state and decide which one
won.

## What makes the window wide

- The read and the write live in different functions, so extra work happens
  between them.
- An external call — email, webhook, render — sits inside the window.
- The isolation level permits the interleaving. A single transaction at a strict
  level closes the window entirely; check before spending the budget.

## Traps

- Racing a shared resource corrupts it for other players. Race an object you own.
- Parallel requests over one connection may serialise; use enough connections
  that the requests genuinely overlap.
- If the first attempt does not land, re-roll rather than escalating the rate.

## Routing

Shares signals with: `../web-logic-flaw/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/web-race-condition/references/README.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
