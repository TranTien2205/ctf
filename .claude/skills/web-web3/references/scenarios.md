# Scenarios — the challenge-shape → the solve path

## "a contract + an RPC + a key, nothing else"

The standard shape — read `isSolved()`/`Setup.sol`, the predicate names the
class, enumerate the reachable calls, send the transition. `workflow.md`.

## "just a deployed address — no source"

Bytecode-only — `cast code` + `evm disasm`/`heimdall` → the dispatch + the
SSTORE map → the reachable surface. `detection-deep.md`, `evasion.md`.

## "a proxy pointing at an impl"

`storage-collision`/`uninitialized-proxy`/`delegatecall` — read the impl slot,
check the layouts, check the init's callable contexts. `delegatecall.md`.

## "the contract holds ether and pays out"

`reentrancy`/`accounting-vault`/`selfdestruct` — a `call`-then-update, a
desync, a force-feed. `reentrancy.md`, `accounting-vault.md`.

## "the contract wants a guess/an answer"

`weak-randomness`/`visibility` — the `block.*` source or a `private` seed — a
Predict contract or a `cast storage` read. `weak-randomness.md`.

## "the contract needs a signature"

`signature-replay` — the `ecrecover` hash's fields; replay/forge/zero-address.
`signature-replay.md`.

## "a King/Elevator/Gatekeeper contract"

`gas-griefing-dos`/`tx-origin`/`edge-cases` — the refusing partner, the
EOA-check, the gasleft key. `gas-griefing-dos.md`, `tx-origin.md`.

## "a Vault/Bank/Staking/Dex"

`accounting-vault`/`flashloan-oracle` — the deposit/withdraw/rate desync, the
flash-loan skew. `accounting-vault.md`.

## "a Token/ERC contract"

`token-standards`/`integer-overflow`/`accounting-vault` — the standard's
surfaces, the old-pragma wrap, the desync.

## "the challenge is a private chain + a script"

A non-`cast` toolchain — `web3.py`/`ethers.js`/a python script — the primitives
are the same; the calls differ. `evm-primitives.md` for the model.

## "the contract is already solved"

`isSolved()` reads `true` on the fresh instance — the setup was pre-solved, or
the predicate reads a different contract. Re-read `Setup.sol`.
