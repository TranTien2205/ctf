# Workflow map — the phase → the file → the command

## The phases

| Phase | The file | The commands |
|---|---|---|
| intake | `recon-order.md` | read `Setup.sol`; `cast chain-id`; `cast wallet address` |
| predicate | `detection.md`, `attack-shapes.md` | `cast call $SETUP "isSolved()"`; map the shape |
| state-map | `detection-surface.md` | `cast call` getters; `cast storage`; `cast balance` |
| inventory | `detection-deep.md`, `per-verb.md` | the function list; which write the predicate's slots |
| class | `detection-map.md`, `per-bug.md` | the named class + the falsifier |
| plan | `decision-table.md`, `payload-map.md` | the ONE transition; the attack contract if needed |
| dry-run | `workflow.md`, `exploitation.md` | `forge test --fork-url`/`cast call` the sim |
| send | `exploitation.md`, `payload-variants.md` | `cast send` / `forge create` + `run` |
| verify | `evidence-rules.md`, `verification-protocol.md` | `cast call isSolved()` → true; `cast receipt` |
| record | `evidence-deep.md`, `negative-results.md` | the chain + the falsified paths |

## The decision points

```
after intake     → the predicate names the class
after inventory  → a bare setter? the cheap solve first
after the class  → ONE transition — the reachable write
after dry-run    → sim flips? then send; sim-fails? fix the transition
after send       → isSolved() flips? the solve; else re-read the predicate
after 3 reverts  → decide.py escalate — a different class/contract
```

## The file-to-phase index

- the read phase → `recon-order.md`, detection*.md
- the class decision → `attack-shapes.md`, `per-bug.md`, `detection-map.md`
- the exploit phase → `exploitation.md`, payload-*.md, the bug files
- the verify phase → evidence-*.md, `verification-protocol.md`
- the discipline → workflow*.md, `checklist.md`, `operator-notes.md`
