# Detection verdict — naming the class with confidence

## The verdict levels

| Level | The state |
|---|---|
| **candidate class** | the predicate + a reachable call suggest it — probe it |
| **confirmed class** | a reachable transition is planned and dry-run-flips the predicate |
| **closed class** | the falsifier observed — the class is dead |
| **unknown** | no reachable transition found yet — keep enumerating |

## The verdict decision

```
predicate's shape  →  the candidate classes
reachable calls    →  which classes have a transition
source/bytecode    →  which class's primitive is present
the dry-run        →  does the transition flip the predicate?
                   ↓
   the verdict = the class whose transition flips it
```

## The confidence rules

- the predicate narrows but doesn't confirm — a `balance` predicate could be
  reentrancy OR force-feed OR accounting
- the reachable-call inventory is the confirmation — a transition exists or not
- the dry-run is the strongest evidence before the live send — a sim-flip is
  the transition working
- a `cast send` that flips `isSolved()` is the confirmation

## The "two classes apply" case

A predicate `balance == 0` on a contract with a `call`-then-update `withdraw` —
reentrancy; the same predicate on a contract with no ether routes —
selfdestruct. The contract's primitives disambiguate — `detection-matrix.md`.

## The verdict record

```text
the class       — the named bug class
the confidence  — candidate / confirmed / closed
the transition  — the planned cast send / attack contract
the falsifier   — what would close it
```

`hooks.py post-probe` records the verdict; `decide.py` routes on it.

## The "no verdict" case

Every reachable function enumerated, no transition to the predicate's state →
the class is closed for this contract → escalate to a different contract in the
setup or a different predicate reading.
