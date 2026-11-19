# Evidence map — the evidence type → the file → the rule

## The evidence types

| Type | The file | The rule |
|---|---|---|
| the receipt | `evidence-rules.md`, `evidence-deep.md` | `status: 0x1`, `from` = caller |
| the predicate flip | `evidence-rules.md`, `verification-protocol.md` | `isSolved()` false → true |
| the state read | `evidence-deep.md` | the getter/storage/balance before/after |
| the trace | `evidence-deep.md`, `troubleshoot.md` | `cast run`/`forge -vvvv` |
| the negative | `negative-results.md`, `negative-map.md` | the revert proves a path closed |
| the chain | `multi-step-chains.md`, `evidence-catalogue.md` | the ordered tx sequence |
| the verbatim record | `evidence-rules.md` | the calldata + the receipt + the reads |

## The evidence-quality table

| The evidence | The verdict it supports |
|---|---|
| a `cast call` sim | a prediction — never a solve |
| a `forge test` pass | a fork-pass — never a live solve |
| a `status: 0x1` receipt | a mined tx — needed, not sufficient |
| `isSolved()` → true | the solve — with the receipt + the from |
| the platform's flag | the reward — the solve's consequence |

## The evidence-to-file index

- the proof standard: `evidence-rules.md`, `evidence-deep.md`
- the verify protocol: `verification-protocol.md`
- the per-bug evidence shapes: `evidence-catalogue.md`
- the negatives: `negative-results.md`, `negative-map.md`
- the honest-status: `verified-chains.md`

## The "what to preserve" index

```text
the tx hash + the receipt (status, from, to, gasUsed, logs)
the calldata / the attack-contract source
the before/after isSolved() + the getter/slot/balance reads
the falsified paths (the negative results)
```

## The hooks.py call

`hooks.py post-probe --verdict confirms --evidence "<excerpt>" --response "<the cast output>"`
— the `--response` is the verbatim `cast` output; the substring check validates
the evidence against the real read.
