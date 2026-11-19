# Per-route map — the solve-route → the procedure

## The direct-call route

```
the predicate's slot is writable by a bare public setter
  → cast send the setter → isSolved() flips
```

The cheapest route — the unguarded setter. `access-control.md`.

## The contract-deploy route

```
the primitive needs a deployed contract (reentrancy/phish/force/predict)
  → write the contract → forge/cast deploy → call its run()/attack()
  → isSolved() flips
```

The standard route for most bug classes — `payload-families.md`.

## The atomic-sequence route

```
multiple transitions must land in one tx (front-running, a check-then-act)
  → a Solver.run() sequencing them → cast send run() → isSolved() flips
```

`front-running.md`, `exploitation.md`.

## The bytecode-only route

```
no source → cast code → decompile → the dispatch/SSTORE map
  → name the transition → the exploit
```

`detection-deep.md`, `evasion.md`.

## The multi-contract route

```
the setup deploys several contracts → the predicate's + the attack surface
  → map them → the path through them → the solve
```

`per-target.md`, `workflow-catalogue.md`.

## The chain route

```
two bugs compose (access→reentrancy, collision→delegatecall)
  → sequence them — per-step evidence → isSolved() flips
```

`multi-step-chains.md`.

## The per-route checklist

| Route | The order |
|---|---|
| direct | read → send → verify |
| contract | read → write contract → deploy → run → verify |
| atomic | read → Solver.run() → deploy → run → verify |
| bytecode | code → disasm → map → the transition → send |
| multi-contract | map deploys → the predicate's contract → its surface |
| chain | the sequence → per-step evidence → the flip |
