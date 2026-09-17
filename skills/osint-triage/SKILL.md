---
name: osint-triage
description: >
  OSINT router for CTF challenges whose answer lives in public sources: a photo
  to geolocate, a handle to pivot, a domain or certificate to trace, a document
  whose metadata carries the answer. Extract one unique pivot, then work one
  source at a time.
tags: [osint, geolocation, pivot, metadata, ctf]
environment: [ctf, lab]
---

# OSINT — Router

A CTF OSINT challenge gives you a small artifact and expects one specific fact.
The work is: find the single most unique thing in the artifact, then follow it
through one source at a time.

**Scope.** This router covers challenge artifacts only. It is not reconnaissance
against an organisation, and it is not credential collection. Several files under
`references/` were written for authorised external engagements — they are kept
for reference but are out of scope for CTF work and must not be used to query
real people or to test credentials anywhere.

## Step 0 — extract one pivot

Rank what the artifact contains by uniqueness, then take the top one:

1. An exact string: a handle, an unusual filename, a build identifier, an error
   message, a serial number.
2. Embedded metadata: `exiftool` on any image or document, document properties,
   author fields, timestamps, camera or software identifiers.
3. A visual detail: signage and its language, a licence plate format, road
   markings, architecture, vegetation, the position of the sun and shadows.
4. A network identifier: a domain, a certificate subject, a mail header, an
   address block.

A generic pivot — a common first name, a stock photo, a popular filename — costs
hours and yields nothing. Discard it and take the next one.

## Step 1 — one source per pivot

| Pivot | Source to work first | Depth |
|---|---|---|
| Handle or username | the platforms where that exact string exists, then the account's own posts | `../ctf-osint/social-media.md` |
| Photo or video | reverse image search, then terrain and signage matching | `../ctf-osint/geolocation-and-media.md` |
| Domain or host | certificate transparency, passive DNS, archived copies of the site | `../ctf-osint/web-and-dns.md` |
| Document | embedded metadata, then the revision history if the format keeps one | `references/search-dorking-cheatsheet.md` |
| Repository or commit | commit authors, timestamps, and content removed in later commits | `../ctf-osint/web-and-dns.md` |

## Step 2 — record before you pivot again

Write down the exact source URL and the exact span that supports each claim. An
OSINT chain built on a half-remembered match is how a wrong answer gets
submitted with confidence. Use `references/output-template.md` for the report
shape.

## Discipline

- One pivot at a time. Two half-followed pivots are worth less than one followed
  to the end.
- Distinguish confirmed from plausible in every note. A visual resemblance is not
  an identification.
- Stay inside the challenge scope. Do not contact anyone, do not query breach
  data about real people, and do not test any credential you find.
- Budget and escalation as in `../LOOP_DISCIPLINE.md`.
