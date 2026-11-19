# Mechanism map — the recon sub-mechanisms and how they connect

## The map

```
                        ┌──────────────┐
                        │  inventory   │  M1 — the bundle set
                        └──────┬───────┘
                               │
              ┌────────────────┼────────────────┐
              │                                 │
        ┌─────▼─────┐                    ┌──────▼─────┐
        │ map path  │                    │ string path │
        │ M2 map    │                    │ M4 endpoint │
        │ recovery  │                    │ mining      │
        └─────┬─────┘                    │ M5 secret   │
              │                          │ M6 flag     │
        ┌─────▼─────┐                    │ M8 config   │
        │ M3 source │                    └──────┬─────┘
        │reconstruct│                           │
        └─────┬─────┘                           │
              │                          ┌──────▼─────┐
        ┌─────▼─────┐                    │  leads     │
        │ M7 layout │                    └──────┬─────┘
        │ M9 comment│                           │
        │ M10 sink  │                    ┌──────▼─────┐
        └─────┬─────┘                    │ verify +   │
              │                          │ route      │
              └─────────────────────────►└────────────┘
```

## The two paths

**Map path** (M2→M3): the `.map` exists → reconstruct `sourcesContent`
→ read real source. Then M7 (layout), M9 (comments), M10 (sinks) apply
to the recovered source.

**String path** (M4/M5/M6/M8): no map → grep every bundle for
endpoints, secrets, flags, config literals.

Both feed the same lead list → verify → route.

## The dependency

| Mechanism | Needs |
|---|---|
| M1 inventory | the entry page + manifests |
| M2 map recovery | M1's bundle set |
| M3 reconstruction | a real `.map` + `sourcesContent` |
| M4-M8 string mining | the fetched bundles |
| M7 layout | a `.map` (even without content) |
| M9 comments | `sourcesContent` |
| M10 sinks | `sourcesContent` or beautified source |

## The sub-mechanism index

| # | Mechanism | File |
|---|---|---|
| M1 | inventory | `detection.md`, `detection-deep.md` |
| M2 | map recovery | `source-maps.md`, `mechanism-deep.md` |
| M3 | source reconstruction | `source-maps.md`, `mechanism-deep.md` |
| M4 | endpoint mining | `endpoint-inventory.md`, `endpoint-inventory-deep.md`, `extraction.md` |
| M5 | secret mining | `secrets.md`, `secrets-deep.md`, `secrets-catalogue.md` |
| M6 | flag/gate mining | `flag-mining.md`, `route-guard.md` |
| M7 | structure mining | `structure-mining.md` |
| M8 | config mining | `config-mining.md` |
| M9 | comment mining | `comment-mining.md` |
| M10 | sink mining | `sink-mining.md` |

See `mechanism-index.md` for the flat list and `per-mechanism-deep.md`
for each in detail.
