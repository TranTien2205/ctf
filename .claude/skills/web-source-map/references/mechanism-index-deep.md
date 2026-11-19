# Mechanism index (deep) — every recon sub-mechanism catalogued

## The discovery mechanisms

| # | Mechanism | Detects | File |
|---|---|---|---|
| M1 | entry inventory | the bundle set | `detection.md` |
| M2 | manifest inventory | every route+chunk | `detection-deep.md`, `service-worker-mining.md` |
| M3 | build fingerprint | the bundler/framework | `bundle-formats.md`, `frameworks.md` |
| M4 | map recovery | the `.map` + its routes | `source-maps.md`, `source-maps-deep.md` |
| M5 | source reconstruction | `sourcesContent` → real source | `mechanism-deep.md`, `source-maps-deep.md` |

## The mining mechanisms

| # | Mechanism | Mines | File |
|---|---|---|---|
| M6 | endpoint mining | the route table | `endpoint-inventory.md`, `endpoint-inventory-deep.md`, `per-endpoint-class.md` |
| M7 | param mining | the request params | `param-surface.md`, `per-param.md` |
| M8 | secret mining | credential candidates | `secrets.md`, `secrets-deep.md`, `secrets-catalogue.md`, `per-secret-class.md` |
| M9 | flag/gate mining | the gated surface | `flag-mining.md`, `route-guard.md` |
| M10 | config mining | env/config values | `config-mining.md`, `per-prefix.md` |
| M11 | structure mining | the app layout | `structure-mining.md` |
| M12 | comment mining | dev notes/flag | `comment-mining.md` |
| M13 | sink mining | the vuln sink | `sink-mining.md`, `per-sink.md` |
| M14 | GraphQL mining | the schema hints | `graphql-surface.md` |

## The verify/route mechanisms

| # | Mechanism | Does | File |
|---|---|---|---|
| M15 | lead triage | ranks leads | `lead-triage.md`, `per-target.md` |
| M16 | live verify | falsifier per lead | `verification-protocol.md`, `per-check.md`, `per-check-deep.md` |
| M17 | route | each lead → its class | `per-target-deep.md`, `class-boundary.md` |

## The context mechanisms

| # | Mechanism | Does | File |
|---|---|---|---|
| M18 | adjacent disclosure | probes `.git`/`.env`/backups | `adjacent-disclosure.md` |
| M19 | authenticated bundle | mines behind the login | `authenticated-bundle.md` |
| M20 | dev-build mining | the richer dev bundle | `dev-build.md` |
| M21 | deobfuscation | reads a resistant bundle | `deobfuscation.md`, `obfuscation-formats.md` |

## The flat index

See `mechanism-index.md` for the short list, `mechanism-map.md` for the
dependency graph, `per-mechanism-deep.md` for each in detail.
