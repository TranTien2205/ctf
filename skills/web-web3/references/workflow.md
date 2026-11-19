# Workflow — from the challenge package to the solve

## Order of operations

1. **Read the setup contract and the solved predicate first.** `Setup.sol`'s
   `isSolved()` names the exact state to reach — it points at the bug class.
2. **Read the challenge contract.** Map the reachable non-view functions; mark
   which write the slots `isSolved()` reads.
3. **Capture the environment.** RPC, chain id, setup address, challenge
   address, the supplied caller — record hostnames/addresses, never the key.
4. **Read the starting state.** `cast call` every predicate-relevant getter;
   `cast storage` the relevant slots; `cast balance` the contract.
5. **Name the cheapest transition.** The reachable call whose post-state
   satisfies the predicate — usually the unguarded setter, then the bug-class
   path the predicate forces.
6. **Dry-run the exploit.** `cast call`/`forge` the exact call — does the
   simulated `isSolved()` flip? A simulation is a prediction, not a solve.
7. **Send the attributable transaction.** `cast send` from the supplied caller.
8. **Verify on-chain.** Re-read `isSolved()` — `false → true` — and keep the
   receipt + tx hash.

## The first commands

```bash
export RPC=<rpc> KEY=<privkey>
cast chain-id --rpc-url $RPC
cast call $SETUP "isSolved()(bool)" --rpc-url $RPC
cast call $SETUP "challenge()(address)" --rpc-url $RPC   # or the deploy log
cast call $CH "owner()(address)" "locked()(bool)" --rpc-url $RPC
cast balance $CH --rpc-url $RPC
for s in 0 1 2 3; do cast storage $CH $s --rpc-url $RPC; done
```

## The read-vs-write discipline

**Never send a write-shaped transaction before the read pass** — every `cast
send` is a permanent, attributable state change. Read `isSolved()`, the getters,
and the slots first; the cheapest solve (a bare setter) is found in the read,
not the first guessed transaction.

## The local-sim step

`forge init` a scratch project, write the attack contract, `forge test` it
against a fork (`forge test --fork-url $RPC`), or `cast call` the dry-run. The
simulation catches a wrong transition for free; the live `cast send` is the
solve.

## The decide/checkpoint hooks

- `classify.py` on the source signals names the class — `web-web3`.
- `hooks.py post-probe` for each probe: `confirms` needs `--verdict confirms
  --evidence <excerpt> --response <bytes>` — the `cast` output is the response.
- `decide.py` after a falsifier or 3 reverted txs — escalate rather than a
  4th variant of the same transition.

## The failure re-order

A reverted transaction → read the revert reason (`cast`/`forge` trace it), find
the failing `require`, and ask whether a DIFFERENT reachable transition reaches
the predicate. A wrong bug-class guess is the common cause — re-read the
predicate.
