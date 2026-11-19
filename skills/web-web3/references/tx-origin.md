# tx.origin — the phishing-contract ownership check

## The shape

```solidity
function setOwner() public {
    require(tx.origin != msg.sender);   // "only callable through a contract"
    owner = tx.origin;                  // or: protected by origin
}
```

`tx.origin` is the EOA that STARTED the transaction — it never changes down a
call chain. `msg.sender` is the IMMEDIATE caller. A `tx.origin` check is a
phishing invite: a contract in the middle makes `tx.origin` the victim while
`msg.sender` is the attacking contract.

## The detection fingerprint

- `require(tx.origin == ...)`, `tx.origin != msg.sender`, `owner = tx.origin`
- any authorization or assignment that reads `tx.origin`
- **falsifier**: the check uses `msg.sender` correctly, or no contract can be
  placed in the call path

## The exploit

```solidity
contract Phish {
    function attack(address victim) external {
        Target(victim).protected();       // msg.sender = this contract
    }                                    // tx.origin = whoever called attack()
}
// the supplied caller calls attack() → Target sees tx.origin=caller, msg.sender=Phish
```

For `require(tx.origin != msg.sender)` (the "must come through a contract"
check): deploy `Phish`, the caller calls `Phish.attack(target)` — inside
`Target`, `tx.origin` = caller (an EOA), `msg.sender` = Phish → `origin !=
sender` passes.

For `owner = tx.origin` (the phish): trick the owner into calling `Phish` —
in CTF the supplied caller IS the origin, so `Phish` forwards a call and the
contract records the caller.

## The chain shape

The `tx.origin` bug needs an intermediary — a contract between the victim and
the target. In CTF the challenge supplies the caller, so the intermediary is a
contract the caller deploys:

```
supplied-caller(EOA) --calls--> Phish --calls--> Target
Target sees: tx.origin = supplied-caller, msg.sender = Phish
```

## The paired check

`require(tx.origin == msg.sender)` — "only an EOA, no contracts." Defeated by a
contract calling **from its constructor**: during construction `extcodesize ==
0`, so a contract under construction passes an "is EOA" check that reads
code size. (See `extcodesize` in `evm-primitives.md`.)

## The evidence

`cast call $TARGET "owner()(address)"` = the supplied caller; `isSolved()` →
true. The Phish contract's deploy tx + the `attack` tx are the chain.
