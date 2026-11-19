# Evidence catalogue — the records a web3 solve produces

## Per-bug evidence shapes

| Bug | The evidence record |
|---|---|
| access-control | the `cast send` tx + `cast call owner()`/`locked()` before/after + `isSolved()` |
| reentrancy | the attack-contract deploy tx + the `attack()` tx + `cast balance` → 0 + `cast run` the recursive trace |
| delegatecall | the `delegatecall` tx + `cast storage` the owner/impl slot before/after |
| tx.origin | the Phish deploy + the `attack` tx + `cast call owner()` = the caller |
| integer-overflow | the tx + `cast call balances(me)` → `2**256-1` |
| storage-collision | the collision tx + `cast storage` the protected slot = the attacker |
| weak-randomness | the Predict deploy + the `attack` tx + the stored answer = the computed one |
| selfdestruct | the funded Force deploy + `boom` tx + `cast balance`/`cast code` the target |
| uninitialized-proxy | the `initialize` tx + `cast call owner()` = the caller |
| front-running | the atomic tx + the receipt's `logs` showing the order + `isSolved()` |
| signature | the `claim` tx + the recovered address + the balance change |
| accounting | the deposit/donate/withdraw txs + `cast balance`/`totalAssets` the desync |
| visibility | the `cast storage` read + the unlock tx + `locked()` → false |
| gas-griefing | the partner/loop tx + the `cast call` to the bricked function reverting |

## The universal evidence block

```text
instance:   RPC host, chain id
the setup:  setup address, challenge address
the predicate: the exact isSolved() expression
the class:  the bug class solved
the chain:  the ordered tx hashes + receipts
the state:  the before/after reads (getters, slots, balance)
the proof:  isSolved() false → true, verbatim
```

## The "no flag in the response" note

Unlike a web solve, there's no `flag{...}` in a response body — the flag is
whatever the checker/platform returns after `isSolved()` is true. The web3
solve's evidence is the on-chain transition; the flag's evidence is the
platform's response to the solved state.

## The negative-evidence

Each falsified path is also evidence — the revert reason, the read that stayed
false. `negative-results.md` records them; a chain's proof includes what was
tried and closed.
