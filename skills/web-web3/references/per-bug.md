# Per-bug map — bug class → the file → the first call

| Bug class | File | The detection | The first call |
|---|---|---|---|
| access-control / unprotected setter | `access-control.md` | a non-view public fn writes the predicate's slot, no guard | `cast send "setOwner(address)"` |
| reentrancy | `reentrancy.md` | external call before state update | deploy a `receive`-reenter, deposit+withdraw |
| delegatecall | `delegatecall.md` | a `delegatecall` to an influenceable/mismatched target | call through the proxy to write the owner slot |
| tx.origin | `tx-origin.md` | `tx.origin` used for auth | a Phish contract the caller calls |
| integer overflow/underflow | `integer-overflow.md` | `<0.8` pragma or `unchecked` | `cast send` a transfer that wraps |
| storage collision | `storage-collision.md` | proxy/impl slot mismatch | `cast send "setA(address)"` to write the wrong slot |
| weak randomness | `weak-randomness.md` | `block.*`/`keccak(public)` feeding a decision | a Predict contract computing the same-block answer |
| selfdestruct / force-feed | `selfdestruct.md` | `selfdestruct` reachable, or a balance-check predicate | funded deploy + `boom(target)` |
| uninitialized proxy | `uninitialized-proxy.md` | an `initialize` callable | `cast send "initialize(address)"` |
| front-running / ordering | `front-running.md` | a first-come/order-dependent win | a contract sequencing the calls atomically |
| signature / ecrecover | `signature-replay.md` | `ecrecover` + a replayable/malleable hash | `cast send` the replayed/forged sig |
| accounting / vault / token | `accounting-vault.md` | a deposit/withdraw desync | the deposit/donate/withdraw sequence |
| visibility / private-as-secret | `visibility.md` | a `private` var as a secret | `cast storage` the slot, feed it to the gate |
| constructor / extcodesize | `edge-cases.md` | an `extcodesize == 0` EOA check | call from a contract's constructor |
| blockhash / future-block | `weak-randomness.md` | `blockhash(n)` used as random | the answer is `blockhash`/`0` at the right block |

## The class-falsifier

Each row's file carries the falsifier — the observation that closes that bug.
When a path's falsifier is observed, mark it dead and move to the next row —
the predicate's reachable-writers enumeration is the class-closing test.
