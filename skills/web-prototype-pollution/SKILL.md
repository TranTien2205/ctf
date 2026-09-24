---
name: web-prototype-pollution
description: >
  Action-oriented depth skill for Prototype / class pollution. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: web-nosqli, web-deserialization.
  Verified here by 3 chain card(s).
tags: [web, prototype-pollution, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: verified
---
# Prototype / class pollution

**Verified here.** Chains that prove this class:

- `knowledge/chains/htb-secnotes-mongoose-rename-prototype-pollution-local-gate.json`
- `knowledge/chains/htb-tornadoservice-bot-csrf-class-pollution.json`
- `knowledge/chains/htb-novacore-hopbyhop-cache-overflow-domclobber-polyglot-rce.json`

Run `python3 tools/chain_match.py` before this skill: a matching
chain gives you the exact confirming probe that already worked.

## First probe

pollute one harmless property, then read it back through a path that should not have it

**Falsifier** — the observation that closes this class: the merge rejects reserved keys, or nothing reads the polluted property with a fallback

**Blast radius** — read before any write on a shared instance: pollution is global to the process: every later request inherits it until restart
## Recognise

Two shapes, same mechanism: JavaScript **prototype** pollution and Python **class**
pollution. Somewhere a routine copies attacker-shaped keys onto an object without
filtering reserved ones — a deep merge, a recursive assignment, a rename, a config
loader.

The payoff is a property that some later code reads **with a fallback**. A check
that reads an optional property and treats absence as trusted is the target.

## Confirm

Pollute one harmless property, then read it back through a path that should not
have it. Do not jump straight at the gate you actually want.

## Operational probe

Pin every write to an object you created and use a property with no security
meaning. For a JSON deep merge, the shape is:

```json
{"profile":{"__proto__":{"training_marker":"unique-value"}}}
```

For a document-store rename, create the source value first and omit every other
write field:

```json
{"filter":{"id":"<own-id>"},"$rename":{"marker":"__proto__.training_marker"}}
```

Use the exact wrapper and operator observed in the request schema. The class
signal is the marker appearing on a fresh object or a later object that should
not inherit it. A successful update response alone is surface evidence. If
reserved keys are rejected, values are coerced to strings, or no later read
observes the marker, record the falsifier or `inconclusive` and stop.

For Python class pollution, prove the harmless attribute path before testing a
security-relevant fallback or command sink.

## Reaching the write

| Route | Shape |
|---|---|
| Deep merge of request JSON | `__proto__` as a key in the merged object |
| Rename operator in a document store | a dotted target path under `__proto__` |
| Recursive attribute set in Python | `__class__.__init__.__globals__` to a module-level object |

A rename is the route when direct assignment is blocked: validators usually guard
assignment paths, not rename targets.

## Materialisation

Writing the pollution is not the same as applying it. A document store may only
run the prototype setter when the document is **loaded and cloned**, so the
sequence is write, then read the object back, then test the gate.

## Traps

- Pollution is global to the process. Every later request inherits it until
  restart, so on a shared instance you have changed the app for everyone. Pollute
  the narrowest property that reaches your goal.
- The values you pollute with must already exist somewhere when the write is a
  rename: create them first.
- Restart or isolate the process after a pollution probe when the challenge
  permits it; polluted state can persist globally for every player.
- Never test a broad filter or a role/command property first.

## Routing

Shares signals with: `../web-nosqli/`, `../web-deserialization/`. Check those before committing to this one.

Depth, one named file at a time:

- `../ctf-web/node-and-prototype.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
