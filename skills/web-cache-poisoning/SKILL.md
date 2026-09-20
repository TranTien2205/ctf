---
name: web-cache-poisoning
description: >
  Cache poisoning / deception. Open after the router or tools/classify.py named this class.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [web, cache-poisoning, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
evidence_level: catalogue
---
# Cache poisoning / deception

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

send an unkeyed header with a unique marker, then request the same URL cleanly and look for the marker

**Falsifier** — the observation that closes this class: the header is part of the cache key, so the poisoned copy is never served to anyone else

**Blast radius** — read before any write on a shared instance: a poisoned entry is served to every other player until it expires
## Recognise

A cache sits in front of the application — the response carries a cache status,
an age, or a vary header. The question is which parts of the request are in the
cache key and which are not.

## Confirm

Send an unkeyed input carrying a unique marker, then request the same URL cleanly
from a different session. Finding your marker in the clean response proves the
poisoned entry is served to others.

## What to look for

- A header the application reflects but the cache does not key on.
- A path that normalises differently in cache and application, so a static-looking
  URL is served the dynamic response.
- A parameter the cache ignores but the application honours.

## Traps

- This is the one web class where a successful probe **affects every other
  player** until the entry expires. Use a marker that is harmless, keep the time
  to live in mind, and never poison an entry the whole challenge depends on.
- A response that varies per user is usually not cached at all; confirm the
  response is cacheable before spending the budget.

## Routing

Shares signals with: `../web-parser-differential/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/ctf-web/client-side.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
