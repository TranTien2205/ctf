# Workflow steps — the operation as a checklist of commands

## The intake step

```bash
export RPC=<rpc> KEY=<privkey>
cast chain-id --rpc-url $RPC
cast wallet address --private-key $KEY       # the attributable caller
cast balance $ME --rpc-url $RPC              # the caller's funds
cat Setup.sol                                 # the predicate + the deploys
```

## The predicate step

```bash
cast call $SETUP "isSolved()(bool)" --rpc-url $RPC   # → false
cast call $SETUP "challenge()(address)" --rpc-url $RPC
# record the predicate's expression — the class it names
```

## The state step

```bash
CH=<challenge>
cast call $CH "owner()(address)" --rpc-url $RPC
cast call $CH "locked()(bool)" --rpc-url $RPC
cast balance $CH --rpc-url $RPC
for s in 0 1 2 3 4 5; do cast storage $CH $s --rpc-url $RPC; done
cast code $CH --rpc-url $RPC | wc -c
cast logs --rpc-url $RPC "address=$CH"
```

## The inventory step

```bash
# the source — the reachable non-view functions + the signals
grep -nE "function .*\(.*\).*(public|external)" Challenge.sol
grep -nE "delegatecall|tx.origin|block\.|selfdestruct|ecrecover|unchecked|private|call\{|call\(" Challenge.sol
# or the bytecode — the dispatch + the SSTORE map
cast code $CH --rpc-url $RPC | evm disasm | grep -E "PUSH4|SSTORE|DELEGATECALL|SELFDESTRUCT"
```

## The class step

```
the predicate + the reachable calls → ONE class + ONE transition + the falsifier
```

## The dry-run step

```bash
forge test --fork-url $RPC -vvvv      # the exploit on a fork
# or a dry-run:
cast call $CH "fn(args)" --rpc-url $RPC
```

## The send step

```bash
cast send $CH "fn(args)" <args> --private-key $KEY --rpc-url $RPC
# or the attack contract:
forge create Solver --constructor-args $CH --private-key $KEY --rpc-url $RPC
cast send $SOLVER "run()" --private-key $KEY --rpc-url $RPC
```

## The verify step

```bash
cast call $SETUP "isSolved()(bool)" --rpc-url $RPC   # → true
cast receipt <txhash> --rpc-url $RPC                  # status 0x1, from = caller
cast tx <txhash> --rpc-url $RPC
```

## The record step

```text
the predicate + the calldata + the tx hash + the receipt + the before/after reads
hooks.py post-probe --verdict confirms
```
