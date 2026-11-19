# Evidence index — every evidence type and the file that governs it

## The solve-evidence

| Evidence | The file | The rule |
|---|---|---|
| `isSolved() → true` | `evidence-rules.md`, `verification-protocol.md` | the predicate flip — the solve |
| the receipt `status: 0x1` | `evidence-rules.md`, `evidence-deep.md` | the tx mined |
| the receipt `from` | `evidence-deep.md`, `verification-protocol-deep.md` | the attributable caller |
| the calldata/`cast tx` | `evidence-deep.md`, `exploitation-deep.md` | the exploit's exact call |
| `cast run` the trace | `evidence-deep.md`, `troubleshoot.md` | the mechanism's execution |
| the before/after reads | `evidence-catalogue.md` | the getter/slot/balance change |

## The negative-evidence

| Evidence | The file | The rule |
|---|---|---|
| the revert reason | `negative-results.md`, `troubleshoot.md` | the failing `require` |
| `status: 0x0` | `negative-results.md` | the tx reverted — not a solve |
| a `status: 0x1` + still-false `isSolved()` | `negative-results.md` | a mined no-op — wrong transition |
| `cast storage` → `0x` | `negative-results.md` | the var isn't at that slot |
| the enumeration-closure | `negative-map.md`, `per-falsifier.md` | every writer enumerated + guarded |

## The honest-status evidence

| Evidence | The file |
|---|---|
| the class is `catalogue` | `verified-chains.md`, `../SKILL.md` |
| a real solve's field-note | `field-notes-deep.md`, `../field-notes.md` |
| a verified chain card | `knowledge/chains/` (when one lands) |

## The per-bug evidence table

| Bug | The evidence record | File |
|---|---|---|
| access-control | the setter tx + the owner getter | `evidence-catalogue.md` |
| reentrancy | the attack deploy + the drain + `cast balance` → 0 | `evidence-catalogue.md` |
| delegatecall | the tx + `cast storage` the slot | `evidence-catalogue.md` |
| tx.origin | the Phish deploy + `owner()` = caller | `evidence-catalogue.md` |
| ... | each bug's shape | `evidence-catalogue.md` |

## The index's use

`evidence-map.md` is the type→file map; `evidence-catalogue.md` is the
per-bug record shapes; verification-protocol*.md is the verify sequence;
negative-*.md is the falsified-path records. The solve's proof is the
on-chain transition — every file's rule is that `cast call`/`forge`/`status 0x1`
alone is not it.
