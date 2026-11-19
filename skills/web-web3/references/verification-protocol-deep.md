# Verification protocol (deep) — the full proof procedure

## The four-step verify

```bash
# 0. BEFORE — the predicate reads false
cast call $SETUP "isSolved()(bool)" --rpc-url $RPC    # → false

# 1. the attributable tx mined
cast receipt <txhash> --rpc-url $RPC                   # status: 0x1, from: <caller>

# 2. the predicate flipped
cast call $SETUP "isSolved()(bool)" --rpc-url $RPC    # → true

# 3. the flag from the checker
#    (the platform's response — record verbatim)
```

## The attribution check

```bash
cast wallet address --private-key $KEY     # the supplied caller's address
cast tx <txhash> --rpc-url $RPC | grep -i from   # the tx's from — must match
```

The `from` must equal the supplied caller — a tx from a different key isn't the
solve.

## The status check

```
status 0x1  → the tx mined and didn't revert
status 0x0  → it REVERTED — the state rolled back — NOT a solve
```

A `status: 0x1` is necessary; `isSolved() → true` is the sufficiency.

## The live-vs-sim check

| The proof | The truth |
|---|---|
| `cast call` returning `true` | a dry-run — NOT the live solve |
| `forge test` passing | a fork — NOT the live solve |
| `cast send` + `cast call` after | the live chain flipped — the solve |

The live `cast send` + the re-read `isSolved()` is the ONLY solve proof.

## The multi-step verify

Each step's receipt + the getter read after — the ordered evidence:

```text
deploy Solver → contractAddress
tx1: the setup step → the receipt + the getter
tx2: the exploit step → the receipt + the getter
final: isSolved() → true
```

## The record

```text
instance:   the RPC host, the chain id
the caller: the supplied key's address (never the key)
the target: the setup + challenge addresses
the predicate: the isSolved() expression
the chain:  the ordered tx hashes + receipts
the state:  the before/after reads
the proof:  isSolved() false → true + the flag
```

## The unverifiable case

A solve that can't be re-read, a solve on a different instance, a solve needing
a different key — unverifiable. Re-run on the live instance with the supplied
caller, or report the blocker.
