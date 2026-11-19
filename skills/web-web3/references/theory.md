# Theory — why the web3 bug classes exist

## The contract-can't-trust root

A smart contract is immutable, public, and callable by anyone. It can't hide a
secret (`cast storage` reads everything), can't tell its caller apart from a
contract (`tx.origin`/`msg.sender` confusion), can't control what a `call`ed
contract does back (reentrancy), and can't take back a transaction. Every bug
class is one of those limits:

- **it can't hide state** → visibility (the readable `private`)
- **it can't tell the caller** → tx.origin (the phish), extcodesize-0 (the
  constructor)
- **it can't trust callee behavior** → reentrancy (the callback), delegatecall
  (the storage-write)
- **it can't take back a tx** → every exploit is permanent and attributable
- **it can't get real randomness** → weak-randomness (the `block.*` source)
- **it can't change its code** → delegatecall/proxy (the workaround IS the bug)
- **its arithmetic wraps** → integer-overflow (pre-0.8)

## The attribution-and-finality root

Every transaction is signed and final — the solve is attributable and permanent.
This is why the read/dry-run (`cast call`/`forge`) is where iteration lives, and
why `cast send` is the solve action — there's no undo.

## The "the contract IS the state" root

There's no hidden server — the contract's code + storage ARE the system. The
challenge is entirely about REACHABILITY: which transaction leaves the
predicate's slots satisfied. The bug classes are the reachable state-changes
the author didn't intend.

## The public-ledger root

Storage, code, call history, events — all public. A contract that hides a secret
is broken by design; a contract that assumes a private value is broken by
`cast storage`. The only real secret is a key never sent on-chain.

## The catalogue-honest note

This is `catalogue` — published knowledge, not local solves. The theory explains
WHY the classes exist; `verified-chains.md` records the honest status.
