# Detection playbook — the decision sequence

## Step 1 — the package

```
.sol file + RPC + key → a web3 challenge
Setup.sol + isSolved() → the predicate-driven shape
```

## Step 2 — the predicate

```
isSolved() reads X → the class narrows:
  owner()         → access-control / tx.origin
  balance         → reentrancy / selfdestruct / accounting
  flag/locked     → access-control / visibility
  answer/winner   → weak-randomness / front-running
  code.length     → selfdestruct / constructor
  signer/verified → signature
  rate/shares     → accounting/flash
```

## Step 3 — the reachable-call inventory

```
for each non-view external/public function:
  does it write a predicate slot?  → candidate transition
  is it guarded? by what?          → the bypass shape
  does it call/delegatecall/selfdestruct before settling? → the primitive
```

## Step 4 — the bytecode confirmation

```
cast code → match the source? no → the bytecode's dispatch/SSTORE map is the surface
grep the ops: DELEGATECALL/CALL/SELFDESTRUCT/ORIGIN/TIMESTAMP/ECRECOVER/SSTORE
```

## Step 5 — the class decision

```
the predicate + the reachable calls + the primitive signals → ONE class
the unguarded setter checked FIRST — it's usually the intended solve
the deep bug only when no bare setter exists
```

## The falsifier checkpoints

- every reachable function guarded AND none writes the predicate's slots → the
  class is closed — escalate
- the call is `.transfer`/`.send` → reentrancy closed
- the pragma is `>=0.8` with no `unchecked` → overflow closed
- the decision doesn't read `block.*` → weak-randomness closed

## The output

ONE named class + the planned transition + the falsifier that would close it.
`decide.py`/`hooks.py` the checkpoint before the attributable `cast send`.
