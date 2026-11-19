# Extended corpus — the wider web3 attack surface

## The governance shapes

| Shape | The bug |
|---|---|
| a flash-loan of the gov token → a snapshot-vote | borrow → vote → repay in one tx — the borrowed balance passes the quorum |
| a proposal with a `delegatecall` action | the proposal's action runs attacker code on the treasury's storage |
| an unprotected `execute`/`propose` | anyone submits/executes |
| a timelock that isn't | the delay is bypassable or the check is missing |

## The bridge / cross-chain shapes

| Shape | The bug |
|---|---|
| a signature without a chainid/domain | a sig from chain A replays on chain B |
| a validator-quorum that's spoofable | the sig check accepts a forged/quorum-of-one sig |
| a message the contract doesn't bind to the sender/amount | a replayed or a forged message |
| a `mint`/`unlock` callable on a forged proof | the proof verification is bypassable |

## The oracle shapes

| Shape | The bug |
|---|---|
| a spot-price AMM oracle | a flash-loan swap skews the reserve → the price |
| a single-source oracle | the source is manipulable or compromised |
| a stale/cached price | the price lags the real one — the arb window |
| a `getPrice` that reads a manipulable balance | the balance is a flash-loan away |

## The MEV / the block-shape surface

| Shape | The bug |
|---|---|
| a transaction-ordering dependence | the atomic sequencer or a mempool copy |
| a `block.coinbase`/proposer dependence | the proposer's value |
| a `block.basefee`/`gasprice` read | public per-block |
| a same-block-sandwich window | the front/back-run pair |

## The access-granularity shapes

| Shape | The bug |
|---|---|
| a role that grants too much | `onlyRole(X)` where X controls the whole treasury |
| a `transferOwnership`/`renounce` callable | ownership moves/abandons unintentionally |
| a `pausable`/`freeze` the attacker can trigger | the contract bricks itself |
| a `killSwitch`/`emergency` reachable | the callable halt |

## The data-availability shapes

| Shape | The bug |
|---|---|
| a `private` var as the secret | `cast storage` reads it |
| an event emitting the secret | `cast logs` reads it |
| a constructor arg as the key | `cast tx` the deploy reads it |
| calldata in a past tx | `cast tx`/the mempool reads it |
| a `bytes32` that's a hash of a small space | brute it — `keccak("rock")` etc. |

## The non-EVM-adjacent surface

A "web3" challenge that's actually a WASM/other-VM contract, or a Solana/Cosmos
program — the primitives differ (no `delegatecall`, different accounts model)
but the class logic is the same: a reachable state-transition flips a predicate.
The corpus's EVM-specific files map only loosely to non-EVM — flag it as a
different class if the VM isn't EVM.
