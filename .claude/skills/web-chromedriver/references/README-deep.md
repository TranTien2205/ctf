# README deep — the corpus map, annotated

## The corpus at a glance

`web-chromedriver` is a verified-class skill — the local-bot-debugging
and channel-check discipline is anchored by `apexsurvive` and
`tornadoservice`. The corpus covers the browser-control layer in both
its uses: a local reproduction for debugging a client-side payload,
and an exposed WebDriver endpoint as a file-read/loopback capability.

## The modules by role

### The mechanism layer

- `mechanism.md` — what a driven browser is; the two uses
- `mechanism-deep.md` — the internals: serialisation, frames, jar, process
- `mechanism-deep-2.md` — the architecture: the three-layer stack
- `mechanism-catalogue.md` — every primitive, indexed
- `mechanism-alphabet.md` — the primitives A–Z
- `mechanism-index.md` — the primitive catalogue, indexed

### The detection layer

- `detection.md` — is an endpoint exposed / is a bot worth it
- `detection-deep.md` — the endpoint hunt in detail
- `detection-deep-2.md` — the endpoint and bot taxonomy
- `detection-matrix.md` — the signal x use grid
- `detection-matrix-deep.md` — the full signal grid
- `detection-surface.md` — where to look
- `detection-surface-deep.md` — every hiding place
- `detection-index.md` — the ordered probe list
- `detection-checklist.md` — the run-down
- `detection-workflows.md` — the hunt, end to end
- `detection-playbook.md` — the ordered procedure

### The control layer

- `webdriver-api.md` — the endpoint cheat sheet
- `library-drivers.md` — Selenium / Playwright
- `capabilities.md` — the session capability reference
- `chrome-flags.md` — the flags and their reproduction
- `session-management.md` — lifecycle, leaks, shared instances
- `cdp.md` — DevTools protocol when WebDriver is not enough
- `grid-remote.md` — the shared/exposed variant
- `multi-page.md` — frames, pages, contexts

### The use layer

- `local-bot.md` — reproduce the challenge's bot
- `local-bot-deep.md` — the reproduction engineering detail
- `attack-surface.md` — the endpoint as target
- `attack-surface-deep.md` — the exposed endpoint's full reach
- `observability.md` — console/DOM/network
- `observability-deep.md` — extracting max signal
- `payload-development.md` — the debug loop
- `payload-development-deep.md` — the iteration discipline
- `payload-variants.md` — the exfil and probe library
- `payload-variants-deep.md` — the payload library, annotated
- `payload-dictionary.md` — the payload set, indexed

### The map layer

- `per-mechanism.md` / `per-mechanism-deep.md` — the primitives
- `per-check.md` / `per-check-deep.md` — the gates
- `per-route.md` / `per-route-deep.md` — the route map
- `per-endpoint.md` / `per-endpoint-deep.md` — the endpoints
- `per-surface.md` / `per-surface-deep.md` — the reach
- `per-boundary.md` / `per-boundary-deep.md` — the class edges
- `per-vector.md` / `per-vector-deep.md` — the channels
- `per-falsifier.md` — the kill map
- `falsifier-map.md` — the kill map at a glance
- `evidence-map.md` — what proves each claim
- `field-inventory.md` — the inputs and outputs
- `carrier-catalogue.md` — the carriers a flag travels by
- `decision-map.md` — every fork
- `probe-matrix.md` — the probe set, indexed

### The discipline layer

- `workflow.md` / `workflow-deep.md` / `workflow-checklist.md` /
  `workflow-checklist-deep.md` / `workflow-scenarios.md` — the run
- `evidence-rules.md` / `evidence-rules-deep.md` — what counts
- `falsifiers.md` / `falsifiers-deep.md` — what kills it
- `negative-results.md` / `negative-results-deep.md` — the dead ends
- `edge-cases.md` / `edge-cases-deep.md` / `edge-catalogue.md` /
  `edge-catalogue-2.md` — the unusual states
- `common-mistakes.md` / `common-mistakes-deep.md` — the misapplications
- `troubleshoot.md` / `troubleshoot-deep.md` / `troubleshoot-scenarios.md` /
  `troubleshoot-playbook.md` — the fixes
- `evasion.md` / `evasion-deep.md` / `evasion-scenarios.md` — the pivots
- `anti-patterns.md` / `anti-patterns-deep.md` — the named mistakes
- `class-boundary.md` — where it ends

### The context layer

- `attack-shapes.md` / `attack-shapes-deep.md` — the named patterns
- `multi-step-chains.md` / `multi-step-chains-deep.md` — the staged shapes
- `case-studies.md` / `case-studies-deep.md` — the anchors
- `real-world-cases.md` / `real-world-cases-deep.md` — the patterns
- `verified-chains.md` — the honest status
- `whitebox-hunt.md` — finding the driver/bot in source
- `exploitation-playbook.md` — the end-to-end runs

### The reference layer

- `theory.md` / `theory-deep.md` — why it works
- `glossary.md` / `glossary-deep.md` — the terms
- `summary.md` / `summary-deep.md` / `summary-checklist.md` — the one page
- `onboarding.md` / `onboarding-deep.md` — the first session
- `first-hour.md` / `first-hour-deep.md` — the sixty minutes
- `preconditions.md` / `preconditions-deep.md` — what must be true
- `common-questions.md` / `common-questions-deep.md` — the FAQ
- `checklist.md` — the run-down
- `quick-reference.md` / `quick-reference-deep.md` / `quick-check.md` —
  the card
- `field-manual.md` / `field-manual-deep.md` — the ops runbook
- `extended-corpus.md` — the full command/pattern library
- `README.md` — the index

## The two anchors

- `apexsurvive` — local-bot debugging -> a stored-XSS -> RCE chain
- `tornadoservice` — the tunnel interstitial that costs bot visits
