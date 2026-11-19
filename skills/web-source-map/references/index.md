# Index — the full corpus map

## Core

- `mechanism.md`, `mechanism-deep.md` — what a bundle and a `.map` are;
  the v3 spec, `sourcesContent`, scheme handling, traversal rejection
- `detection.md`, `detection-deep.md`, `detection-matrix.md`,
  `detection-index.md`, `detection-index-deep.md`, `detection-checklist.md`,
  `detection-checklist-deep.md`, `detection-surface.md`,
  `detection-surface-deep.md`, `detection-map.md`, `detection-playbook.md`
- `extraction.md`, `extraction-deep.md`, `extraction-index.md`,
  `extraction-playbook.md`, `extended-greps.md`, `bundle-mining.md`,
  `bundle-mining-deep.md`, `bundle-formats.md`
- `source-maps.md`, `source-maps-deep.md`, `map-playbook.md`
- `secrets.md`, `secrets-deep.md`, `secrets-catalogue.md`,
  `secrets-playbook.md`, `per-secret-class.md`
- `frameworks.md`, `webpack-internals.md`, `nextjs-internals.md`,
  `vite-internals.md`, `vue-internals.md`, `angular-internals.md`

## Workflow

- `workflow.md`, `workflow-deep.md`, `workflow-checklist.md`,
  `workflow-playbook.md`, `workflow-map.md`, `playbook.md`
- `first-hour.md`, `first-hour-deep.md`, `field-manual.md`,
  `field-manual-deep.md`, `field-manual-map.md`, `quick-map.md`

## The mining surfaces

- `endpoint-inventory.md`, `endpoint-inventory-deep.md`,
  `endpoint-playbook.md`, `per-endpoint-class.md`
- `param-surface.md`, `per-param.md`
- `config-mining.md`, `per-prefix.md`
- `flag-mining.md`, `route-guard.md`, `flag-playbook.md`
- `route-table.md`, `per-route.md`, `per-route-deep.md`
- `structure-mining.md`, `comment-mining.md`, `sink-mining.md`,
  `per-sink.md`, `graphql-surface.md`
- `service-worker-mining.md`, `adjacent-disclosure.md`,
  `authenticated-bundle.md`, `dev-build.md`, `deobfuscation.md`,
  `obfuscation-formats.md`, `per-file.md`

## Leads → classes

- `lead-triage.md`, `per-target.md`, `per-target-deep.md`,
  `per-check.md`, `per-check-deep.md`, `per-surface.md`,
  `per-surface-deep.md`, `per-surface-map.md`, `per-vector.md`,
  `per-vector-deep.md`, `per-mechanism-deep.md`, `per-boundary.md`
- `attack-shapes.md`, `attack-shapes-deep.md`, `multi-step-chains.md`,
  `multi-step-chains-deep.md`, `scenarios.md`

## Discipline

- `evidence-rules.md`, `evidence-deep.md`, `evidence-map.md`,
  `evidence-playbook.md`, `verification-protocol.md`
- `falsifiers.md`, `falsifiers-deep.md`, `per-falsifier.md`,
  `per-falsifier-deep.md`, `falsifier-map.md`
- `negative-results.md`, `negative-results-deep.md`, `negative-map.md`
- `edge-cases.md`, `edge-cases-deep.md`, `common-mistakes.md`,
  `common-mistakes-deep.md`, `anti-patterns.md`
- `troubleshoot.md`, `troubleshoot-deep.md`, `troubleshooting-map.md`,
  `evasion.md`, `evasion-deep.md`
- `case-studies.md`, `case-studies-deep.md`, `real-world-cases.md`,
  `real-world-deep.md`, `verified-chains.md`

## Reference

- `theory.md`, `theory-deep.md`, `glossary.md`, `glossary-deep.md`,
  `summary.md`, `summary-deep.md`, `onboarding.md`, `onboarding-deep.md`,
  `checklist.md`, `checklist-deep.md`, `quick-reference.md`,
  `quick-reference-deep.md`, `preconditions.md`, `preconditions-deep.md`,
  `common-questions.md`, `common-questions-deep.md`,
  `mechanism-index.md`, `mechanism-index-deep.md`, `mechanism-map.md`,
  `mechanism-catalogue.md`, `class-boundary.md`, `class-boundary-deep.md`,
  `recon-order.md`, `extended-corpus.md`, `index.md`, `README.md`

## The rules

1. the map is **recon, not the exploit**
2. **verify every lead live**
3. a **secret is a candidate** until it authenticates
4. the source is **attacker-controlled** — read, never execute
5. **catalogue** — no local verified solve
