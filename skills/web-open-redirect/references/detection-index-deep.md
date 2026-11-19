# Detection index (deep) — the complete cross-reference

## The full file inventory — every reference, its role

```text
CORE MODEL:
  mechanism.md              the gap the redirect produces
  mechanism-deep.md         the component-by-component model
  mechanism-map.md          the component -> arm map
  mechanism-index.md        the component -> file index
  theory.md                 the trust-laundering why
  class-boundary.md         the sibling-class boundary
  glossary.md               the vocabulary

DETECTION:
  detection.md              the parameter/carrier signals
  detection-deep.md         the systematic sweep
  detection-matrix.md       the signal -> confidence -> probe
  detection-index.md        the signal -> file map
  detection-catalogue.md    the signal catalogue
  detection-map.md          the navigation map
  detection-signals.md      the observable signals
  detection-surface.md      the surface inventory
  detection-verdicts.md     the verdict vocabulary
  detection-playbook.md     the ordered runbook
  detection-checklist.md    the verification pass
  detection-workflow.md     the decision procedure
  detection-index-deep.md   this file

THE BYPASS CORPUS:
  filter-bypasses.md        the base bypass alphabet (pre-existing)
  filter-bypass-deep.md     the full check-shape × arm matrix
  per-check.md              the per-check arms
  per-vector.md             the per-vector payload families
  per-boundary.md           the parser-boundary arms
  per-target.md             the allowlist/read arms
  payload-dictionary.md     the full payload dictionary
  payload-variants.md       the arm-generation
  encoding-attacks.md       the decode-order arms
  evasion.md                the residual arms
  parser-differentials.md   the two-parser gaps
  framework-matrix.md       the per-framework checks

THE CARRIERS:
  client-side.md            the meta/JS/hash twins
  stored-and-referer.md     the two-step + the header-carried
  edge-cases.md             the unusual carriers
  per-channel.md            the input channels
  per-mechanism.md          the per-mechanism detail

THE CHAINS:
  chain-routes.md           the OAuth/SSRF/XSS/bot/phishing routes
  per-route.md              the per-route reachability
  multi-step-chains.md      the two/three-hop chains
  attack-shapes.md          the canonical exploits
  exploitation.md           the confirm-to-flag procedure

DISCIPLINE:
  evidence-rules.md         the verbatim-Location standard
  evidence-rules-deep.md    the evidence hierarchy
  falsifiers.md             the class-closing observations
  falsifiers-deep.md        the complete falsifier treatment
  per-falsifier.md          the per-falsifier arms
  negative-results.md       the negative taxonomy
  negative-results-deep.md  the full negative treatment
  negative-map.md           the negative navigation
  workflow.md               the ordered steps
  workflow-deep.md          the full procedure
  detection-workflow.md     the detection decision-procedure
  field-manual.md           the operating procedure
  first-hour.md             the 60-minute pass
  recon-order.md            the ordered recon
  checklist.md              the verification checklist
  detection-checklist.md    the detection checklist
  quick-reference.md        the 60-second pass
  onboarding.md             the first 15 minutes
  edge-cases.md             the unusual surfaces
  common-mistakes.md        the ways it goes wrong
  anti-patterns.md          the approaches that fail
  troubleshoot.md           the when-it-fails
  common-questions.md       the operator confusions
  case-studies.md           the named shapes
  real-world-cases.md       the documented cases
  verified-chains.md        the honest local state
  field-notes-deep.md       the learning-loop
  decision-table.md         the fingerprint -> arm -> verdict
  lead-grammar.md           the observation phrasing
  probe-catalogue.md        the probe list
  probe-map.md              the probe -> observation map
  per-falsifier.md          the per-falsifier detail
  per-mechanism.md          the per-mechanism detail
  summary.md                the one-page
```

## The task → the file chain

```text
"I have a redirect-param" -> param-inventory.md -> per-endpoint.md ->
  detection.md -> the canary -> decision-table.md -> the arm ->
  evidence-rules-deep.md
```

```text
"the Location is safe" -> falsifiers.md -> the arm -> per-check.md ->
  the residual -> evasion.md -> the uniform falsifier ->
  negative-results-deep.md
```

```text
"I want the chain" -> chain-routes.md -> per-route.md -> the reachability
  -> multi-step-chains.md -> the flag
```

```text
"the client-side" -> client-side.md -> the meta/JS/hash -> the DOM-sink ->
  the evidence
```

```text
"the framework check" -> framework-matrix.md -> the check-API -> the arms
```
