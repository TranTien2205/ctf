# Glossary — the web3 vocabulary

## The challenge terms

| Term | Definition |
|---|---|
| **Setup contract** | the contract that deploys the challenge and holds `isSolved()` |
| **solved predicate** | the `isSolved()`/`solved()` boolean the checker reads |
| **the supplied caller** | the private key the challenge provides — the attributable EOA |
| **the instance** | the per-challenge RPC + key + addresses — never reusable |

## The EVM terms

| Term | Definition |
|---|---|
| `msg.sender` | the immediate caller — a contract or an EOA |
| `tx.origin` | the EOA that started the whole transaction — never changes down a call chain |
| `msg.value` | the ether sent with the call |
| `msg.data`/`calldata` | the selector + the encoded args |
| `address(this)` | the contract whose storage the frame reads/writes |
| `extcodesize` | a contract's code size — `0` for an EOA OR a contract in construction |
| `selfdestruct` | erases code+storage, force-sends the balance |
| `SSTORE`/`SLOAD` | storage write/read opcodes |
| the `fallback`/`receive` | the unmatched/ether-call entry point |

## The call primitives

| Term | Definition |
|---|---|
| `call` | foreign call — callee's storage, caller is `msg.sender` |
| `delegatecall` | foreign code on CALLER's storage — `msg.sender`/`value` preserved |
| `staticcall` | read-only foreign call — no state writes |
| `callcode` | legacy delegatecall |

## The bug-class terms

| Term | Definition |
|---|---|
| **reentrancy** | a callback re-enters before the caller settles state |
| **delegatecall bug** | foreign code writes the caller's storage |
| **storage collision** | a delegatecall write lands on the wrong slot |
| **tx.origin phish** | a contract between the EOA and the target confuses origin/sender |
| **force-feed** | `selfdestruct` sends ether a contract can't refuse |
| **uninitialized proxy** | an `initialize` callable post-deploy owns the context |
| **weak randomness** | `block.*`/readable-state used as a secret |
| **the predicate slot** | the storage `isSolved()` reads |
| **the reachable transition** | a call the supplied caller can send that changes the predicate's state |

## The evidence terms

| Term | Definition |
|---|---|
| **the attributable tx** | a `cast send` `from` the supplied caller — the receipt's `from` |
| **the predicate flip** | `isSolved()` false → true on the live chain |
| **the receipt** | `status`, `from`, `to`, `logs`, `gasUsed` — the mined-tx proof |
| **the dry-run** | a `cast call`/`forge test` — a simulation, not the solve |
