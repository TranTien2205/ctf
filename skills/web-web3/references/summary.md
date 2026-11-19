# Summary — the web3 class in one page

## The class

A `Setup.sol` ships a `Challenge.sol` on a private chain with an `isSolved()`
predicate. The solve is a transaction from the supplied caller that leaves the
predicate's state satisfied — `isSolved()` goes `false → true` on the live chain.

## The method

1. Read `isSolved()` — the predicate names the class
2. Enumerate the reachable non-view functions — which write the predicate's slots
3. Read the state — `cast call`/`cast storage`/`cast balance`/`cast code`
4. Name ONE transition; dry-run it (`forge --fork-url`/`cast call`)
5. `cast send` it from the supplied caller — attributable
6. Re-read `isSolved()` — `false → true` + the receipt = the solve

## The bug classes

- **access-control** — a bare setter
- **reentrancy** — a callback re-enters
- **delegatecall** — foreign code writes the caller's storage
- **storage-collision** — a write lands on the wrong slot
- **tx.origin** — the origin vs the sender
- **integer-overflow** — the wrap
- **weak-randomness** — the predictable source
- **selfdestruct** — force-feed / delete
- **uninitialized-proxy** — the callable init
- **front-running** — the ordering
- **signature** — the replay/forge
- **accounting** — the balance desync
- **visibility** — the readable `private`
- **gas-griefing** — the refusing partner / the unbounded loop

## The rules

- the predicate names the class — read it first
- the reachable-call enumeration is the detection — before any send
- `cast call`/`forge` is a sim — only `cast send` flips live state
- `cast storage` reads `private` vars — no secret on-chain
- the receipt's `status: 0x1` + `isSolved()` true = the solve
- the private key stays out of notes
- a `catalogue` class — the corpus is published knowledge, not local solves

## The pointer set

- `mechanism.md`/`evm-primitives.md` — the execution model
- `detection.md`/`attack-shapes.md`/`detection-index.md` — the class-naming
- `per-bug.md`/`per-mechanism.md`/`decision-table.md` — the maps
- `workflow.md`/`first-hour.md`/`exploitation.md` — the order
- `evidence-rules.md`/`verification-protocol.md` — the proof standard
- the bug files — `reentrancy`, `delegatecall`, `tx-origin`, `access-control`, ...
