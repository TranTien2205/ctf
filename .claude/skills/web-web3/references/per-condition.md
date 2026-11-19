# Per-condition map — the solved-condition shape → the class

## The predicate-shape inventory

| The `isSolved()` reads | The class it forces |
|---|---|
| `owner() == tx.origin`/`== player` | access-control — own the contract (setter/phish/collision) |
| `owner() != setup`/`== challenger` | a ownership-takeover |
| `address(this).balance == 0` | a drain — reentrancy/withdraw/accounting |
| `address(this).balance > 0` | a force-feed — selfdestruct |
| `address(this).balance == K` | a precise balance — the accounting force |
| `locked() == false` | an unlock — access-control/visibility |
| `flag()`/`solved() == true` | a setter — access-control |
| `winner() == player` | a first-come — front-running |
| `answer() == X`/`guess == answer` | a predict — weak-randomness/visibility |
| `count() >= N` | a callable-increment — reentrancy |
| `balances[player] > huge` | a wrap — integer-overflow |
| `balances[contract] == 0` | a drain |
| `extcodesize(c) == 0`/`c.code.length == 0` | a destruction — selfdestruct/constructor |
| `contract.owner() == player` on a delegatecall target | a storage-collision/delegatecall |
| `token.balanceOf(player) >= X` | a token-balance — overflow/mint/transfer |
| `rate()`/`price()`/`shares()` | a desync — accounting-vault |
| `verified()`/`signer()` | a sig-check — signature-replay |

## The composite predicates

```solidity
isSolved() = owner() == player && locked() == false
isSolved() = balance == 0 || flag == true
isSolved() = a() && b() && c()
```

A composite → the chain — each clause is a transition; `multi-step-chains.md`.

## The predicate-to-first-check table

| Reads | Check first |
|---|---|
| `owner()` | a bare setter |
| `balance` | the withdraw + the ether routes |
| `flag`/`locked` | a setter / a private gate |
| `answer`/`winner` | the `block.*` source / the ordering |
| `count` | the increment's reentrancy room |
| `balances[x]` | the arithmetic — the wrap |
| `code.length` | a `selfdestruct` reachable? a constructor check? |
| `rate`/`shares` | the desync path |

## The "the predicate is unreachable" case

The predicate's slots have no reachable writer → the class is closed — a
different contract in the setup, or a different predicate reading —
`falsifiers.md`.
