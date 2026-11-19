# README (deep) — the corpus at depth

## What this corpus is

A complete operational reference for the `web-web3` / smart-contract CTF class —
the Setup+Challenge+RPC+private-key shape where the solve is an attributable
transaction that flips `isSolved()` on the live chain. Catalogue status:
published EVM knowledge, not local solves.

## The coverage

- **the model** — `mechanism*`/`evm-primitives`/`theory*` — the EVM, the
  call-family, the storage model, the context ops, the block context
- **the detection** — `detection*`/`attack-shapes*`/`per-*` — the predicate
  read, the reachable-call inventory, the signal tables
- **the bug classes** — the per-class files: the shape, the fingerprint, the
  exploit, the falsifier, the evidence
- **the payloads** — `payload-*`/`exploitation*`/`probe-catalogue` — the
  `cast send`/`forge create`/`Solver` contract shapes
- **the evidence** — `evidence*`/`verification*`/`negative-*`/`falsifiers*` —
  the on-chain proof standard, the per-bug records, the dead-path records
- **the workflow** — `workflow*`/`first-hour*`/`recon-order`/`onboarding*`/
  `field-manual*`/`checklist*`/`quick-reference*`/`operator-notes*` — the order
  and the habits
- **the traps + cases** — `edge-cases*`/`boundary-cases`/`common-mistakes*`/
  `anti-patterns`/`troubleshoot*`/`evasion*`/`case-studies*`/`real-world-cases`/
  `worked-examples`/`scenarios`/`common-questions*` — the failure modes and the
  canonical shapes
- **the reference** — `glossary*`/`summary*`/`index`/`README*`/`closing-*`/
  `field-notes-deep`/`verified-chains`/`extended`/`preconditions*` — the index,
  the honest status, the vocabulary

## The honest-status line

Every module is a starting point — `web-web3` is `catalogue`. The live chain's
behavior is the ground truth; a module that disagrees with it is wrong, and a
`../field-notes.md` entry is the correction that moves the class to `verified`.
