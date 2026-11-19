# Summary (deep) — the web3 class, complete

## The challenge form

A `Setup.sol` + a `Challenge.sol` + a private-chain RPC + a private key. The
checker calls `isSolved()` — the solve is the state transition that flips it,
attributable to the supplied caller.

## The detection

`isSolved()`'s predicate names the class. The reachable non-view functions are
the candidate transitions — the one that writes the predicate's slot unguarded
(or via a bug) is the solve. `cast call`/`storage`/`balance`/`code` are the free
reads; `cast send` is the attributable write.

## The bug classes (the whole set)

- **access-control** — a bare setter, a re-init, a default-visibility, a
  constructor-as-function, a bypassable guard
- **reentrancy** — a `call`-then-update; single/cross-function/cross-contract/
  read-only; the ERC-777/721 hooks
- **delegatecall** — a controlled target, a storage collision, an
  uninitialized shared library
- **storage-collision** — the delegatecall write lands on the wrong slot; a
  packed/array collision
- **tx.origin** — `!=`/`==`/`=` checks defeated by a contract in the middle or
  a constructor
- **integer-overflow** — `<0.8` wrap or a `>=0.8` `unchecked` block
- **weak-randomness** — `block.*`/`private`-state as a "random"/"secret"
- **selfdestruct** — force-feed ether, delete code, the library-kill
- **uninitialized-proxy** — a callable `initialize` in the impl/proxy context
- **front-running** — the ordering/atomicity dependence
- **signature** — the replay/malleability/zero-address/wrong-hash
- **accounting** — the tracked-balance desync, the first-depositor, the
  share-price, the flash-loan
- **visibility** — `private`/`internal`/`event`/constructor-arg as a secret
- **gas-griefing/DOS** — the refusing partner, the unbounded loop
- **token-standards** — the ERC-20/721/777/1155 surfaces
- **flashloan-oracle** — the atomic skew of a manipulable source

## The method

read the predicate → enumerate the reachable calls → name the class → name ONE
transition → dry-run it → `cast send` it → verify `isSolved() → true` + the
receipt.

## The rules

- the predicate names the class — read it first
- the inventory is the detection — before any send
- `cast call`/`forge` is a sim — only `cast send` flips live
- `cast storage` reads `private` — no on-chain secret
- `status: 0x1` + `isSolved()` true + `from` = caller = the solve
- the private key stays out of notes
- `catalogue` — published knowledge, not local proof
