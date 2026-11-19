# Coverage map — every file, grouped

## Identification

- `detection*` — the fingerprint tests and reads.
- `cipher-identification*` — the stream-type discriminator.
- `detection-matrix*`/`detection-catalogue*`/`detection-index*`/
  `detection-playbook`/`detection-checklist*` — the matrices and lists.
- `lead-grammar` — the description cues.

## The attacks

- `per-attack-*` + `*-deep` — `lcg-recover`, `lcg-unknown-modulus`,
  `lcg-truncated`, `berlekamp-massey`, `lfsr-recover`, `lfsr-predict`,
  `mt19937-clone`, `xorshift128`.
- `lcg-*`/`lfsr-*`/`mt-*`/`xorshift-*`/`seed-*` — the family deeps +
  catalogues.
- `per-family-*` + `*-deep` — `lcg`,`lfsr`,`mt-xorshift`,`seed`.
- `attack-catalogue` — the id table.

## The math

- `theory*`/`theory-variant`/`theory-map` — the `S/O` floor, linearity.
- `mechanism*`/`mechanism-variant` — the `(F,G)` model.
- `glossary*` — the terms.

## The gates

- `boundary*`/`boundary-catalogue`/`per-boundary` — the floors/edges.
- `edge-*`/`edge-catalogue` — the non-textbook shapes.
- `condition-*`/`per-condition`/`preconditions` — the requirements.
- `per-check*`/`detection-checklist*` — the checks.

## The commands

- `payload-*`/`payload-dictionary*`/`payload-map`/`payload-index` —
  the flags.
- `operator-notes*` — the helpers.
- `field-manual*`/`quick-reference*` — the cards.

## The close

- `verify*`/`verify-variant` — the accept gate.
- `evidence*`/`evidence-map` — what proves what.
- `checklist*`/`detection-checklist*` — the run-lists.

## The failure paths

- `falsifiers*`/`falsifier-map` — the kills.
- `negative-*`/`negative-map` — the records.
- `troubleshoot*` — by attack.
- `common-mistakes*`/`anti-patterns*`/`common-questions` — the traps.
- `evasion*`/`evasion-catalogue` — the disguises.

## The order

- `workflow*`/`workflow-map`/`workflow-index`/`workflow-playbook*`/
  `workflow-catalogue*` — the loop.
- `recon-order*`/`probe-order*`/`first-hour` — the ordering.
- `decision-table*` — the matrix.

## The cases

- `case-studies*`/`worked-examples*`/`scenarios*`/`real-world-cases*`/
  `multi-step-chains*` — the solves.

## The scope

- `class-boundary*` — in/out of class.
- `verified-chains*`/`preconditions` — the status.
