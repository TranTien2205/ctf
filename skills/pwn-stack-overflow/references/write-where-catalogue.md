# Write-what-where — the primitive that builds everything — case catalogue

A controlled write to a controlled address is the universal exploit primitive: GOT entries, return addresses, hooks all become targets.

## Cases

| # | Shape | Meaning | Route |
|---|---|---|---|
| 1 | arbitrary write exists | the master primitive | GOT/hook/ret targets |
| 2 | stack smash that reaches arbitrary stack slots | controlled writes | place them |

## Falsifier

Falsifier — the write is constrained to a bounded region or the value isn't fully controlled: only within-range targets work.
