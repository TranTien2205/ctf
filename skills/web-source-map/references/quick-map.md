# Quick map — the one-page corpus map

## The task → the file, in one line each

| I need to | Open |
|---|---|
| know what this class is | `mechanism.md`, `theory.md`, `onboarding.md` |
| find the bundles | `detection.md`, `detection-playbook.md` |
| fingerprint the build | `bundle-formats.md`, `frameworks.md` |
| get the `.map` | `source-maps.md`, `map-playbook.md` |
| mine endpoints | `endpoint-inventory.md`, `extraction.md`, `endpoint-playbook.md` |
| mine params | `param-surface.md`, `per-param.md` |
| mine secrets | `secrets.md`, `secrets-playbook.md`, `secrets-catalogue.md` |
| mine flags/gates | `flag-mining.md`, `route-guard.md`, `flag-playbook.md` |
| mine config/env | `config-mining.md`, `per-prefix.md` |
| get the routes | `route-table.md`, `per-route.md` |
| read the app layout | `structure-mining.md` |
| read the comments | `comment-mining.md` |
| find the sinks | `sink-mining.md`, `per-sink.md` |
| GraphQL | `graphql-surface.md` |
| a service worker | `service-worker-mining.md` |
| an adjacent artifact | `adjacent-disclosure.md` |
| an authed bundle | `authenticated-bundle.md` |
| a dev build | `dev-build.md` |
| an obfuscated bundle | `deobfuscation.md`, `obfuscation-formats.md` |
| run the whole pass | `workflow.md`, `workflow-playbook.md`, `field-manual.md`, `first-hour.md` |
| verify a lead | `verification-protocol.md`, `evidence-playbook.md`, `per-check.md` |
| rank the leads | `lead-triage.md` |
| route a lead | `per-endpoint-class.md`, `per-secret-class.md`, `per-param.md` |
| the falsifiers | `falsifiers.md`, `per-falsifier.md`, `falsifier-map.md` |
| record a dead end | `negative-results.md`, `negative-map.md` |
| an edge case | `edge-cases.md`, `evasion.md`, `evasion-deep-2.md` |
| a mistake | `common-mistakes.md`, `anti-patterns.md` |
| a fix | `troubleshoot.md`, `troubleshooting-map.md` |
| the boundary | `class-boundary.md`, `per-boundary.md`, `recon-order.md` |
| a checklist | `checklist.md`, `field-checklist.md`, `detection-checklist.md` |
| a lookup | `quick-reference.md`, `glossary.md`, `summary.md`, `decision-table.md`, `probe-catalogue.md`, `payload-patterns.md`, `extended-greps.md`, `mechanism-catalogue.md`, `operator-notes.md`, `closing-notes.md` |
| the honest status | `verified-chains.md` |

## The deep/second-tier files

Every `-deep` / `index` / `map` / `playbook` variant of the above —
`detection-deep.md`, `extraction-deep.md`, `secrets-deep.md`,
`workflow-deep.md`, `per-route-deep.md`, `multi-step-chains-deep.md`,
`case-studies-deep.md`, `real-world-deep.md`, `evidence-deep.md`,
`falsifiers-deep.md`, `negative-results-deep.md`, `edge-cases-deep.md`,
`common-mistakes-deep.md`, `troubleshoot-deep.md`, `evasion-deep.md`,
`theory-deep.md`, `glossary-deep.md`, `summary-deep.md`,
`onboarding-deep.md`, `checklist-deep.md`, `quick-reference-deep.md`,
`preconditions-deep.md`, `detection-checklist-deep.md`,
`common-questions-deep.md`, `per-mechanism-deep.md`, `per-check-deep.md`,
`per-surface-deep.md`, `per-vector-deep.md`, `per-target-deep.md`,
`per-falsifier-deep.md`, `attack-shapes-deep.md`,
`endpoint-inventory-deep.md`, `bundle-mining-deep.md`,
`source-maps-deep.md`, `mechanism-deep.md`, `field-manual-deep.md`,
`first-hour-deep.md`, `field-notes-deep.md`, `detection-index-deep.md`,
`mechanism-index-deep.md`, `detection-surface-deep.md`,
`class-boundary-deep.md`.

## The five rules

1. the map is **recon**, not the exploit
2. **verify every lead live**
3. a **secret is a candidate** until it authenticates
4. **never execute** the recovered source
5. **catalogue** — no local verified solve
