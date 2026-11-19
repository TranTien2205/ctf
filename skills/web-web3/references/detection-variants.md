# Detection variants — the detection angle by available artifact

## When source is shipped

- `Setup.sol`/`Challenge.sol` readable → the source signals + the reachable
  functions; `detection-map.md`'s source table
- the pragma + the keywords + the modifiers + the function bodies

## When only bytecode is available

- `cast code` → `evm disasm`/`heimdall`/`panoramix` → the dispatch table + the
  SSTORE map + the context ops → `detection-deep.md`'s bytecode table
- `cast 4byte <selector>` resolves the function selectors to signature guesses
- the `SSTORE`-to-predicate-slot map = the reachable-transition inventory

## When only an address + ABI is given

- the ABI lists the functions — the reachable surface
- `cast call` the getters + `cast storage` the slots → the state
- the bytecode still readable via `cast code` for the real logic

## When the source is a decoy

- `cast code` differs from the `.sol` → trust the bytecode — `evasion.md`
- the dispatch/SSTORE map reveals the real surface

## When the predicate isn't obvious

- no `isSolved()` → the contract's `solved()`/`flag()`/`winner()`/a state the
  checker watches — the contract's docs/comments name it
- `cast call` the candidate getters; the setup's naming convention

## When the setup deploys several contracts

- map them — `cast call` the setup's getters for each deployed address
- the predicate's contract is the target; the others are the path/red herrings
- `per-target.md` for the contract-type → bug map

## When it's a non-EVM contract

- a WASM/Solana/Cosmos contract — different primitives; the class logic (a
  reachable transition flips a predicate) holds, but the EVM-specific files map
  loosely — flag it as a different class if the VM isn't EVM

## The detection-completeness check

- [ ] the predicate's exact expression recorded
- [ ] the reachable non-view functions enumerated
- [ ] the class named (the predicate + a reachable transition)
- [ ] the falsifier NOT observed — the path is open
