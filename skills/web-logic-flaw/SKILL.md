---
name: web-logic-flaw
description: >
  Business logic / mass assignment. Open after the router or tools/classify.py named this class.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [web, logic-flaw, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
evidence_level: catalogue
---
# Business logic / mass assignment

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

one extra field the model has but the form does not send, or one step of the flow skipped

**Falsifier** — the observation that closes this class: the handler reads an explicit allowlist of fields and ignores everything else
## Recognise

Nothing is technically broken — the application does exactly what it was told, and
what it was told is wrong. Extra fields accepted into a model, a workflow step
that can be skipped, a coupon that can be applied twice, a role that can be set at
registration.

## Confirm

One extra field the model has but the form never sends, or one step of the flow
performed out of order. The confirmation is the state change, read back from the
account's own view.

## Where to look first

- The model's field list versus the form's field list. The gap is the candidate.
- Any step that trusts a value the previous step produced without re-checking it.
- Anything that assumes an order the API does not enforce.

## Traps

- Logic flaws are easy to claim and hard to prove. State exactly which field or
  which skipped step produced the change, and show the before and after.
- An allowlist of assignable fields closes mass assignment completely; read the
  handler before spending the budget.

## Routing

Shares signals with: `../web-idor/`, `../web-race-condition/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/ctf-web/auth-and-access.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
