# Per-endpoint map — the function-endpoint → the check

## The getter endpoints (read-only, free)

| Endpoint shape | The read |
|---|---|
| `isSolved()`/`solved()` | the predicate — `cast call` first |
| `owner()`/`locked()`/`flag()` | the predicate-relevant var |
| `balances(addr)`/`balanceOf(addr)` | the accounting state |
| `challenge()`/`player()`/`token()`/`impl()` | the setup's deployed addresses |
| `totalAssets()`/`totalShares()`/`rate()` | the vault invariant |
| `getPrice()`/`getAnswer()` | the oracle/answer |

## The setter endpoints (write, attributable)

| Endpoint shape | The check |
|---|---|
| `setOwner`/`changeOwner`/`transferOwnership` | the access-control surface |
| `unlock`/`setFlag`/`setSolved` | the flag surface |
| `initialize`/`init`/`setup`/`register` | the init surface |
| `deposit`/`withdraw`/`transfer`/`claim` | the value-move surface — reentrancy/accounting |
| `guess`/`roll`/`flip`/`answer` | the randomness surface |
| `propose`/`execute`/`vote` | the governance surface |
| `permit`/`verify`/`claim(sig)` | the signature surface |
| `setImpl`/`upgradeTo`/`setLibrary` | the delegatecall-target surface |

## The entry endpoints

| Endpoint | The surface |
|---|---|
| `receive()`/`fallback()` | the ether/unmatched-call entry — reentrancy/delegatecall |
| the constructor | the deploy-time init — the extcodesize-0 window |
| `init`/`initialize` | the post-deploy init — the uninit-proxy surface |

## The per-endpoint read

For each reachable non-view endpoint:

1. does it write a slot `isSolved()` reads? → the candidate transition
2. is it guarded — `msg.sender`/`tx.origin`/a var/a sig?
3. does it `call`/`delegatecall`/`selfdestruct` before settling?
4. does its arithmetic wrap?
5. does it read a predictable source?

## The endpoint-to-class table

| The endpoint | The class it likely is |
|---|---|
| a bare `setOwner` | access-control |
| a `call`-then-update `withdraw` | reentrancy |
| a `fallback` → `delegatecall` | delegatecall |
| a `tx.origin`-checked `changeOwner` | tx.origin |
| a `<0.8` `transfer` | integer-overflow |
| a `block.*`-fed `guess` | weak-randomness |
| a `selfdestruct`-calling `kill` | selfdestruct |
| an `initialize` callable | uninitialized-proxy |
| an `ecrecover`-gated `claim` | signature |
| a `deposit`/`withdraw`/`rate` | accounting-vault |
