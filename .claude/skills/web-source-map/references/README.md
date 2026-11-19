# references/ — web-source-map corpus index

Front-end bundle + source-map recon. A bundle is a map to the surface —
this corpus is the read of it. Every lead is a candidate until verified
live; every dead lead is a recorded negative. **Catalogue class** — no
local verified solve; `verified-chains.md` is the honest record.

## Mechanism

`mechanism.md`, `mechanism-deep.md` — what a bundle and a `.map` are;
the v3 spec, `sources`/`names`/`mappings`/`sourcesContent`, scheme
handling, the traversal rejection, why the map is attacker-controlled.
`bundle-lifecycle.md` — the build pipeline (transpile→bundle→minify→
map→split→hash→deploy) and what each stage leaves. `mechanism-index.md`,
`mechanism-index-deep.md`, `mechanism-map.md`, `mechanism-catalogue.md` —
the sub-mechanism index and the per-mechanism detail.

## Detection and inventory

`detection.md`, `detection-deep.md`, `detection-matrix.md`,
`detection-index.md`, `detection-index-deep.md`, `detection-checklist.md`,
`detection-checklist-deep.md`, `detection-surface.md`,
`detection-surface-deep.md`, `detection-map.md`, `detection-playbook.md`,
`per-file.md`, `per-artifact.md`, `bundle-formats.md`, `frameworks.md`.

## The `.map` and source recovery

`source-maps.md`, `source-maps-deep.md`, `map-playbook.md` — the
`sourceMappingURL` comment, the sibling `.map`, the `SourceMap` header,
`/static/maps/`, the inline `data:` map; `sourcesContent` reconstruction;
the catch-all and the scheme/traversal reject.

## Extraction and mining

`extraction.md`, `extraction-deep.md`, `extraction-index.md`,
`extraction-playbook.md`, `extended-greps.md`, `bundle-mining.md`,
`bundle-mining-deep.md`, `endpoint-inventory.md`,
`endpoint-inventory-deep.md`, `endpoint-playbook.md`,
`per-endpoint-class.md`, `param-surface.md`, `per-param.md`,
`secrets.md`, `secrets-deep.md`, `secrets-catalogue.md`,
`secrets-playbook.md`, `per-secret-class.md`, `flag-mining.md`,
`flag-playbook.md`, `route-guard.md`, `route-table.md`, `per-route.md`,
`per-route-deep.md`, `config-mining.md`, `per-prefix.md`,
`structure-mining.md`, `comment-mining.md`, `sink-mining.md`,
`per-sink.md`, `graphql-surface.md`, `service-worker-mining.md`,
`adjacent-disclosure.md`, `authenticated-bundle.md`, `dev-build.md`,
`deobfuscation.md`, `obfuscation-formats.md`.

## Framework internals

`webpack-internals.md`, `nextjs-internals.md`, `vite-internals.md`,
`vue-internals.md`, `angular-internals.md` — the per-build artifact
names, the manifest shapes, the lazy-chunk layout, the env-inline style.

## Workflow

`workflow.md`, `workflow-deep.md`, `workflow-checklist.md`,
`workflow-playbook.md`, `workflow-map.md`, `playbook.md`,
`first-hour.md`, `first-hour-deep.md`, `field-manual.md`,
`field-manual-deep.md`, `field-manual-map.md`, `checklist.md`,
`checklist-deep.md`, `field-checklist.md`, `quick-reference.md`,
`quick-reference-deep.md`, `quick-map.md`, `preconditions.md`,
`preconditions-deep.md`, `onboarding.md`, `onboarding-deep.md`,
`probe-catalogue.md`, `payload-patterns.md`, `decision-table.md`,
`operator-notes.md`, `closing-notes.md`, `worked-examples.md`,
`lead-grammar.md`, `recon-order.md`, `extended-corpus.md`, `index.md`.

## Lead → class routing

`lead-triage.md`, `per-target.md`, `per-target-deep.md`, `per-check.md`,
`per-check-deep.md`, `per-surface.md`, `per-surface-deep.md`,
`per-surface-map.md`, `per-vector.md`, `per-vector-deep.md`,
`per-boundary.md`, `per-mechanism-deep.md`, `attack-shapes.md`,
`attack-shapes-deep.md`, `multi-step-chains.md`,
`multi-step-chains-deep.md`, `scenarios.md`, `class-boundary.md`,
`class-boundary-deep.md`, `field-notes-deep.md`.

## Discipline

`evidence-rules.md`, `evidence-deep.md`, `evidence-map.md`,
`evidence-playbook.md`, `verification-protocol.md`, `falsifiers.md`,
`falsifiers-deep.md`, `per-falsifier.md`, `per-falsifier-deep.md`,
`falsifier-map.md`, `negative-results.md`, `negative-results-deep.md`,
`negative-map.md`, `edge-cases.md`, `edge-cases-deep.md`,
`common-mistakes.md`, `common-mistakes-deep.md`, `anti-patterns.md`,
`troubleshoot.md`, `troubleshoot-deep.md`, `troubleshooting-map.md`,
`evasion.md`, `evasion-deep.md`, `evasion-deep-2.md`,
`case-studies.md`, `case-studies-deep.md`, `real-world-cases.md`,
`real-world-deep.md`, `verified-chains.md`.

## Reference

`theory.md`, `theory-deep.md`, `glossary.md`, `glossary-deep.md`,
`summary.md`, `summary-deep.md`, `common-questions.md`,
`common-questions-deep.md`, `mechanism-index.md`,
`mechanism-index-deep.md`, `mechanism-map.md`, `mechanism-catalogue.md`.

## The rules

1. the map is **recon**, not the exploit
2. **verify every lead live**
3. a **secret is a candidate** until it authenticates
4. **never execute** the recovered source
5. **catalogue** — no local verified solve
