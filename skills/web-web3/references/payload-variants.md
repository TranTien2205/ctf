# Payload variants — the call-shape variants per class

## The `cast send` variants

```bash
# named-arg calls — the exact Solidity signature
cast send $CH "setOwner(address)" $ME --private-key $KEY --rpc-url $RPC
cast send $CH "changeOwner(address)" $ME --private-key $KEY --rpc-url $RPC
cast send $CH "unlock(bytes32)" 0x<pw> --private-key $KEY --rpc-url $RPC
cast send $CH "guess(uint256)" 42 --private-key $KEY --rpc-url $RPC
cast send $CH "claim(bytes,uint256)" 0x<sig> 100 --private-key $KEY --rpc-url $RPC

# the raw-selector call — when the signature is unknown
cast send $CH 0x<4byte-selector><encoded-args> --private-key $KEY --rpc-url $RPC

# the value call — a payable exploit
cast send $CH "deposit()" --value 1ether --private-key $KEY --rpc-url $RPC

# the fallback trigger — empty data hits receive(), non-empty hits fallback()
cast send $CH "" --private-key $KEY --rpc-url $RPC                    # receive()
cast send $CH 0x1234 --private-key $KEY --rpc-url $RPC                # fallback()
```

## The arg-encoding variants

```bash
cast send $CH "f(address)" 0x000000000000000000000000<addr> ...        # the padded address
cast send $CH "f(uint256)" 0x<64-hex> ...                              # the padded uint
cast send $CH "f(bytes32)" 0x<64-hex> ...                              # the bytes32
cast send $CH "f(bool)" true ...                                       # the bool
cast send $CH "f(string)" "the string" ...                              # the string
cast send $CH "f(address[])" "[0xA,0xB,0xC]" ...                       # the array
cast send $CH "f((uint256,bool))" "(1,true)" ...                       # the tuple
```

## The contract-call variants

```solidity
// a low-level call — when the function signature is raw bytes
(bool ok,) = t.call(abi.encodeWithSelector(0x12345678, arg));
// a value-forwarding call
(bool ok,) = t.call{value: msg.value}("");
// a delegatecall — runs t's code on THIS storage
(bool ok,) = t.delegatecall(abi.encodeWithSelector(sel, arg));
// a staticcall — read-only
(bool ok, bytes r) = t.staticcall(abi.encodeWithSelector(sel));
```

## The hook variants

```solidity
receive() external payable { /* ether-only call — the reentrancy hook */ }
fallback() external payable { /* non-empty unmatched call — the delegatecall/other hook */ }
```

`call{value}("")` → `receive`; `call{value}(0xdata)` → `fallback`. The exploit
needs the right hook for the call type the challenge sends.

## The deploy variants

```bash
forge create Solver --constructor-args $CH --private-key $KEY --rpc-url $RPC
forge create Solver --constructor-args $CH --value 1ether --private-key $KEY --rpc-url $RPC
cast send --create "<bin>" --private-key $KEY --rpc-url $RPC
cast send --create "<bin>" --value 1ether --private-key $KEY --rpc-url $RPC
```
