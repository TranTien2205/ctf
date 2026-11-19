# Recon order — what to read in what order

## The order

1. **`Setup.sol`'s `isSolved()`** — the predicate; names the class before
   anything else
2. **`Challenge.sol` source** — the reachable functions; which write the
   predicate's slots
3. **the deployed bytecode** — `cast code` — does it match the source?
4. **the live state** — `cast call` the getters, `cast storage` the slots,
   `cast balance`
5. **the environment** — RPC, chain id, the supplied caller's address
6. **the other setup deploys** — every contract `Setup` deploys — a red herring
   vs the real target
7. **the events/logs** — `cast logs`/`cast tx` — constructor args, emitted secrets
8. **the reachable-call inventory** — every non-view external/public function

## The read-only budget

The entire recon is read-only — `cast call`/`storage`/`balance`/`code`/`logs`
cost nothing and aren't attributable. The only attributable action is a
`cast send` — hold it until the transition is named and dry-run.

## The predicate-first rule

Reading `isSolved()` before the contract body aims the whole recon — the
predicate's shape says which slots to watch and which bug class to expect. A
recon that starts with the contract body wastes the read on unneeded functions.

## The bytecode-diff checkpoint

`cast code` early — if the deployed bytecode doesn't match the shipped source,
the source is a decoy and the bytecode's dispatch/SSTORE map is the real
surface. Don't spend the read pass on a misleading source.

## The inventory-first rule

The reachable-function enumeration IS the detection — the class is "a reachable
transition flips the predicate," and the inventory is where that transition is
found. The bug-class modules name the MECHANISM; the inventory names the
concrete function.
