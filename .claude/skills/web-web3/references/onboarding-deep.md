# Onboarding (deep) — the mental model and the discipline

## The paradigm shift from web

Web exploitation sends HTTP requests to a hidden server and reads responses.
Web3 sends signed transactions to a PUBLIC contract and reads on-chain state.
The differences that change the work:

- **no hidden server state** — `cast storage` reads every slot; `cast code`
  reads the logic. The only secret is a key never sent on-chain.
- **the exploit is attributable** — every `cast send` is signed by the supplied
  key and permanent. Iteration happens in `cast call`/`forge` dry-runs, not in
  sent transactions.
- **the proof is a state transition** — not a response string. `isSolved()`
  going `false → true` on the live chain, with a receipt, is the solve.
- **the attack surface is the caller's contracts too** — the supplied caller
  deploys `Phish`/`Predict`/`Force`/`Solver` contracts; the chain is the
  caller's deployed contracts calling the challenge's functions.

## The solved-condition read

`isSolved()` is the spec — it names the exact state to reach. A challenge's
whole difficulty is which reachable transition leaves that state satisfied.
Read it before the contract body; the predicate shape names the bug class.

## The bug-class mental model

The classes are the ways a call changes state the author didn't intend:

- **unguarded write** — a bare setter anyone calls
- **context confusion** — `delegatecall`/`tx.origin`/`msg.sender` mismatched
- **reentrancy** — a callback re-enters before the state settles
- **arithmetic** — a wrap or a desynced accounting
- **storage** — a write lands on the wrong slot / a `private` var is public
- **predictability** — `block.*`/the storage is a readable "secret"
- **destruction** — `selfdestruct` force-feeds or deletes

## The transaction discipline

- `cast call`/`cast storage`/`cast balance`/`cast code`/`cast logs` — free,
  unattributable, the iteration surface
- `cast send` — attributable, permanent, the solve action
- `forge test --fork-url`/`cast call` — the dry-run before the send
- never record the private key — record that it was used
- a reverted tx is a measurement — the reason names the unmet precondition

## The discipline

The budget is in TRANSACTIONS. Enumerate the reachable functions in the read;
name ONE transition; dry-run it; send it; verify `isSolved()`. A wrong guess
costs a real tx — the read/dry-run is where the iteration lives.
