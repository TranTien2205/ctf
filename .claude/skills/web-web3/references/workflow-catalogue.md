# Workflow catalogue — the per-shape procedure

## The single-setter procedure

```bash
# predicate reads owner()/locked()/flag → a bare setter is the cheapest solve
cast call $CH "owner()(address)" --rpc-url $RPC
cast send $CH "setOwner(address)" $ME --private-key $KEY --rpc-url $RPC
cast call $SETUP "isSolved()(bool)" --rpc-url $RPC   # verify
```

## The attack-contract procedure

```bash
# a primitive needs a deployed contract (reentrancy/phish/force-feed/predict)
forge create Solver --constructor-args $CH --private-key $KEY --rpc-url $RPC
# or funded:
cast send --create "<bin>" --value 1ether --private-key $KEY --rpc-url $RPC
cast send $SOLVER "run()" --private-key $KEY --rpc-url $RPC
cast call $SETUP "isSolved()(bool)" --rpc-url $RPC
```

## The dry-run procedure

```bash
# simulate before the attributable send
forge test --fork-url $RPC -vvvv     # the exploit on a local fork + the trace
# or a dry-run call:
cast call $CH "fn(args)" <args> --rpc-url $RPC   # simulates without sending
```

## The bytecode-only procedure

```bash
cast code $CH --rpc-url $RPC > code.evm
evm disasm code.evm | grep -E "PUSH4|SSTORE|SLOAD|DELEGATECALL|SELFDESTRUCT"
# the dispatch table + the storage-map = the reachable surface
```

## The multi-contract procedure

```bash
# the setup deploys several — map them
cast call $SETUP "challenge()(address)" "player()(address)" "token()(address)" --rpc-url $RPC
# which holds the predicate, which is the attack surface, which is a red herring
```

## The verify procedure

```bash
cast call $SETUP "isSolved()(bool)" --rpc-url $RPC   # false → true
cast receipt <txhash> --rpc-url $RPC                  # status 0x1, from = caller
cast tx <txhash> --rpc-url $RPC                       # the calldata + the from
```

## The per-shape order

| The shape | The order |
|---|---|
| a bare setter | read → send → verify |
| a contract-needing primitive | read → write the contract → deploy → run → verify |
| a bytecode-only target | code → disasm → SSTORE-map → the transition → send |
| a multi-contract setup | map the deploys → the predicate's contract → its surface |
| a wrong-state send | the trace → the unmet precondition → the predecessor that sets it |
