---
name: web-cache-poisoning
description: >
  Action-oriented depth skill for Cache poisoning / deception. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: web-parser-differential.
  Verified here by 1 chain card(s).
tags: [web, cache-poisoning, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: verified
---
# Cache poisoning / deception

**Verified here.** Chains that prove this class:

- `knowledge/chains/htb-encodecept-charset-xss-cache-deception-orm-oracle-marshal-rce.json`

Run `python3 tools/chain_match.py` before this skill: a matching
chain gives you the exact confirming probe that already worked.

## First probe

send an unkeyed header with a unique marker, then request the same URL cleanly and look for the marker

**Falsifier** — the observation that closes this class: the header is part of the cache key, so the poisoned copy is never served to anyone else

**Blast radius** — read before any write on a shared instance: a poisoned entry is served to every other player until it expires
## Recognise

A cache sits in front of the application — the response carries a cache status,
an age, or a vary header. The question is which parts of the request are in the
cache key and which are not.

## Confirm

1. Record a clean baseline from a fresh session and note cache headers, age, and
   the apparent cache key.
2. Send one harmless unique marker through a suspected unkeyed header, query
   parameter, or path normalisation boundary.
3. Request the same URL cleanly from a separate session.

Confirmation requires the marker to persist into the clean response and a cache
indicator or repeatable response comparison showing that the stored response was
reused. A marker reflected only in the immediate response is not poisoning.

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
- Use a disposable path or an entry with a short, known lifetime; poisoning a
  shared flag or login page is an avoidable outage.

## Routing

Shares signals with: `../web-parser-differential/`. Check those before committing to this one.

Depth, one named file at a time:

- `../ctf-web/client-side.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
