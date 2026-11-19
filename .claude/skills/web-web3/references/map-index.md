# Map index — every map file and what it maps

## The axis maps

| File | Maps |
|---|---|
| `attack-shapes.md`/`attack-shapes-deep.md` | the predicate → the class → the transition |
| `per-bug.md`/`per-bug-catalogue.md` | the bug → the file → the first call |
| `per-verb.md` | the function-shape → the bug |
| `per-target.md` | the contract type → the bug |
| `per-surface.md` | the interaction surface → the check |
| `per-mechanism.md`/`per-mechanism-deep.md` | the primitive → the bug files |
| `per-check.md` | the `require`/`assert` → the bypass |
| `per-falsifier.md` | the falsifier → the class it closes |
| `per-vector.md` | the exploit vector → the file |
| `per-route.md` | the solve route → the procedure |
| `per-endpoint.md` | the function endpoint → the check |
| `per-channel.md` | the RPC channel → the evidence |
| `per-condition.md` | the solved-condition shape → the class |
| `per-class.md` | the class → the contract type → the mechanism |
| `per-boundary.md` | the boundary → the class inside it |

## The detection maps

| File | Maps |
|---|---|
| `detection-map.md` | the signal → the class → the file |
| `detection-index.md`/`detection-index-deep.md` | the full signal table |
| `detection-matrix.md` | the predicate × primitive matrix |
| `detection-signals.md` | the signal-strength table |

## The payload maps

| File | Maps |
|---|---|
| `payload-map.md` | the class → the payload → the verify |
| `payload-dictionary.md` | the call shapes |
| `payload-variants.md` | the call-shape variants |
| `payload-families.md`/`payload-families-deep.md` | the contract templates |

## The class maps

| File | Maps |
|---|---|
| `access-control-map.md`/`access-control-catalogue.md` | the guard/setter shapes |
| `reentrancy-map.md`/`reentrancy-variants.md` | the re-entry shapes |
| `tx-origin-map.md` | the origin-check shapes |
| `integer-overflow-map.md` | the wrap shapes |
| `weak-randomness-map.md` | the predictable-source shapes |
| `selfdestruct-map.md` | the destruction shapes |
| `signature-replay-map.md` | the sig shapes |

## The reference maps

| File | Maps |
|---|---|
| `mechanism-map.md`/`mechanism-index.md`/`mechanism-catalogue.md` | primitive → bug |
| `theory-map.md`/`theory-index.md` | the limit → the classes |
| `evidence-map.md`/`evidence-index.md` | the evidence type → the file/rule |
| `negative-map.md` | the observed-negative → the class it rules out |
| `workflow-map.md` | the phase → the file → the command |
| `workflow-index.md` | the procedure files → when to open |
| `index.md` | every file listed |
| `summary-map.md` | the one-line map |
| `map-index.md` | this file — the maps indexed |
