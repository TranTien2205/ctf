---
name: osint-geolocation
description: >
  Action-oriented depth skill for Photo / video geolocation. Use after the router or tools/classify.py names this class; start with the first probe and record the expected signal. Do not use it as proof of a finding. Confusable classes: osint-media-metadata, osint-identity-pivot.
  Catalogue class: nothing in this toolkit has solved one yet.
tags: [osint, geolocation, ctf, bug-class]
environment: [ctf, lab, authorized-testing]
budget:
  stuck_threshold: 3
  on_stuck: pivot
  stop_conditions:
    - "same probe point: 3 attempts with no new signal"
    - "the class falsifier is observed"
evidence_level: catalogue
---
# Photo / video geolocation

**Catalogue class.** This toolkit has never solved one. What follows is
standard published knowledge, not local experience — treat it as a starting
point and record what actually happens in `field-notes.md`.

## First probe

reverse image search first — a hit names the place outright; only when that fails do you match terrain and signage by hand

**Falsifier** — the observation that closes this class: no unique landmark, text, plate, sun angle or terrain feature distinguishes the frame, and reverse search returns only generic matches
## Recognise

A photo or video frame is the artifact and the question is where it was
taken — a place, address, or coordinates. Geolocation is matching unique
visual detail against public imagery, not guessing a city.

## Confirm safely

Reads only; a claimed location is proven by a public source showing the same
unique feature — quote the matching detail and the source verbatim in the
report.

## Pivot order

1. `exiftool` — embedded GPS coordinates end the challenge in one command;
   record them before anything strips metadata.
2. Reverse image search (Google Lens, Yandex, Bing visual) — a hit names
   the place; check more than one engine.
3. Text in frame: signage language, shop names, plates, road markings,
   driving side, utility poles, terrain, vegetation.
4. Sun and shadow: hemisphere from shadow direction, rough latitude from
   length; combine with any timestamp metadata.
5. Architecture/infrastructure style, then map the candidate area against
   street-level imagery to confirm.

`references/visual-pivots.md` carries the per-feature table.

## Traps

- Reverse-search hits on similar-looking places are leads, not answers —
  confirm with an independent feature in the same frame.
- Metadata can be planted or stripped-and-readded — a GPS tag that disagrees
  with every visual cue is bait; trust the visuals.
- Screenshots and re-uploads carry no EXIF — say so and go visual; do not
  report a metadata negative as a geolocation negative.

## Operational probe

```bash
exiftool photo.jpg | grep -iE "gps|location|date|comment"
python3 -c "print(open('photo.jpg','rb').read()[:400])"  # sanity: real camera file?
```

## Routing

Shares signals with: `../osint-media-metadata/`, `../osint-identity-pivot/`. Check those before committing to this one.

Depth, one named file at a time. Route first:

- `skills/osint-geolocation/references/README.md` — the corpus index
- `skills/osint-geolocation/references/visual-pivots.md` — the per-feature table
- `skills/osint-geolocation/references/the-workflow.md` — the order: exiftool -> reverse search -> text/cues -> sun/shadow -> confirm
- `skills/osint-geolocation/references/the-map-index.md` — the full reference map

Cue guides — the-feature guides: `references/the-exif-first.md`,
`references/the-reverse.md`, `references/the-text.md`, `references/the-signage.md`, `references/the-plates.md`,
`references/the-roadmarks.md`, `references/the-driveside.md`, `references/the-poles.md`,
`references/the-terrain.md`, `references/the-vegetation.md`, `references/the-architecture.md`,
`references/the-sun.md`, `references/the-bollards.md`, `references/the-flags.md`. The feature modules
(`signage-`, `plates-`, `roadmarks-`, `driveside-`, `poles-`,
`bollards-`, `vehicles-`, `terrain-`, `vegetation-`,
`architecture-`, `signposts-`, `curbs-`, `sunshadow-`, `weather-`,
`script-`, `shops-`, `flags-`, `uniforms-`, `bins-`, `antennas-`)
cover feature × question pairs; the region modules (`reg-`) cover
region × feature pairs.

Discipline — the-standard modules: `references/the-confirm.md`, `references/the-lead-vs.md`,
`references/the-planted.md`, `references/the-no-exif.md`, `references/the-falsifier.md`,
`references/the-evidence.md`, `references/the-boundary.md`, `references/the-traps.md`,
`references/the-checklist.md`, `references/the-detection.md`, `references/the-worked.md`,
`references/the-close-geo.md`.

Signals that route here are in `knowledge/bug-classes.json`; classify with
`python3 tools/classify.py`. Budget and escalation: `../LOOP_DISCIPLINE.md`.

## Field notes

`field-notes.md` in this directory grows every time a challenge of this class
is solved. Entries marked `proposed` are awaiting review; entries marked
`confirmed` have been checked. See `../../LEARNING_LOOP.md`.
