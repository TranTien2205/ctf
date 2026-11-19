# Write-what-where — the primitive that builds everything — map


## Signals

| Observation | Meaning | Route |
|---|---|---|
| arbitrary write exists | the master primitive | GOT/hook/ret targets |
| stack smash that reaches arbitrary stack slots | controlled writes | place them |

## Falsifier

Falsifier — the write is constrained to a bounded region or the value isn't fully controlled: only within-range targets work.
