# Visual pivots, ranked by uniqueness

## Step order

1. **EXIF first** — `exiftool` GPS tags end the challenge; check before
   anything else, and re-check on the ORIGINAL file (re-uploads strip).
2. **Reverse image search** — Google Lens, Yandex, Bing Visual Search.
   Different engines, different indexes — a Lens miss is not a miss.
3. **Text in frame** — signage, shop names, license plates, road signs.
   Language first (country), then the actual words (a business name is
   searchable to a street address).
4. **Infrastructure style** — utility poles, road markings, bollards,
   driving side, streetlight arms, guardrail type. GeoGuessr-style
   checklists (geohints, plonkit guides) name which detail pins which
   country.
5. **Sun and terrain** — shadow direction (hemisphere), shadow length
   (rough latitude/time), vegetation, terrain color, mountain profiles.
6. **Confirm** — two independent features agree, then verify the candidate
   on street-level or satellite imagery and quote both matches.

## Feature table

| Feature | What it bounds |
|---|---|
| driving side + plate shape | country cluster |
| language + script on signs | country/region |
| pole & road-marking style | country (plonkit tables) |
| sun/shadow + timestamp | hemisphere + rough latitude |
| business name in frame | street address via search/maps |
| vegetation + terrain + roof style | climate band |
| mountain/coast profile | candidate area for satellite sweep |

## Evidence standard

The finding is "this location, because feature X in the frame matches
source Y at these coordinates" — two independent matches minimum. A
reverse-image hit alone, unconfirmed by a second feature in the same frame,
is a lead.
