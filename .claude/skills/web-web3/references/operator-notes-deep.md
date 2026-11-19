# Operator notes (deep) — the field-tested details

## The `cast` habits that pay

- `cast call $CH "fn()"` before `cast send` — the dry-run is free; the send is
  attributable.
- `cast storage $CH <slot>` reads ANY slot — `private` vars, the predicate's
  slots, the impl's address.
- `cast code $CH` early — the deployed bytecode is the truth, not the shipped
  `.sol`.
- `cast run <txhash>`/`forge -vvvv` — the trace names the failing `require`.
- `cast 4byte <selector>` resolves a raw selector to a signature guess.
- `cast index`/`cast keccak` compute a mapping/array slot for `cast storage`.

## The attack-contract habits

- `constructor() payable` + `cast send --create --value` — fund the contract at
  deploy when the exploit needs it to hold ether.
- `receive() external payable` — hold a force-fed or deposited balance.
- `function sweep()` — return the drained/exploit ether to the caller.
- bound the `receive` recursion — by `address(v).balance` or a counter — an
  unbounded loop runs out of gas and reverts the drain.
- `me = msg.sender` in the constructor — record the attributable caller.

## The predicate habits

- read `isSolved()` BEFORE the contract body — it names the class.
- `isSolved() → true` BEFORE the exploit means a stale read or a pre-solved
  setup — re-read the setup.
- a `isSolved()` on the SETUP (not the challenge) is the checker's read — use it.

## The detection habits

- the bare setter FIRST — `setOwner`/`unlock`/`setFlag`/`initialize` — the
  cheap solve is the common case.
- the dispatch table + the `SSTORE` map for a bytecode-only target — the
  reachable surface without source.
- the `grep -n` the source for `delegatecall`/`tx.origin`/`block.`/`ecrecover`/
  `selfdestruct`/`unchecked`/`private` — the class signals.

## The transaction habits

- a revert's REASON is the signal — `cast run` the trace; a sixth variant of
  the same transition doesn't help.
- the attack contract's deployed address comes from the receipt's
  `contractAddress`, not a guess.
- `--gas-limit` when a tx underestimates; `--value` when the exploit needs ether.
- `cast getAddress`/`cast compute-address` for the deploy address when a
  contract must reference its own/another's address pre-deploy.

## The key/secret habits

- the private key never in notes — record the ADDRESS and "the supplied key."
- a `private` var is not a secret — `cast storage` reads it.
- a constructor arg / an event-emit / a calldata — all leak on-chain.
- per-instance values — RPC/key/addresses read fresh; never reuse a dead instance's.
