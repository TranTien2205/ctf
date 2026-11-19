# Summary map — the class at a glance, all surfaces

## The one-line class

A `Setup.sol` + `Challenge.sol` + an RPC + a key; `isSolved()` is the spec;
the solve is a `cast send` from the supplied caller that flips it.

## The one-line method

read `isSolved()` → enumerate the reachable calls → the one that writes the
predicate's slot → dry-run → `cast send` → `isSolved() → true` + the receipt.

## The bug classes, one line each

- **access-control** — a setter no one guarded
- **reentrancy** — a `call` that runs the callee before settling
- **delegatecall** — foreign code writing your storage
- **storage-collision** — the delegatecall write landing wrong
- **tx.origin** — the origin-vs-sender confusion
- **integer-overflow** — the pre-0.8 wrap
- **weak-randomness** — `block.*` as a "secret"
- **selfdestruct** — force-feeding or deleting
- **uninitialized-proxy** — the callable `init`
- **front-running** — the ordering the contract depends on
- **signature** — the replayable/malleable sig
- **accounting** — the tracked-vs-real desync
- **visibility** — the readable `private`
- **gas-griefing** — the refusing partner / the unbounded loop

## The discipline, one line

- the predicate names the class — read it first
- the enumeration is free — the send is attributable
- `cast call`/`forge` = sim; `cast send` = the solve
- `cast storage` reads `private` — no on-chain secret
- the receipt + `isSolved() → true` + `from` = caller = the solve
- the private key stays out of notes
- `catalogue` — published knowledge; `../field-notes.md` the local layer

## The file index, one line

- `mechanism*`/`evm-primitives` — the model
- `detection*`/`attack-shapes`/`per-*` — the maps
- the bug files — the classes
- `payload*`/`exploitation*` — the calls
- `evidence*`/`verification*` — the proof
- `workflow*`/`first-hour`/`field-manual`/`checklist`/`onboarding*` — the order
- `edge-cases`/`common-mistakes`/`anti-patterns`/`troubleshoot`/`evasion`/`theory*` — the traps + the why
- `case-studies`/`real-world-cases`/`verified-chains`/`field-notes-deep` — the cases + the honest status
