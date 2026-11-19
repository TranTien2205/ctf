# Glossary (deep) — the complete web3 vocabulary

## The challenge terms

| Term | Definition |
|---|---|
| **Setup contract** | deploys the challenge, holds `isSolved()` |
| **solved predicate** | the `isSolved()`/`solved()` boolean the checker reads |
| **the supplied caller** | the private key the challenge provides — the attributable EOA |
| **the instance** | the per-challenge RPC + key + addresses |
| **the target** | the contract the predicate reads |

## The EVM terms

| Term | Definition |
|---|---|
| `msg.sender` | the immediate caller (contract or EOA) |
| `tx.origin` | the EOA that started the tx — constant down the chain |
| `msg.value` | the ether sent with the call |
| `msg.data`/`calldata` | the selector + encoded args |
| `msg.sig` | `msg.data[:4]` — the function selector |
| `address(this)` | the contract whose storage the frame uses |
| `extcodesize`/`codesize` | the code size — `0` for EOA or a constructor |
| `SSTORE`/`SLOAD` | the storage write/read ops |
| `SSTORE`-in-delegatecall | writes the CALLER's slot at the callee's position |
| `revert`/`require`/`assert` | the guard — rolls back state, spends gas |
| `gasleft()` | remaining gas — a gate or a loop bound |

## The call primitives

| Term | Definition |
|---|---|
| `call` / `call{value}` | a foreign call — callee's storage, forwards gas+value |
| `delegatecall` | foreign code on CALLER's storage — sender+value preserved |
| `staticcall` | read-only foreign call |
| `callcode` | legacy delegatecall |
| `selfdestruct` | erases code+storage, force-sends the balance |
| `create`/`create2` | deploy — CREATE2's address is predictable |
| `receive()`/`fallback()` | the ether-call / unmatched-call entry |

## The bug-class terms

| Term | Definition |
|---|---|
| **reentrancy** | a callback re-enters before the caller settles |
| **delegatecall bug** | foreign code writes the caller's storage |
| **storage collision** | a write lands on the wrong slot |
| **tx.origin phish** | a contract confuses origin vs sender |
| **force-feed** | `selfdestruct` sends ether a contract can't refuse |
| **uninitialized proxy** | a callable `initialize` on the impl/proxy |
| **weak randomness** | `block.*`/readable state as a secret |
| **the predicate slot** | the storage `isSolved()` reads |
| **the reachable transition** | a caller-sendable call that flips the predicate |
| **the attributable tx** | a `cast send` from the supplied caller |
| **the predicate flip** | `isSolved()` false → true |
| **the dry-run** | a `cast call`/`forge` sim — not the solve |
| **the catalogue class** | published knowledge, no local solve |

## The Solidity terms

| Term | Definition |
|---|---|
| `onlyOwner`/`onlyX` | a modifier guard — check what it reads |
| `nonReentrant` | a reentrancy flag |
| `payable` | accepts `msg.value` |
| `internal`/`private` | contract-internal / other-contract-hidden (not storage-hidden) |
| `external`/`public` | the reachable surface |
| `view`/`pure` | reads/no-state functions — the free probes |
| `unchecked` | 0.8+ — deliberately wraps arithmetic |
| `SafeMath` | pre-0.8 — the wrap-check library |
| `pragma` | the compiler version — `<0.8` wraps, `>=0.8` reverts |
| `modifier` | a function guard |
| `constructor` | the deploy-time init — `extcodesize 0` inside |
