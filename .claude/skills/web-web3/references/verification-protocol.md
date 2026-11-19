# Verification protocol — how to be sure the solve is real

## The three-step verify

```bash
# 1. the tx mined and is attributable
cast receipt <txhash> --rpc-url $RPC        # status: 0x1, from: <caller>

# 2. the predicate flipped
cast call $SETUP "isSolved()(bool)" --rpc-url $RPC    # true (was false)

# 3. the checker returns the flag
# (the platform's response — record it verbatim)
```

## The from-check

`cast tx <txhash>`'s `from` field must equal `cast wallet address --private-key
$KEY` — the exploit is attributable to the supplied caller. A tx from a
different address isn't the solve.

## The state-check

`isSolved() → true` is necessary but a false-positive if it was ALREADY true —
always read it BEFORE the exploit too (`false → true`, not just `true`). A
challenge whose setup starts solved needs a different read of the predicate.

## The simulation-vs-live line

| The tool | The truth it proves |
|---|---|
| `cast call` (eth_call) | a dry-run — the predicate WOULD flip; NOT the solve |
| `forge test --fork-url` | a local fork — the exploit logic is sound; NOT the solve |
| `cast send` + `cast call` after | the live predicate flipped — the solve |

Never record a `call`/`forge` result as a solve — only the live `cast send` +
the re-read `isSolved()`.

## The multi-step verify

For an attack-contract chain: the deploy's `contractAddress`, each `cast send`'s
receipt, and the final `isSolved()` — every step's `from`/`status`/`to` preserved
in order.

## The hooks.py call

Capture the live `cast` output first, then pass it as `--response` so the
substring check validates the `isSolved()=true` quote against the real read:

```bash
RESP="$(cast call $SETUP 'isSolved()(bool)' --rpc-url $RPC; cast receipt <txhash> --rpc-url $RPC)"
python3 tools/hooks.py post-probe \
  --hypothesis-id <hN> --class web-web3 \
  --verdict confirms --evidence-kind impact \
  --evidence "isSolved()=true, tx=0x<hash>" \
  --response "$RESP"
```

The transaction receipt's `status: 0x1` and `from` field are the attribution;
the `isSolved()` read is the solved predicate. Both go inside `--response`.

## The "claimed but unverifiable" case

A solve on a fork, a solve that needed a different key, a solve that can't be
re-read — unverifiable. Re-run on the live instance with the supplied caller,
or report the exact blocker.
