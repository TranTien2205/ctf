---
name: web-logic-flaw
description: >
  Action-oriented depth skill for Business logic / mass assignment. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: web-idor, web-race-condition.
  Verified here by 1 chain card(s).
tags: [web, logic-flaw, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: verified
---
# Business logic / mass assignment

**Verified here.** Chains that prove this class:

- `knowledge/chains/pico-pachinko-revisited-node-offset-scale-wrap-instruction-overwrite.json`

Run `python3 tools/chain_match.py` before this skill: a matching
chain gives you the exact confirming probe that already worked.

## First probe

one extra field the model has but the form does not send, or one step of the flow skipped

**Falsifier** — the observation that closes this class: the handler reads an explicit allowlist of fields and ignores everything else
## Recognise

Nothing is technically broken — the application does exactly what it was told, and
what it was told is wrong. Extra fields accepted into a model, a workflow step
that can be skipped, a coupon that can be applied twice, a role that can be set at
registration.

## Confirm

1. Record the account's own state before the request.
2. Add exactly one field the normal form does not send, or omit exactly one
   workflow step.
3. Read the state back through the account's normal view.

Confirmation requires an attributable before/after change caused by that one
field or skipped step. A success response without a state change is
inconclusive.

## Where to look first

- The model's field list versus the form's field list. The gap is the candidate.
- Any step that trusts a value the previous step produced without re-checking it.
- Anything that assumes an order the API does not enforce.

## Traps

- Logic flaws are easy to claim and hard to prove. State exactly which field or
  which skipped step produced the change, and show the before and after.
- An allowlist of assignable fields closes mass assignment completely; read the
  handler before spending the budget.
- Keep the first test on an account or object you created. Do not change roles,
  balances, or another player's records until the field boundary is proven.

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
