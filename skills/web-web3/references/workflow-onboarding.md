# Workflow onboarding — the operation for someone new to the class

## The first thing to internalize

A web3 challenge is NOT a web challenge. There's no HTTP request to inject, no
response to read a flag from. There's a Solidity contract on a private chain,
an `isSolved()` predicate, and a private key to send transactions with. The
win is a transaction that flips the predicate — a `cast send` that leaves
`isSolved() == true` on the live chain.

## The first commands

```bash
export RPC=<rpc> KEY=<privkey>      # the per-instance environment
cast chain-id --rpc-url $RPC        # the chain
cast wallet address --private-key $KEY  # YOUR attributable address
cast call $SETUP "isSolved()(bool)" --rpc-url $RPC   # the predicate — false
```

## The first read

`Setup.sol` — the `isSolved()` expression is the SPEC. It names the state to
reach: `owner() == you`, `balance == 0`, `locked() == false`, `answer ==
guess`. The predicate's shape names the bug class — `attack-shapes.md`.

## The first inventory

Read `Challenge.sol`'s external/public non-view functions — which write the
slots `isSolved()` reads? The unguarded one (`setOwner`/`unlock`/`setFlag`/
`initialize`) is the intended solve more often than a deep bug — check it
FIRST with a single `cast send`.

## The first transaction

```bash
cast send $CH "setOwner(address)" $ME --private-key $KEY --rpc-url $RPC
cast call $SETUP "isSolved()(bool)" --rpc-url $RPC   # → true?
```

`cast send` is attributable and permanent — `cast call`/`forge` the dry-run
first; the send is the solve action.

## The bug-class orientation

The classes are the ways a contract can't trust its callers: it can't hide
state (`private` is public), can't tell the caller apart from a contract
(`tx.origin`/`msg.sender`), can't control the callback (`call` → reentrancy),
can't trust `delegatecall` (storage-write), can't get real randomness
(`block.*`), can't keep arithmetic in range (pre-0.8). `mechanism.md` is the
model; the bug files are the misuses.

## The proof

`isSolved()` → `true` on the live chain + a `status: 0x1` receipt `from` the
supplied caller — that's the solve. A `cast call`/`forge` simulation is NOT —
it's a dry-run.

## The files to open next

`workflow.md` the order, `detection.md` the package read, `per-bug.md` the
bug→call map, `evidence-rules.md` the proof standard, `onboarding-deep.md` the
discipline.
