# Troubleshoot — when the transaction fails

## The symptom → the check

| Symptom | The check |
|---|---|
| `status: 0x0` / revert | `cast`/`forge` the trace — find the failing `require`; the precondition isn't met |
| `isSolved()` still false after a mined tx | the wrong transition was sent — re-read the predicate and the reachable-call inventory |
| `execution reverted` on a setter | the function IS guarded — the access-control class is falsified; find a different writer of the slot |
| `out of gas` | bump `--gas-limit`, or the loop/recursion is unbounded |
| the `receive` can't re-enter | the call is `.transfer` (2300 gas) — reentrancy falsified; a different drain |
| `cast: no contract at address` | the address is wrong or selfdestructed — re-read it from the setup |
| `invalid private key` / `nonce` | the per-instance key — re-read it from the challenge, never reuse |
| a `cast storage` reads `0x` | the var is at a hashed slot (mapping/array) — `cast index`/`cast keccak` it |
| the decompile differs from the `.sol` | trust the bytecode — `heimdall`/`panoramix`/`evm disasm` |

## The revert-reason read

```bash
cast send ... --rpc-url $RPC               # the revert surfaces a reason
# or trace the failing call:
cast run <txhash> --rpc-url $RPC           # the execution trace
forge test --fork-url $RPC -vvvv           # a local trace on the fork
```

The revert reason (or the failing `require` in the trace) names the unmet
precondition — set it before resending.

## The "simulation passed, live reverted" case

A `cast call`/`forge` pass but a `cast send` revert → the fork/sim's state
differed (a nonce, a block value, an unmocked precompile) OR the live chain's
state changed between sim and send. Re-read the state at send-time; a
block-dependent exploit must compute the value at send-time, not read-then-send.

## The "no reachable transition" case

Every external/public function enumerated, none writes the predicate's slot →
the class is falsified. The solve needs a different contract (the setup's other
deploy, a library, a token) or a different predicate interpretation — re-read
`isSolved()` and every contract the setup deploys.

## The budget check

3 reverted transactions on the same transition with no new revert reason →
`decide.py escalate`. A web3 challenge's budget is in TRANSACTIONS, not probes —
each `cast send` is attributable and permanent, so the enumeration/dry-run is
where the iteration lives.
