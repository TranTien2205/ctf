# web-websocket — references index

The corpus for the WebSocket / realtime-API class. One named file at a
time — load the file that matches the question; do not load the whole
corpus.

## The model

- `mechanism.md` / `mechanism-deep.md` — the two trust surfaces + the four gap classes
- `theory.md` / `theory-deep.md` — the protocol model, formalized
- `summary.md` / `summary-deep.md` — the class in one page
- `glossary.md` / `glossary-deep.md` — the term list

## The surfaces

- `handshake-side.md` / `handshake-side-deep.md` — the upgrade checks (Origin/auth/token/subproto)
- `cswsh.md` / `cswsh-deep.md` — the four-leg CSWSH chain
- `message-side.md` / `message-side-deep.md` — the per-frame authz surface
- `message-idor.md` / `message-idor-deep.md` — the object-read gap
- `action-dispatch.md` / `action-dispatch-deep.md` — the privileged-action gap
- `injection-in-frames.md` / `injection-in-frames-deep.md` — the sink carriers
- `framing-protocols.md` / `framing-protocols-deep.md` — the envelopes (raw/socket.io/sockjs/stomp/graphql-ws/mqtt/protobuf)
- `channel-abuse.md` / `channel-abuse-deep.md` — the original reference, deepened

## The discipline

- `workflow.md` / `workflow-deep.md` — the timed pass
- `first-hour.md` — the minute-by-minute pass
- `recon-order.md` — the bounded intake
- `detection.md` / `detection-deep.md` / `detection-matrix.md` / `detection-index.md` / `detection-checklist.md` / `detection-surface.md` / `detection-playbook.md` / `detection-catalogue.md` / `detection-signals.md` / `detection-map.md` / `detection-verdicts.md` / `detection-workflow.md` — the detection corpus
- `evidence-rules.md` / `evidence-rules-deep.md` / `evidence-map.md` — the verbatim-proof discipline
- `falsifiers.md` / `falsifiers-deep.md` / `per-falsifier.md` — the kill-map
- `negative-results.md` / `negative-results-deep.md` / `negative-map.md` — the dead ends
- `checklist.md` / `checklist-deep.md` — the pass, box by box
- `preconditions.md` / `preconditions-deep.md` — the required state
- `edge-cases.md` / `edge-cases-deep.md` — the nonstandard cases
- `common-mistakes.md` / `common-mistakes-deep.md` — the failure modes
- `anti-patterns.md` — the things that look like findings but are not
- `troubleshoot.md` / `troubleshoot-deep.md` — the failure-to-fix map
- `evasion.md` / `evasion-deep.md` — the check bypasses

## The payload corpus

- `payload-variants.md` — the named payloads, grouped
- `payload-dictionary.md` — the payload → field → oracle dictionary
- `payload-map.md` — the payload → field → oracle map
- `extended-corpus.md` — the transport/session/write/history payload sets
- `probe-catalogue.md` — every probe, indexed
- `probe-map.md` — the check → command → oracle map
- `attack-shapes.md` — the gap classes, each a template
- `multi-step-chains.md` — the composite exploits
- `worked-examples.md` — the verbatim probes end-to-end
- `scenarios.md` — the challenge shapes and the pass per shape
- `case-studies.md` / `case-studies-deep.md` — the worked passes
- `exploitation.md` — the channel-gap → flag chains
- `second-order.md` — the follow-on gaps
- `real-world-cases.md` — the published bug history
- `verified-chains.md` — the honest state (catalogue — no local card)

## The maps

- `mechanism-index.md` / `mechanism-map.md` / `mechanism-catalogue.md` — the mechanism inventory
- `detection-map.md` / `detection-index.md` — the observable → check → file map
- `decision-table.md` / `decision-catalogue.md` — the reply → verdict → step
- `quick-map.md` / `quick-reference.md` / `quick-reference-deep.md` — the cheat sheets
- `lead-grammar.md` — the observation → class grammar
- `boundary-map.md` / `per-boundary.md` — the boundaries and the checks that cross them
- `per-route.md` — the flag-routes
- `reporting.md` — the report shapes

## The per-axis maps

- `per-endpoint.md` / `per-endpoint-deep.md` — the check order per endpoint shape
- `per-message-field.md` / `per-message-field-deep.md` — every field, its gap, its probe
- `per-transport.md` / `per-transport-deep.md` — the check order per transport
- `per-channel.md` — each channel type, the cells it carries
- `per-mechanism.md` — each mechanism, the full check path
- `per-check.md` — each check, its probe, its verdict, its record
- `per-surface.md` / `per-surface-map.md` — each surface's channels + cells
- `per-vector.md` — each vector, its lead, its route
- `per-target.md` — each target shape, the ordered pass
- `per-boundary.md` — each boundary, the check that crosses it

## The operator files

- `field-manual.md` — the field lessons
- `operator-notes.md` — the operational lessons
- `closing-notes.md` — the last-pass checklist
- `onboarding.md` / `onboarding-deep.md` — the first read
- `field-notes-deep.md` — the per-endpoint learning record
- `common-questions.md` — the FAQ
- `class-boundary.md` — this class vs the confusables

## The honest state

`web-websocket` is a catalogue class — no `knowledge/chains/` card records
a local solve. `verified-chains.md` names the promotion path. The corpus
is standard published guidance; a confirmed local chain is the FIRST
verification.

## The root files

- `../SKILL.md` — the entry contract
- `../field-notes.md` — the per-solve learning record
