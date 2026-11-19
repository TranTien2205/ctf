# Probe catalogue — the `cast` commands indexed

## The read probes (free, unattributable)

```bash
# the chain
cast chain-id --rpc-url $RPC
cast block-number --rpc-url $RPC

# the caller
cast wallet address --private-key $KEY
cast balance $ME --rpc-url $RPC
cast nonce $ME --rpc-url $RPC

# the contract
cast code $CH --rpc-url $RPC                       # the bytecode
cast balance $CH --rpc-url $RPC                    # its ether
cast call $CH "isSolved()(bool)" --rpc-url $RPC   # the predicate
cast call $CH "owner()(address)" --rpc-url $RPC    # a getter
cast storage $CH <slot> --rpc-url $RPC             # a slot — private too
cast index <key> <slot>                            # the mapping slot
cast keccak <data>                                 # the array-data slot

# the events / the txs
cast logs --rpc-url $RPC "address=$CH"             # the emitted logs
cast tx <txhash> --rpc-url $RPC                    # a past tx — constructor args
cast receipt <txhash> --rpc-url $RPC               # the receipt
cast run <txhash> --rpc-url $RPC                   # the execution trace
```

## The write probes (attributable, permanent)

```bash
cast send $CH "<sig>" <args> --private-key $KEY --rpc-url $RPC
cast send $CH "<sig>" <args> --value 1ether --private-key $KEY --rpc-url $RPC
cast send --create "<bin>" --private-key $KEY --rpc-url $RPC
forge create Solver --constructor-args $CH --private-key $KEY --rpc-url $RPC
```

## The utility probes

```bash
cast 4byte <selector>          # resolve a selector to a signature
cast sig "<fn-signature>"      # the selector for a signature
cast getAddress <deployer> <nonce>   # the CREATE address
cast compute-address --deployer <d> --salt <s> --init-code <bin>   # the CREATE2 address
cast abi-encode "<sig>" <args>  # encode args
cast to-hex <value>            # hex-encode
```

## The local-fork probes (simulation)

```bash
forge test --fork-url $RPC -vvvv     # the exploit on a fork + the trace
cast call $CH "fn()" --rpc-url $RPC  # a dry-run — state UNCHANGED
cast estimate $CH "fn()" --rpc-url $RPC  # the gas estimate
```

## The probe-order

Read probes first — the chain, the caller, the contract's state and code — then
the ONE planned `cast send`. The `forge`/`call` dry-run sits between the read
and the send — the simulation before the attributable action.
