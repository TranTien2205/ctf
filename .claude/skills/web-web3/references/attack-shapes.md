# Attack shapes — predicate → bug class → first call

## The predicate-to-class map

`isSolved()` names the target; the shape of the predicate names the bug class:

| Predicate shape | Likely class | First read |
|---|---|---|
| `owner() == X` / `msg.sender`-ish | access-control / tx.origin | the owner setter's guard |
| `address(this).balance == 0` / `> K` | reentrancy / selfdestruct / drain | the withdraw + the ether routes |
| `balances[X] > huge` | integer-overflow / accounting | the arithmetic pragma + unchecked |
| `locked() == false` / `flag` | access-control / visibility | the unlock setter / the private secret |
| `winner == X` | front-running / randomness | the claim + the randomness source |
| `extcodesize(addr) == 0` | constructor trick / selfdestruct | the code-size check |
| `player == owner` on a delegatecall target | delegatecall / storage-collision | the fallback + the layouts |
| `count >= N` | reentrancy / a callable-increment | the increment's reentrancy room |
| `contract destroyed` / `code.length == 0` | selfdestruct | the selfdestruct path |
| `answer == guess` | weak-randomness / visibility | the answer's source |

## The bug-class-to-call map

| Class | The first call |
|---|---|
| access-control | `cast send ... "setOwner(address)" $ME` |
| reentrancy | deploy a `receive`-reentering contract, `deposit`+`withdraw` |
| delegatecall | call through the proxy a function that writes the owner slot |
| tx.origin | deploy a Phish contract, the caller calls `attack(target)` |
| integer-overflow | `cast send ... "transfer(uint256)" 1` (wrap the balance) |
| storage-collision | `cast send $PROXY "setA(address)" $EVIL` |
| weak-randomness | a Predict contract computing the same-block answer |
| selfdestruct | `cast send $FORCE "boom(address)" $VAULT` (funded deploy) |
| uninitialized-proxy | `cast send $IMPL "initialize(address)" $ME` |
| front-running | a contract that sequences the calls in one atomic tx |
| signature | `cast send ... "claim(bytes,uint256)" $SIG $AMT` (replayed/forged) |
| accounting | deposit/withdraw that desyncs the tracked balance |
| visibility | `cast storage` the private slot, feed it to the gate |

## The multi-bug chain

The solved predicate often needs TWO bugs: an access-control bypass to reach a
reentrancy, a delegatecall to place attacker code, a storage-collision to write
`owner`. The chain is the sequence of transitions; each is its own evidence
(the slot/getter read before/after).
