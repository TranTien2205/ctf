# Workflow map — the phase → the file → the command

## Phase 0 — extract

| File | The command |
|---|---|
| `parameter-sheet.md` | fill the sheet |
| `detection.md`/`detection-deep.md` | fingerprint the weakness |
| `recon-order.md` | source → count → exponent → leak → relation |

`python3 tools/crypto_attack.py list` — the inventory + bounds.

## Phase 1 — discriminate

| File | The command |
|---|---|
| `attack-table.md`/`attack-table-deep.md` | the first-yes row |
| `per-signal.md`/`per-parameter.md`/`per-bound.md`/`per-mechanism.md` | the maps |
| `detection-matrix.md`/`detection-catalogue.md` | the feature grid |

## Phase 2 — bound-check

| File | The command |
|---|---|
| `per-bound.md`/`lattice-bounds.md`/`falsifiers.md`/`boundary-cases.md` | the bounds |
| `per-check.md`/`per-falsifier.md`/`falsifier-map.md` | the checks |

Read the applicability line the tool prints — the falsifier.

## Phase 3 — attack

| File | The command |
|---|---|
| `payload-dictionary.md`/`payload-map.md`/`payload-families.md`/`payload-variants.md` | the call |
| `exploitation.md`/`exploitation-deep.md`/`exploitation-catalogue.md` | the run |
| `probe-catalogue.md`/`probe-map.md` | the measurable reads |

`python3 tools/crypto_attack.py <id> <flags>` — `<id> --help` for the args.

## Phase 4 — verify

| File | The command |
|---|---|
| `verify.md`/`verification-protocol.md`/`evidence-rules.md`/`evidence-deep.md`/`evidence-catalogue.md` | the proof |

`pow(m,e,n)==c` or `p*q==n`.

## Phase 5 — record / escalate

| File | The command |
|---|---|
| `negative-results.md`/`falsifiers.md` | the dead attacks |
| `troubleshoot.md`/`troubleshoot-deep.md`/`common-mistakes.md`/`anti-patterns.md`/`edge-cases.md`/`evasion.md` | the stalls |
| `verified-chains.md` | the honest status |

`tools/classify_solve.py --chain <id>` after a solve; `knowledge/attempts/` for
a dead end.
