# Negative map — the observed-negative → the class it ruled out

## The revert-negative → the class

| The negative | The class it rules out |
|---|---|
| `Ownable: caller is not the owner` on every setter | access-control via those setters |
| `SafeMath`/revert on the arithmetic | integer-overflow on that path |
| `.transfer` (2300 gas) on the call | reentrancy via that call |
| `reentrancy guard` revert | reentrancy via the guarded function |
| `already initialized` revert | uninitialized-proxy in that context |
| `not a contract`/`extcodesize` revert | the constructor-EOA trick |
| a `call` that doesn't run `receive` | reentrancy — the call isn't gas-forwarded |
| `cast storage` returns `0x` | the var isn't at that slot — recompute |
| `ecrecover` → `address(0)` | the sig format is wrong |
| the `call` to `selfdestruct` reverts | the selfdestruct isn't reachable |

## The no-transition negative

Every non-view external/public function enumerated, each checked for a write
to the predicate's slots, none reachable → the class is closed for THIS contract.
Record the enumeration; the solve needs a different contract in the setup.

## The "the predicate's already true" negative

`isSolved()` reads `true` on the fresh instance — the setup was already solved,
or the predicate reads a different contract than assumed. Re-read `Setup.sol`.

## The simulation-negative

`forge`/`cast call` the exploit — `isSolved()` stays `false` → the transition
is wrong. The dry-run falsified the approach before a live tx was spent.

## The negative-result record format

```text
the path        — the class + the transition tried
the negative    — the revert reason / the read that stayed false
what it proved  — which transition/class is closed
the next        — the different transition/class to try
```

## The strong-vs-weak table

- **strong-negative**: a real reachable call on the real target that reverts on
  a guard — the path is closed
- **weak-negative**: a call to a wrong function signature or the wrong contract —
  the signature/address was wrong, not the class

A weak-negative doesn't falsify — fix the signature/address and retry.
