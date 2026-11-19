# First hour (deep) — the bounded opening in detail

## Minutes 0–10 — the environment + the predicate

```bash
export RPC=<rpc> KEY=<privkey>
cast chain-id --rpc-url $RPC
cast wallet address --private-key $KEY          # the attributable caller
cast call $SETUP "isSolved()(bool)" --rpc-url $RPC   # the predicate → false
cast call $SETUP "challenge()(address)" --rpc-url $RPC
cat Setup.sol; cat Challenge.sol                 # read the predicate first
```

The predicate names the class — `owner()` → access-control; `balance` → a drain;
`flag` → a setter/visibility. Record it.

## Minutes 10–25 — the state map

```bash
CH=<challenge>
cast call $CH "owner()(address)" "locked()(bool)" "solved()(bool)" --rpc-url $RPC
cast balance $CH --rpc-url $RPC
for s in 0 1 2 3 4 5; do cast storage $CH $s --rpc-url $RPC; done
cast code $CH --rpc-url $RPC | head -c 100
cast logs --rpc-url $RPC "address=$CH"            # emitted secrets
```

The `cast storage` reads the `private` + the predicate vars — the `private`
secret is the cheap solve if the predicate gates on it.

## Minutes 25–40 — the inventory + the class

```bash
grep -nE "function .*\(.*\).*(public|external)" Challenge.sol
grep -nE "delegatecall|tx.origin|block\.|selfdestruct|ecrecover|unchecked|private|call" Challenge.sol
```

The reachable functions + the signal keywords → the class + the transition.
The bare setter checked first — `setOwner`/`unlock`/`setFlag`/`initialize`.

## Minutes 40–50 — the dry-run

```bash
forge test --fork-url $RPC -vvvv     # or: cast call the exact call
```

The sim's `isSolved()` should flip — a sim-fail is free; fix the transition.

## Minutes 50–60 — the send + verify

```bash
cast send $CH "fn(args)" <args> --private-key $KEY --rpc-url $RPC
cast call $SETUP "isSolved()(bool)" --rpc-url $RPC   # → true
cast receipt <txhash> --rpc-url $RPC                  # status 0x1, from = caller
```

The solve = `isSolved() → true` + the receipt. Preserve the tx hash, the
calldata, the before/after reads.

## The stop rule

3 reverted txs on the same transition, or the reachable-writers enumeration
closed → `decide.py escalate`. The web3 budget is in transactions — the read +
the dry-run is where the iteration lives.
