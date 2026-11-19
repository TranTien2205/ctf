# Closing index — the final reference

## The one-paragraph class

A `Setup.sol` deploys a `Challenge.sol` on a private chain with an `isSolved()`
predicate. The supplied caller's transactions are the only way to change the
contract's state. The solve is the attributable transaction — a `cast send`
from the supplied key — that leaves `isSolved() == true` on the live chain, with
a receipt (`status: 0x1`, `from` = the caller) proving it mined.

## The one-paragraph method

Read `isSolved()` — the predicate names the class. Enumerate the reachable
non-view functions — which write the predicate's slots? The unguarded setter is
the solve more often than a deep bug; when none exists, the bug-class the
predicate forces (`delegatecall`, `reentrancy`, `tx.origin`, `selfdestruct`,
`integer-overflow`, `weak-randomness`, `signature`, `accounting`, `visibility`,
`uninitialized-proxy`, `front-running`, `gas-griefing`) is the path. `cast
call`/`forge` the dry-run; `cast send` the solve; `cast call isSolved()` +
`cast receipt` the verify.

## The one-paragraph honest-status

`web-web3` is a `catalogue` class — this toolkit has never solved one. The
corpus is the standard CTF web3 surface (Ethernaut/Capture-the-Ether/Damn-
Vulnerable-DeFi shapes, the EVM semantics, the foundry/cast toolchain) —
published knowledge, not local proof. A real solve's `../field-notes.md` entry is
what moves the class to `verified`.

## The traps in one breath

- `cast call`/`forge` is a simulation — never the solve
- a `status: 0x1` without `isSolved() → true` is a mined no-op
- a `private` var is readable — `cast storage`
- the bytecode can differ from the `.sol` — `cast code`
- `.transfer`/`.send` don't re-enter — `call` does
- `delegatecall` writes the CALLER's storage by slot
- `tx.origin` is not `msg.sender` — a contract sits between
- `blockhash(block.number)` is `0` — the current block has no hash
- `>=0.8` reverts arithmetic — `<0.8`/`unchecked` wraps
- `selfdestruct` force-sends ether no one can refuse
- the private key never goes in notes
- per-instance values — never reuse a dead instance's RPC/key/addresses

## The pointer set

- `README.md` — the index
- `index.md` — every file listed
- `workflow-index.md` — the procedure files
- `per-bug-catalogue.md` — every class indexed
- `detection-index-deep.md` — the complete signal inventory
- `summary-map.md` — the one-line map

## The last word

The class exists because a contract can't tell its caller apart from a contract,
can't hide its storage, can't control what a `call`ed contract does back, can't
take back a transaction, and can't trust its own arithmetic — every bug is one
of those limits, and `isSolved()` picks which one the challenge exercises.
