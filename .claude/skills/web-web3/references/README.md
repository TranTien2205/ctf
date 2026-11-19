# web-web3 reference index — the smart-contract / web3 class

## Read first

- `onboarding.md` — the mental model + the discipline
- `mechanism.md` — the setup-contract + solved-predicate shape
- `detection.md` — the package read + the predicate
- `workflow.md` — the order
- `attack-shapes.md` — the predicate → class map

## The bug classes

- `access-control.md` — unprotected setters / the bypassable guard
- `reentrancy.md` — the callback re-entry
- `delegatecall.md` — foreign code on the caller's storage
- `storage-collision.md` — the write lands on the wrong slot
- `tx-origin.md` — the origin/sender confusion
- `integer-overflow.md` — the wrap
- `weak-randomness.md` — the predictable source
- `selfdestruct.md` — force-feed / delete / kill
- `uninitialized-proxy.md` — the callable init
- `front-running.md` — the ordering
- `signature-replay.md` — the replay/forge
- `accounting-vault.md` — the balance desync
- `visibility.md` — the readable `private`
- `gas-griefing-dos.md` — the DOS
- `token-standards.md` — the ERC surfaces
- `flashloan-oracle.md` — the atomic skew

## The maps

- `per-bug.md` — bug → file → first call
- `per-verb.md`/`per-target.md`/`per-surface.md`/`per-mechanism.md`/`per-check.md`/`per-falsifier.md`/`per-vector.md`/`per-route.md`/`per-endpoint.md`/`per-channel.md`/`per-condition.md`/`per-class.md`/`per-boundary.md` — the per-axis maps
- `detection-map.md`/`detection-matrix.md`/`detection-index.md`/`detection-signals.md` — the signal tables
- `decision-table.md`/`decision-catalogue.md` — observation → call
- `payload-map.md`/`payload-dictionary.md`/`payload-variants.md`/`payload-families.md` — the call/contract shapes
- `mechanism-map.md`/`mechanism-index.md`/`mechanism-catalogue.md` — primitive → bug
- `reentrancy-map.md`/`weak-randomness-map.md`/`integer-overflow-map.md`/`tx-origin-map.md`/`selfdestruct-map.md`/`signature-replay-map.md`/`access-control-map.md` — the per-class maps
- `theory-map.md`/`theory-index.md` — the limit → the classes

## The deep variants

- `mechanism-deep`, `detection-deep`, `detection-index-deep`, `delegatecall-deep`, `reentrancy-deep`, `storage-collision-deep`, `tx-origin-deep`, `integer-overflow-deep`, `weak-randomness-deep`, `selfdestruct-deep`, `uninitialized-proxy-deep`, `front-running-deep`, `signature-replay-deep`, `accounting-vault-deep`, `access-control-deep`, `evidence-deep`, `exploitation-deep`, `multi-step-chains-deep`, `workflow-deep`, `workflow-index`, `workflow-catalogue`, `workflow-map`, `workflow-playbook`, `workflow-verdict`, `workflow-steps`, `workflow-onboarding`, `first-hour-deep`, `onboarding-deep`, `field-manual-deep`, `field-manual-catalogue`, `operator-notes-deep`, `checklist-deep`, `quick-reference-deep`, `common-mistakes-deep`, `edge-cases-deep`, `troubleshoot-deep`, `evasion-deep`, `theory-deep`, `theory-catalogue`, `theory-playbook`, `theory-notes`, `glossary-deep`, `summary-deep`, `case-studies-deep`, `common-questions-deep`, `common-questions-catalogue`, `verification-protocol-deep`, `payload-families-deep`, `reentrancy-variants`, `field-notes-deep`, `detection-variants`, `detection-playbook`, `detection-verdict`, `detection-catalogue`, `detection-surface`, `detection-checklist`, `detection-signals`

## The reference modules

- `mechanism*`, `evm-primitives`, `detection*`, `evidence*`, `falsifiers`, `per-falsifier`, `negative-*`, `verification-*`, `workflow*`, `recon-order`, `first-hour*`, `onboarding*`, `field-manual*`, `operator-notes*`, `checklist*`, `quick-reference*`, `closing-notes`, `edge-cases*`, `boundary-cases`, `common-mistakes*`, `anti-patterns`, `troubleshoot*`, `evasion*`, `case-studies*`, `real-world-cases`, `worked-examples`, `scenarios`, `common-questions*`, `theory*`, `glossary*`, `summary*`, `index`, `preconditions`, `probe-catalogue`, `decision-*`, `attack-shapes*`, `per-*`, `payload-*`, `exploitation*`, `multi-step-chains*`, `field-notes-deep`, `verified-chains`, `extended`
