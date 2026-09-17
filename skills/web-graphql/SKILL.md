---
name: web-graphql
description: >
  GraphQL abuse. Open after the router or tools/classify.py named this class.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [web, graphql, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
evidence_level: catalogue
---
# GraphQL abuse

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

one introspection query; if it is disabled, one field-suggestion error to recover names

**Falsifier** — the observation that closes this class: introspection is off and errors reveal no field names
## Recognise

A single endpoint that takes a query document. Introspection, type names, or a
query and mutation shape in the body.

## Confirm

One introspection query. If introspection is disabled, field-suggestion errors
often rebuild the schema a name at a time.

## What the schema buys

The schema is the attack surface list: every field, every mutation, every
relationship. The findings are usually the ordinary ones — an object read without
an ownership check, a mutation that should be admin-only — reached through a
single endpoint instead of many routes. Cross-check with `../web-idor/`.

## Traps

- Depth and alias limits exist; a query that is too large is rejected for size,
  not authorisation. Do not read that as a defence.
- Batched queries can bypass per-request rate limits, which matters when the
  finding needs many attempts.

## Routing

Shares signals with: `../web-idor/`, `../web-logic-flaw/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/ctf-web/server-side-2.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
