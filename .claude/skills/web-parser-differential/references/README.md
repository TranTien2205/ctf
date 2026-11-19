# Parser differential reference map

This directory belongs to the canonical `web-parser-differential` class skill.
Open one named file after the first probe; do not read the whole directory.

## Choose by observed signal

| Signal or task | Open |
|---|---|
| A path, route or host value is parsed twice | `path-normalization.md`, then `normalization.md` |
| A proxy adds a trust header the backend believes | `proxy-header-abuse.md`, then `proxy-trust.md`, then `client-supplied.md` |
| The front and back ends may disagree on the HTTP version or the vhost | `protocol-and-vhost.md` |
| A structured value (cookie, email header, token) is decoded differently at two layers | `structured-field-differentials.md` |
| The flag is in a header or path the client cannot set directly | `proxy-header-abuse.md`, then `path-normalization.md` |
| A proxy header named in Connection is stripped | `hop-by-hop.md`, then `hop-by-hop-deep.md` |
| The app's trust check reads a proxy header | `detection.md`, then `detection-deep.md`, then `detection-checklist.md` |
| The app's trust check's input is a header | `per-surface.md`, then `per-surface-deep.md` |
| The app's trust check's input is a check | `per-check.md`, then `per-check-deep.md` |
| The app's trust check's input is a route | `per-route.md` |
| The app's trust check's input is a header | `per-header.md`, then `per-header-deep.md` |
| The app's trust check's input is a boundary | `per-boundary.md` |
| The app's trust check's input is a vector | `per-vector.md`, then `per-vector-deep.md` |
| The app's trust check's input is a mechanism | `per-mechanism.md`, then `per-mechanism-deep.md` |
| The app's trust check's input is a falsifier | `per-falsifier.md` |
| The proxy's behavior is a header | `per-proxy.md`, then `per-proxy-deep.md` |
| The proxy's behavior is a matrix | `framework-matrix.md`, then `framework-matrix-deep.md` |
| The differential's mechanism is a shape | `exploitation.md`, then `exploitation-playbook.md`, then `exploitation-shapes.md` |
| The differential's mechanism is a chain | `multi-step-chains.md` |
| The differential's mechanism is a case | `case-studies.md`, then `case-studies-deep.md` |
| The differential's mechanism is a verified chain | `verified-chains.md` |
| The differential's mechanism is a real-world case | `real-world-cases.md` |
| The differential's mechanism is a whitebox hunt | `whitebox-hunt.md` |
| The differential's mechanism is an evidence rule | `evidence-rules.md` |
| The differential's mechanism is a verification | `verification.md` |
| The differential's mechanism is a negative result | `negative-results.md`, then `negative-results-deep.md` |
| The differential's mechanism is a common mistake | `common-mistakes.md` |
| The differential's mechanism is a common question | `common-questions.md` |
| The differential's mechanism is a class boundary | `class-boundary.md`, then `class-boundary-deep.md` |
| The differential's mechanism is a troubleshoot | `troubleshoot.md`, then `troubleshoot-deep.md` |
| The differential's mechanism is a theory | `theory.md`, then `theory-deep.md` |
| The differential's mechanism is a workflow | `workflow.md`, then `workflow-deep.md` |
| The differential's mechanism is a field manual | `field-manual.md` |
| The differential's mechanism is a glossary | `glossary.md` |
| The differential's mechanism is a summary | `summary.md` |
| The differential's mechanism is a detection matrix | `detection-matrix.md` |
| The differential's mechanism is a detection surface | `detection-surface.md` |
| The differential's mechanism is a detection index | `detection-index.md` |
| The differential's mechanism is a detection checklist | `detection-checklist.md` |
| The differential's mechanism is a detection deep | `detection-deep.md` |
| The differential's mechanism is a detection | `detection.md` |
| The differential's mechanism is a header dictionary | `header-dictionary.md` |
| The differential's mechanism is a normalization | `normalization.md` |
| The differential's mechanism is a path normalization | `path-normalization.md` |
| The differential's mechanism is a protocol and vhost | `protocol-and-vhost.md` |
| The differential's mechanism is a structured field | `structured-field-differentials.md` |
| The differential's mechanism is an edge case | `edge-cases.md` |
| The differential's mechanism is a per-surface | `per-surface.md` |
| The differential's mechanism is a per-check | `per-check.md` |
| The differential's mechanism is a per-route | `per-route.md` |
| The differential's mechanism is a per-header | `per-header.md` |
| The differential's mechanism is a per-boundary | `per-boundary.md` |
| The differential's mechanism is a per-vector | `per-vector.md` |
| The differential's mechanism is a per-mechanism | `per-mechanism.md` |
| The differential's mechanism is a per-falsifier | `per-falsifier.md` |
| The differential's mechanism is a per-proxy | `per-proxy.md` |
| The differential's mechanism is a per-mechanism-index | `per-mechanism-index.md` |

## Loading rule

The `../SKILL.md` file is enough for routine recognition and the first probe.
Open a file here only when the differential needs a concrete request pair, a
named proxy behaviour, or a falsifier wording.

Every technique in this directory was distilled from a confirmed or proposed
field note in `../field-notes.md`; the probe pairs below are the ones that
actually worked on a live target.
