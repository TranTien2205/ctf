---
name: web-graphql
description: >
  Action-oriented depth skill for GraphQL abuse. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: web-idor, web-logic-flaw.
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

1. Identify the endpoint and send one bounded introspection query.
2. If introspection is disabled, send one deliberately unknown field and record
   whether the error discloses a type or field suggestion.
3. Use only the names observed in the schema or error before testing an
   object-level read or mutation.

Confirmation is a schema/error oracle, not a finding by itself. The exploit
class is confirmed only when a read or mutation crosses an authorization or
validation boundary and the result is observed.

## Operational probe

Record the endpoint, method, content type, and one baseline query. Then send a
bounded schema probe:

```json
{"query":"{__typename}"}
```

If accepted, use one introspection query limited to types and fields needed for
the challenge. If introspection is disabled, send one unknown field and preserve
the exact field-suggestion error. Do not invent names after a silent response.

After schema discovery, test one observed object with two identities or one
observed mutation with a harmless value. Schema disclosure is not an exploit;
confirmation requires an attributable authorization or validation boundary
crossed in the response.

## Operational probe

Start with a bounded schema request against the observed endpoint:

```bash
curl -i "$BASE/graphql" \
  -H 'Content-Type: application/json' \
  --data-binary '{"query":"{__typename}"}'
```

If the endpoint accepts it, request only the observed schema surface. If
introspection is disabled, use one unknown field and preserve the exact error.
Do not invent field names after a silent response.

The first useful signal is schema/type disclosure. The vulnerability signal is
separate: use two identities or roles to request one observed object field or
mutation, and compare the authorization result. A schema that is merely public
is not an authorization finding.

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
- A rejected introspection query is not a secure GraphQL implementation; it only
  closes that discovery channel. Do not invent field names after a silent error.

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
