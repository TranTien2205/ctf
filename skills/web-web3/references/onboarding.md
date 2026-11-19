# Onboarding — how to work this class

## What this class is

A smart-contract challenge: a `Setup.sol` + `Challenge.sol`, an RPC endpoint to
a private chain, and a private key. The win is driving the contract's state so
`isSolved()` returns `true`, with a transaction attributable to the supplied
caller. There is no HTTP request to inject — the "parameter" is a transaction
and the "response" is on-chain state.

## The three rules

1. **Read `isSolved()` first.** The predicate names the target state and aims
   the whole detection — an `owner()` check points at access-control, a
   `balance == 0` at a drain, a `flag` at a setter.
2. **Read-only before write.** `cast call`/`cast storage`/`cast balance` are
   free and unattributable; `cast send` is permanent and attributable.
   Enumerate the reachable functions in the read before spending a transaction.
3. **Dry-run before send.** `forge test --fork-url`/`cast call` simulates the
   exploit; only `cast send` flips the live predicate. A "solved" on the fork
   that the live `isSolved()` doesn't confirm is not a solve.

## The mental model

The contract is a state machine; `isSolved()` reads state. The exploit is the
reachable call whose post-state satisfies it. The bug classes are the ways a
call changes state the author didn't intend: unguarded setters, delegatecall,
reentrancy, tx.origin, arithmetic wraps, storage collisions, predictable
randomness, force-fed ether.

## The toolchain

`cast` (foundry) for the RPC — `call`/`send`/`storage`/`balance`/`code`/`tx`/
`receipt`/`chain-id`/`logs`/`4byte`/`index`/`keccak`. `forge` for the local
fork test and the attack contract. `evm`/`heimdall`/`panoramix` to decompile
bytecode-only targets. The private key stays out of notes.

## Where to go next

`detection.md` for the package read, `attack-shapes.md` for the
predicate→class map, `per-bug.md` for the bug→call map, `workflow.md` for the
order, `evidence-rules.md` for what a solve looks like.
