# Negative results — what a failed web3 probe actually proved

## Record what reverted, not just what worked

A reverted transaction is a measurement — it falsifies a transition. Record it:

```text
transition          — the exact call sent
revert reason       — "execution reverted: <reason>" / the failing require
the slot it needed  — which precondition the require checked
the read            — isSolved() / the getter stayed false
```

## The negative-result table

| The revert/result | What it proved |
|---|---|
| `execution reverted: Ownable: caller is not the owner` | the setter IS guarded — access-control via that function falsified |
| a `transfer` that reverts on `balances[msg.sender] - _amt` | the arithmetic is `>=0.8` or SafeMath — overflow falsified |
| a `.call` that doesn't run `receive` | `.transfer`/`send` (2300 gas) — reentrancy falsified |
| `initialize` reverts `already initialized` | the proxy/impl IS initialized — that path closed |
| `cast storage` returns `0x` on a "secret" slot | the var is at a hashed slot, or doesn't exist there — recompute |
| a `call` to `selfdestruct` reverts | the selfdestruct isn't reachable, or post-Cancun rules apply |
| `isSolved()` still false after a mined tx | the transition didn't touch the predicate's state |
| `ecrecover` returns `address(0)` | the sig format is wrong — the hash/prefix mismatched |

## The strong vs weak negative

- **strong-negative** — a real reachable call on a real target contract that
  reverts: the class/path is falsified FOR THAT TRANSITION.
- **weak-negative** — a call to a guessed function signature or the wrong
  contract that reverts on "no such function" — the function/address was wrong,
  not the class.

A weak-negative doesn't falsify — fix the signature/address and retry. A
strong-negative on every reachable transition falsifies the class.

## The enumeration-closure negative

Every non-view external/public function listed, each checked for a write to the
predicate's slots, none found → the contract's reachable surface can't satisfy
the predicate → the class is closed. Record the full enumeration; the solve
needs a different contract in the setup.

## The reporting line

`hooks.py post-probe --verdict falsifies --evidence "<revert reason>" --response "<cast output>"`
records the dead path. `decide.py` reads it and routes to the next transition
or class.
