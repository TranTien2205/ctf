# Evidence rules — what a web3 solve actually looks like

## The proof is on-chain

A web3 solve is a **state change the checker reads**, not a string a response
returns. The evidence chain:

1. **the attributable transaction** — a tx from the supplied caller (or a
   contract it deployed) was mined: the receipt's `status: 0x1`, `from`, `to`,
   `transactionHash`.
2. **the predicate flipped** — `cast call $SETUP "isSolved()(bool)"` was `false`
   before and `true` after.
3. **the flag read** — the checker reads `isSolved()`; the flag is whatever the
   platform returns, recorded from that live response.

## What is NOT confirmation

| Looks like | Is not |
|---|---|
| a transaction with `status: 0x0` | a revert — the state did not change |
| a `forge test` / `cast call` simulation | local — the live chain is unchanged |
| a solve on a local Anvil fork | not the challenge instance |
| a solved predicate on someone else's RPC | not the supplied instance |
| a transaction that mined but didn't flip the predicate | a no-op — the exploit missed |
| a guessed private key or a key from a previous challenge | not the supplied caller |

## The verbatim record

Preserve, per solve:

```text
RPC endpoint (host only — never log the private key)
chain id                              — cast chain-id --rpc-url $RPC
setup address / challenge address
the solved predicate                  — the exact Solidity expression
the exploit calldata                  — the exact call sent
the transaction hash                  — the mined tx
the receipt                           — status, from, to, gasUsed
isSolved() before → after             — false → true verbatim
```

Never record the private key in notes — record that the supplied key was used.

## The receipt fields that matter

```
status            0x1 = mined & succeeded, 0x0 = reverted
from              must be the supplied caller (attribution)
to / contractAddress  the challenge, or the deployed attack contract
logs              emitted events — the state-change trace
gasUsed           confirms the tx executed
```

A `status: 0x1` with unchanged `isSolved()` means the wrong transition was
sent — the receipt alone is not the solve; the predicate is.

## The simulation-vs-live line

`cast call` (a dry-run) and `forge test` (a local fork) are **predictions**, not
proof — they never change the live chain. Only a `cast send` / a real signed
transaction does. Always dry-run the exploit locally first, then send for real
and re-read `isSolved()`.
