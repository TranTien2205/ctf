# Quick reference — the one-page web3 card

## The read

```bash
export RPC=<rpc> KEY=<privkey>
cast call $SETUP "isSolved()(bool)"                    # the predicate
cast call $SETUP "challenge()(address)"                # the target
cast call $CH "owner()(address)" "locked()(bool)"      # the getters
cast balance $CH; for s in 0 1 2 3; do cast storage $CH $s; done
cast code $CH | head -c 100                            # the bytecode
```

## The predicate → class

| Reads | Class |
|---|---|
| `owner()` | access-control / tx.origin |
| `balance` | reentrancy / selfdestruct / accounting |
| `flag`/`locked` | access-control / visibility |
| `answer`/`winner` | weak-randomness / front-running |
| `code.length` | selfdestruct / constructor |

## The exploit shapes

```bash
# bare setter
cast send $CH "setOwner(address)" $ME --private-key $KEY --rpc-url $RPC
# visibility
cast storage $CH 1   →   cast send $CH "unlock(bytes32)" 0x<pw> ...
# attack contract
forge create Solver --constructor-args $CH --private-key $KEY --rpc-url $RPC
cast send $SOLVER "run()" --private-key $KEY --rpc-url $RPC
```

## The bug classes

| Class | The primitive |
|---|---|
| access-control | a bare setter — call it |
| reentrancy | a `receive`-reentering contract + deposit/withdraw |
| delegatecall | call through the proxy to write the owner slot |
| tx.origin | a Phish contract the caller calls |
| integer-overflow | a transfer that wraps the balance |
| storage-collision | a write that lands on the wrong slot |
| weak-randomness | a Predict contract, the same-block answer |
| selfdestruct | funded deploy + `boom(target)` force-feed |
| uninitialized-proxy | `initialize` the impl/proxy |
| signature | a replayed/forged sig |
| accounting | deposit/withdraw that desyncs the tracked balance |
| visibility | `cast storage` the private slot |
| gas-griefing | a refusing partner / an unbounded loop |

## The verify

```bash
cast call $SETUP "isSolved()(bool)"    # false → true = solved
cast receipt <txhash>                   # status 0x1, from = caller
```

## The rules

- read `isSolved()` first — it names the class
- enumerate reachable functions before the first `cast send`
- `cast call`/`forge` is a sim — only `cast send` flips live state
- a `private` var is not a secret — `cast storage` reads it
- the private key stays out of notes
