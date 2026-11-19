# Decision catalogue — the full observation → call table

## By the predicate

| `isSolved()` reads | The call |
|---|---|
| `owner() == X` | `cast send "setOwner"`/`"init"`/`"transferOwnership"`; or Phish/delegatecall |
| `balance == 0` | reentrancy contract / selfdestruct force-feed / the desync |
| `balance > 0` | selfdestruct force-feed |
| `locked() == false` | `cast send "unlock"` / `cast storage` the private secret |
| `flag`/`solved` | `cast send "setFlag"` |
| `winner`/`answer`/`guess` | Predict contract / a sequencer |
| `count >= N` | a reentrancy to the count |
| `balances[x]` | the wrap / the desync |
| `code.length == 0` | `selfdestruct` / a constructor-EOA call |
| `signer`/`verified` | the replayed/forged sig |

## By the primitive found

| The primitive | The call |
|---|---|
| `delegatecall` | `cast send` through the proxy to write the owner slot |
| `call{value}` then `-=` | a `receive`-reenter contract |
| `tx.origin` | a Phish contract |
| `<0.8` arithmetic | `cast send` the wrapping call |
| `block.*` in a decision | a Predict contract |
| `selfdestruct` | a funded Force + `boom` |
| `ecrecover` | a `cast send` the replayed/forged sig |
| `initialize` | `cast send "initialize(address)"` |
| `for` over a growing set | grow the set past the gas limit |
| `extcodesize` check | a constructor call |
| `private` var | `cast storage` the slot |

## By the observation

| Observation | The call |
|---|---|
| a bare setter | `cast send` it |
| a bytecode-only contract | `cast code` + disasm → the SSTORE map |
| a proxy + impl | read the impl slot + the layouts |
| a setup deploying several | `cast call` the setup's getters → the target |
| `isSolved()` already true | re-read `Setup.sol` — a different predicate/contract |
| a revert on the planned call | `cast run` the trace → the failing require |
| `isSolved()` still false | the wrong transition — re-read the predicate |
| the private key missing | re-read it from the challenge — never reuse a dead instance's |
