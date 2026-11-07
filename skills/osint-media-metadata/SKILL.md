---
name: osint-media-metadata
description: >
  Action-oriented depth skill for Media and document metadata. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: osint-identity-pivot, misc-encoding-carrier.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [web, osint-media-metadata, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# Media and document metadata

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

run exiftool and read ALL of its output rather than grepping one tag, then binwalk and strings for appended or embedded data; steghide, zsteg and outguess are absent here, so never claim an extraction with them

**Falsifier** — the observation that closes this class: the metadata was stripped on upload and the carrier holds no appended data, so the answer is only in the visible frame and becomes a hypothesis rather than a measurement
## Recognise

A media or document file is the handout and the question asks for a fact about
it — where, when, on what device, or what was inside before it was shared.

## Confirm

Read **all** of the metadata, not one guessed tag: `exiftool` prints every
group, and the answer is often in an odd corner (`ThumbnailImage`,
`HistoryParameters`, a software string). Then the container itself — `binwalk`
and `strings` find appended archives and embedded payloads that metadata never
shows.

| Evidence surface | What it answers |
|---|---|
| EXIF / XMP groups | device, time, GPS, authoring software |
| embedded thumbnail | what the image showed before a crop or blur edit |
| appended data after the format's end marker | hidden archive or second file |
| document revision/author fields | identity and edit history |

Confirmation is the fact read verbatim from the file — a guess about what a GPS
coordinate names is a hypothesis until a map source confirms it.

## Traps

- Platforms strip metadata on upload; a clean file is evidence the question is
  in the visible frame, not that you missed a flag.
- The embedded thumbnail survives edits the main image does not — compare it.
- `steghide`, `zsteg` and `outguess` cover the common carriers but are not
  installed everywhere; `binwalk -e` and `strings` are the baseline that always
  runs.

## Operational probe

```bash
exiftool -a -u -g1 <file>
binwalk -e <file>
strings -n 6 <file> | grep -iE "flag|gps|key"
```

## Routing

Shares signals with: `../osint-identity-pivot/`, `../misc-encoding-carrier/`. Check those before committing to this one.

Depth, one named file at a time:

- `skills/ctf-osint/geolocation-and-media.md`
- `skills/osint-triage/references/tool-commands.md`

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
