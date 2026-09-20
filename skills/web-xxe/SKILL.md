---
name: web-xxe
description: >
  XML external entity. Open after the router or tools/classify.py named this class.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [web, xxe, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
evidence_level: catalogue
---
# XML external entity

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

one entity pointing at a path the target certainly has, and an out-of-band entity when nothing is echoed

**Falsifier** — the observation that closes this class: the parser is configured with entity resolution disabled
## Recognise

Anything that parses XML on the server: a direct XML endpoint, a SOAP service, an
office document upload, or an SVG. The parser matters more than the endpoint —
older configurations resolve external entities by default.

## Confirm

One entity pointing at a file the target certainly has. If nothing is echoed, the
confirmation is out-of-band: an entity that forces the parser to fetch a URL you
control.

## Where it usually hides

Document formats are ZIP containers with XML inside: replacing one part of a
`.docx` or `.xlsx` puts your entity in front of a parser that the upload handler
never intended to expose. SVG uploads reach an image pipeline that is often an
XML parser first.

## Traps

- A blocked external DTD does not mean entities are off; parameter entities and
  local file entities may still resolve.
- Error-based extraction leaks the file through the parser's own error message
  when the response body does not echo anything.

## Routing

Shares signals with: `../file-read-primitives/`, `../web-ssrf/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/ctf-web/server-side-2.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
