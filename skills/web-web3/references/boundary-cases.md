# Boundary cases — the limits of each class

## The reachable-transition boundary

The whole class needs a reachable transition — a function the supplied caller
(or a contract they deploy) can call whose post-state satisfies `isSolved()`.
The boundary:

- **inside**: a reachable `SSTORE` to a predicate slot exists
- **outside**: every reachable function is guarded AND none writes the
  predicate's slots → the class is closed for this contract

## The attributable boundary

The solve must be `from` the supplied caller — the receipt's `from` must match
`cast wallet address --private-key $KEY`. A tx from a different key, a solve
needing a key the challenge didn't supply, a solve on a different instance —
all outside.

## The simulation-vs-live boundary

- **inside**: a `cast send` that flipped the live `isSolved()`
- **outside**: a `forge`/`cast call` sim — a dry-run, not the solve

## The per-class boundary

| Class | Inside | Outside |
|---|---|---|
| access-control | a reachable unguarded setter | every writer guarded + unbypassable |
| reentrancy | a `call`-then-update to attacker code | `.transfer`/`.send`/`nonReentrant`/CEI |
| delegatecall | a `delegatecall` to a controlled/mismatched target | no delegatecall / fixed + matching |
| tx.origin | a `tx.origin` check + a contract in the chain | `msg.sender` correct + no contract path |
| integer-overflow | `<0.8` or `unchecked` + a wrapping path | `>=0.8` + SafeMath + no unchecked |
| weak-randomness | a `block.*`/readable decision source | commit-reveal / VRF / no predictable source |
| selfdestruct | a `selfdestruct` reachable / a balance predicate | no selfdestruct + the predicate isn't balance |
| uninitialized-proxy | a callable `initialize` | initialized + protected |
| signature | a replayable/malleable/zero-addr hash | a fully-bound hash + low-s |
| accounting | a desync path | every in/out updates atomically |
| visibility | a `private` secret the predicate needs | the secret is genuinely off-chain |
| gas-griefing | a push-payment/loop the contract depends on | pull-payment / bounded loop |

## The catalogue-boundary

`web-web3` is `catalogue` — the corpus is published knowledge; a solve moves it
to `verified`. The corpus's claims are the standard CTF shapes — the live
chain's behavior is the ground truth; a module that disagrees with it is the
module that's wrong, and a field-note corrects it.
