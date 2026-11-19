# Operator notes — the field-tested habits

## The reads that always pay

- **`cast call $SETUP "isSolved()(bool)"` before and after** — the predicate flip
  is the proof; without the before, a `true` could be a stale read.
- **`cast storage` the low slots** — `private` vars leak; the owner/impl/flag
  slots show the state the predicate reads.
- **`cast code` early** — the shipped `.sol` can lie; the bytecode is the truth.
- **the dispatch table / `SSTORE` map** — the reachable-function inventory and
  which slots each writes.

## The transaction habits

- **dry-run every send** — `forge test --fork-url`/`cast call` — a sim-fail is
  free; a live-fail costs gas and is attributable.
- **fund the attack contract** — a `payable` exploit needs the deploy to carry
  `value` (`--value`).
- **bound the reentrancy loop** — an unbounded `receive` recursion runs out of
  gas and reverts the whole drain.
- **read the revert reason** — `cast run <txhash>`/`forge -vvvv` traces the
  failing `require` — it names the unmet precondition.

## The class-selection habit

- **the bare setter first** — an unguarded `setOwner`/`unlock`/`setFlag` is the
  intended solve more often than a deep bug. Check it before delegatecall.
- **the predicate names the class** — `owner()` → access-control; `balance` →
  drain; `flag` → setter/visibility. Don't guess a class the predicate doesn't
  point at.
- **the reachable-writers enumeration closes the class** — if no reachable
  function writes the predicate's slot, the class is falsified — escalate.

## The trap habits

- **`cast call` is not a solve** — it's a dry-run. The live `cast send` + re-read
  `isSolved()` is the only proof.
- **the private key stays out of notes** — record that the supplied key was
  used, never its value.
- **per-instance everything** — RPC, key, addresses — read them fresh each
  instance; never hardcode a dead instance's values.
- **`blockhash(block.number)` is `0`** — a contract that reads it computes on `0`.
- **a contract in its constructor is `extcodesize == 0`** — the EOA check is
  bypassed by a constructor call.

## The budget habit

3 reverted transactions on the same transition with no new revert reason → the
path is stuck. `decide.py escalate` — the common cause is a wrong class guess;
re-read the predicate and the reachable-call inventory.
