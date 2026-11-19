# Troubleshoot (deep) — the failure-mode reference

## The revert-reason taxonomy

| Revert reason | The meaning | The fix |
|---|---|---|
| `Ownable: caller is not the owner` | the setter IS guarded | a different writer of the slot, or own the contract first |
| `execution reverted` (bare) | a `revert()`/`require` without a message | `cast run` the trace — find the failing op |
| `SafeMath: subtraction overflow` | SafeMath guarded the arithmetic | integer-overflow falsified on this path |
| `already initialized` | the init's flag is set | the context is initialized — the other context, or a different bug |
| `reentrancy guard` | the `nonReentrant` flag is set | reentrancy falsified, or a cross-function path |
| `out of gas` | the loop/call exceeded gas | bound the loop, or `--gas-limit` |
| `insufficient funds` | the caller can't cover `msg.value` + gas | fund the caller, or reduce the value |
| `invalid opcode`/`INVALID` | an `assert` failed or a bad jump | `cast run` — the invariant broke |
| `nonce too low/high` | the account's nonce off | `cast nonce` — set `--nonce` |

## The "the trace shows" workflow

```bash
cast run <txhash> --rpc-url $RPC            # the execution trace on the live chain
forge test --fork-url $RPC -vvvv            # a local fork trace with full detail
```

The trace's last `REVERT`/`INVALID` and the ops before it name the failing
`require` — read its condition from the source; that's the unmet precondition.

## The "the transition didn't flip the predicate" case

A `status: 0x1` tx + `isSolved()` still `false` → the transition changed a
DIFFERENT state. Re-read `isSolved()`'s slots; the sent call wrote a different
one — the reachable-call inventory names the right transition.

## The "the same-block value changed" case

A weak-randomness exploit that computes the answer then sends — the block moved
between compute and send → the answer changed. Compute the value in the SAME
transaction (a Predict contract calls `guess` in its own `attack`) or re-read
at send-time.

## The "the address is wrong" case

`cast: no contract at address` / the call hits nothing → the challenge address
is stale or the contract selfdestructed. Re-read it from the live setup;
`cast code` confirms code exists.

## The "the key won't sign" case

`invalid private key` / a `from` that isn't the supplied caller → the per-instance
key. `cast wallet address --private-key $KEY` confirms the caller; re-read the
key from the challenge.
