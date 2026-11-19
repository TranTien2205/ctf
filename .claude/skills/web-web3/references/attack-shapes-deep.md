# Attack shapes (deep) — the predicate → class → transition, full

## The complete predicate-to-class table

| `isSolved()` reads | The classes | The transition |
|---|---|---|
| `owner() == player`/`tx.origin` | access-control, tx.origin, delegatecall, storage-collision | a setter / a Phish / a collision write |
| `locked() == false`/`flag`/`solved()` | access-control, visibility | a setter / a private-unlock |
| `address(this).balance == 0` | reentrancy, accounting, selfdestruct | a drain / a desync-withdraw / force-to-zero |
| `address(this).balance > 0`/`>= K` | selfdestruct | force-feed |
| `balances[player] > huge` | integer-overflow, accounting | a wrap / a desync |
| `count() >= N` | reentrancy | a re-enter to the count |
| `winner() == player` | front-running, weak-randomness | a sequencer / a predict |
| `answer() == guess` | weak-randomness, visibility | a predict / a storage-read |
| `code.length == 0`/`extcodesize == 0` | selfdestruct, constructor | the delete / the EOA-trick |
| `token.balanceOf(player) >= X` | integer-overflow, token-standards, accounting | a mint/wrap/transfer |
| `rate()`/`shares()`/`price()` | accounting-vault, flashloan-oracle | the desync |
| `signer`/`verified()`/`recovered` | signature | a replayed/forged sig |
| `isSolved() && b && c` | a chain | the ordered transitions |

## The class-to-transition detail

| Class | The transition |
|---|---|
| access-control | `cast send "setOwner(address)" $ME` |
| tx.origin | `Phish.attack(target)` — the contract-in-middle |
| delegatecall | a `delegatecall`-ed writer that lands on the owner slot |
| storage-collision | `cast send "setA(addr)"` → the wrong-slot write |
| reentrancy | `Reenter.attack()` — the `receive` re-enters |
| integer-overflow | `cast send "transfer" 1` — the wrap |
| weak-randomness | `Predict.attack()` — the same-block compute |
| selfdestruct | `Force.boom(target)` — the force-feed |
| uninitialized-proxy | `cast send "initialize(address)" $ME` |
| front-running | `Sequencer.run()` — the atomic order |
| signature | `cast send "claim" theSig` — the replay/forge |
| accounting | `Solver.run()` — the deposit/donate/withdraw desync |
| visibility | `cast storage` the slot → `cast send` the gate |
| gas-griefing | a refusing partner / a loop-grow |

## The "the predicate is a chain" case

`isSolved() = a && b && c` — each clause a transition; the chain is the ordered
sequence; `multi-step-chains.md` + `multi-step-chains-deep.md`.

## The "no single transition" case

The predicate's state needs TWO transitions — a collision-then-delegatecall, an
init-then-kill, a force-feed-then-drain — the composed exploit. The single-bug
case first; a chain when no single transition reaches it.
