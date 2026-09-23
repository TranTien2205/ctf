---
name: web-xxe
description: >
  Action-oriented depth skill for XML external entity. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: file-read-primitives, web-ssrf.
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

1. Send a baseline document and record status, body length, and timing.
2. Send one harmless internal entity that points to a path the challenge
   definitely supplies. Keep the entity read-only.
3. If the response is not an echo channel, use an out-of-band URL only when the
   challenge explicitly provides a callback you control.

Expected confirmation is entity expansion in the response or an attributable
callback. A generic XML parse error does not prove entity resolution.

## Operational probe

Use a baseline document, then one internal entity whose value is a harmless
known file or marker:

```xml
<?xml version="1.0"?>
<!DOCTYPE r [<!ENTITY probe "XXE_PROBE">]>
<r>&probe;</r>
```

If the endpoint echoes the field, replace only the internal entity with a local
file reference that the supplied challenge definitely contains. If there is no
echo channel, use an out-of-band URL only when the challenge provides a
controlled callback. Record status, body length, parser error, and callback
evidence separately. A malformed XML error does not prove external entity
resolution.

For uploads, keep the first file a valid document of the observed type. Do not
combine XXE with archive traversal, polyglot content, or an external callback in
the first request.

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
- An uploaded document may be parsed by more than one library; identify the
  parser used by the relevant route before choosing a format-specific reference.

## Routing

Shares signals with: `../file-read-primitives/`, `../web-ssrf/`. Check those before committing to this one.

Depth, one named file at a time:

- `../ctf-web/server-side-2.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
