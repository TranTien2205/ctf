# Per-verb map — the Solidity surface verb → the bug it hides

## The function-shape inventory

| Verb / shape | The likely bug |
|---|---|
| `setOwner`/`transferOwnership`/`changeOwner` | access-control — is it guarded? `tx.origin`? |
| `unlock`/`setFlag`/`solve` | access-control — a bare setter |
| `initialize`/`init`/`setup` | uninitialized-proxy — callable post-deploy? |
| `withdraw`/`transfer`/`send` | reentrancy (call-then-update) / overflow / accounting |
| `deposit`/`stake`/`mint` | accounting-vault — the share/rate desync |
| `claim`/`redeem`/`winner` | front-running / signature / randomness |
| `guess`/`roll`/`flip`/`answer` | weak-randomness — the `block.*` source |
| `fallback`/`receive` | the entry — what does it delegate/accept? |
| `delegatecall` (in a fallback) | delegatecall — the target + the layout |
| `selfdestruct`/`kill`/`destroy` | selfdestruct — force-feed or the library-kill |
| `permit`/`verify`/`claim(sig)` | signature — the replayable/malleable hash |
| `transferFrom`/`approve`/`allowance` | token — an open approval, a missing check |
| `upgradeTo`/`setImpl`/`setLibrary` | the delegatecall target settable — collision |

## The modifier/keyword inventory

| Keyword | The check |
|---|---|
| `onlyOwner`/`onlyX` | what does it compare — `msg.sender`, `tx.origin`, a settable var? |
| `require(tx.origin ...)` | tx.origin — the phish / the EOA-trick |
| `require(msg.sender ...)` | who can be the sender — a contract? a constructor? |
| `nonReentrant`/`locked` | does it actually guard, or is the flag checkable mid-tx? |
| `payable` | does it need `msg.value`? can a selfdestruct bypass it? |
| `internal`/`private` | the intended-private function left public? |
| `external`/`public` | the reachable surface — every one is a candidate transition |
| `staticcall`/`view` for a check | the snapshot read — mid-state invisible to it |

## The per-function read

For each reachable non-view function, ask in order:

1. does it write a slot `isSolved()` reads? → the candidate transition
2. is it guarded, and by what — `msg.sender`, `tx.origin`, a settable var?
3. does it `call`/`delegatecall`/`selfdestruct` before updating state?
4. does its arithmetic wrap (`<0.8`) or revert (`>=0.8`/`unchecked`)?
5. does it read a predictable source (`block.*`, `private` storage)?

The first function whose answer is "yes, unguarded, and writes the predicate's
slot" is the cheapest solve.
