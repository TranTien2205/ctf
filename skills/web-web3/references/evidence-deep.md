# Evidence (deep) — the on-chain proof standard

## The solve is a state transition, not a string

A web3 challenge's "flag" isn't a response value — it's the checker reading
`isSolved() == true` on the live chain. The evidence chain is therefore:

```text
the attributable tx was mined     →  receipt.status == 0x1, receipt.from == caller
the predicate flipped             →  isSolved(): false → true, verbatim
the flag was returned             →  the checker's live response
```

## The receipt fields

```
transactionHash   — the tx id — preserve it
status            — 0x1 success, 0x0 reverted
from              — the attributable caller — must be the supplied key's address
to                — the challenge / the attack contract
contractAddress   — for a deploy, the new contract's address
logs              — emitted events — the state-change trace
gasUsed           — confirms execution ran
blockNumber       — the block it landed in
```

`cast receipt <hash>` and `cast tx <hash>` preserve these.

## The before/after reads

```bash
cast call $SETUP "isSolved()(bool)"   # BEFORE → false
# ... the exploit tx ...
cast call $SETUP "isSolved()(bool)"   # AFTER → true
```

The `false → true` transition on the live chain is the solve's proof. A
receipt's `status: 0x1` alone is a mined tx, not a solve — the predicate must
have flipped.

## What is NOT proof

| The claim | Why not |
|---|---|
| a `forge test` pass | the fork is local — live state unchanged |
| a `cast call` simulation | a dry-run — no state change |
| `status: 0x0` | the tx reverted — state rolled back |
| `status: 0x1` but `isSolved()` false | a mined no-op — the wrong transition |
| a solve on a different instance/RPC | per-instance — not the supplied chain |
| the `isSolved()` true BEFORE the exploit | the setup was already solved — re-check |

## The transaction-attribution rule

The exploit must be `from` the supplied caller — `cast tx`'s `from` field must
match `cast wallet address --private-key $KEY`. A transaction from a different
key, or a call that doesn't touch the supplied caller, isn't the solve.

## The verbatim record

```text
RPC host        — hostname only (never the URL's embedded key if it has one)
chain id        — cast chain-id
setup/challenge addresses
the predicate   — the exact isSolved() expression
the exploit     — the calldata / the attack-contract source
the tx hash     — the mined tx
the receipt     — status, from, to, gasUsed, logs
isSolved()      — false → true
```

## The chain's ordered evidence

A multi-step chain preserves EACH step's evidence: the deploy tx, each
`cast send`'s receipt, and the getter/storage read after each — the ordered
sequence proves the mechanism, not just the final flip.
