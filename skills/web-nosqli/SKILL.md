---
name: web-nosqli
description: >
  Action-oriented depth skill for NoSQL / operator injection. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: web-sqli, web-prototype-pollution.
  Verified here by 1 chain card(s).
tags: [web, nosqli, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: verified
---
# NoSQL / operator injection

**Verified here.** Chains that prove this class:

- `knowledge/chains/htb-secnotes-mongoose-rename-prototype-pollution-local-gate.json`

Run `python3 tools/chain_match.py` before this skill: a matching
chain gives you the exact confirming probe that already worked.

## First probe

send the filter pinned to an object you created, with every write field omitted, and read what comes back

**Falsifier** — the observation that closes this class: the value is coerced to a string, so no object reaches the query

**Blast radius** — read before any write on a shared instance: a broad filter combined with write fields rewrites the whole collection
## Recognise

The query takes an object, not a string. The tell is a JSON body whose value can
be replaced by a document: `{"id": "abc"}` becomes `{"id": {"$ne": null}}` and
the handler passes it straight to the driver. Mongo ids are 24 hex characters and
documents carry a version key, so both show up in responses.

## Confirm safely

Send the filter pinned to an object **you created**, with every write field
omitted. A read-safe update returns the matched documents unchanged, which proves
the filter is attacker-shaped without touching anyone else's data.

Only after that, test operators one at a time.

## The operators that matter

| Operator | What it buys |
|---|---|
| `$ne`, `$gt`, `$regex` | a boolean oracle over a field you cannot read |
| `$where` | JavaScript evaluation inside the query, when the server allows it |
| `$rename` | moves a value to a new path — including a dotted path the validator does not check |

`$rename` is the bridge to prototype pollution: schema validation usually guards
assignment paths, not rename targets. See `../web-prototype-pollution/SKILL.md`.

## Traps

- A broad filter combined with write fields rewrites every document in the
  collection. On a shared instance that destroys other players' work and can cost
  the instance. Pin the filter to your own object id, every time.
- An operator that works in the shell may be blocked by the ODM's strict mode;
  the error text usually names which.

## Routing

Shares signals with: `../web-sqli/`, `../web-prototype-pollution/`. Check those before committing to this one.

Depth, one named file at a time:

- `references/operators.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
