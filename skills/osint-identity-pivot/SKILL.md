---
name: osint-identity-pivot
description: >
  Action-oriented depth skill for Identity and handle pivot. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: osint-media-metadata, osint-infra-records.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [osint, osint-identity-pivot, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# Identity and handle pivot

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

extract the single most UNIQUE pivot and normalise it -- compute the key fingerprint rather than eyeballing it -- then produce an ordered plan of at most six queries, each with its source and the one fact it would confirm, for ctf-writeup-scout to run

**Falsifier** — the observation that closes this class: the pivot is too generic to separate from unrelated accounts, which is a measurement about the pivot and means a different one must be extracted rather than the same one searched harder
## Recognise

The pivot is a handle, an email, a name, or a key fingerprint, and the question
asks for a different attribute of the same identity — another account, a real
name, a location, a domain.

## Confirm

Extract the **single most unique** pivot and normalise it: compute a key
fingerprint rather than eyeballing a key, derive the email pattern rather than
guessing one address. Then an ordered plan — at most six sources, each chosen
for what it can uniquely add — worked one source at a time.

| Pivot | First pivots it buys |
|---|---|
| a rare handle | other platforms where the same handle exists |
| an email | the local-part as a handle; the domain's own records |
| a name + org | professional records, conference talks, commits |
| a PGP or SSH key | keyserver uid packets, `authorized_keys` strings in repos |

Confirmation is two attributes that corroborate each other — a handle match
alone is a lead, not an identity.

## Traps

- A pivot too generic to separate from unrelated people is a measurement about
  the pivot: extract a rarer one instead of forcing the search.
- Avatars and bios get reused — a reverse image match is often a stronger pivot
  than the handle itself.
- Record every negative result with the query that produced it, so no source is
  queried twice and a later claim can cite the dead end.

## Operational probe

Work the plan, not the search bar: one query per source, verbatim results into
notes, and public sources only —
`../osint-triage/references/legal-considerations.md` bounds what is in scope.

## Routing

Shares signals with: `../osint-media-metadata/`, `../osint-infra-records/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/ctf-osint/social-media.md`
- `skills/osint-triage/references/email-pattern-detection.md`
- `skills/osint-triage/references/legal-considerations.md`

| Any handle/identity pivot question | `references/handle-pivot.md` |

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
