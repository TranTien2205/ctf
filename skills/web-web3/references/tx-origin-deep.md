# tx.origin (deep) — every authorization-by-origin shape

## The exact semantics

`tx.origin` is the EOA that initiated the transaction — it is identical in every
call frame down the whole chain. `msg.sender` is the immediate caller and
changes at each `call`. The split is the whole class:

```
EOA --call--> A --call--> B --call--> Target
inside Target: tx.origin = EOA,  msg.sender = B
```

## The three exploit shapes

### 1. `require(tx.origin != msg.sender)` — must come through a contract

The check wants a contract in the middle — the supplied caller deploys a `Phish`
contract and calls `Phish.attack(target)`. Inside `Target`: `tx.origin` = the
caller EOA, `msg.sender` = Phish → `origin != sender` passes.

```solidity
contract Phish { function attack(address t) external { Target(t).go(); } }
```

### 2. `owner = tx.origin` / `require(tx.origin == victim)` — the phish

The target reads `tx.origin` as identity — a contract the VICTIM calls makes
`tx.origin` = victim while the contract performs the action. In CTF the supplied
caller IS the origin — a `Phish` contract forwards a call and the target
records the caller as `tx.origin`.

### 3. `require(tx.origin == msg.sender)` — the "EOA-only" check

The check wants NO contracts — defeated by a contract in its CONSTRUCTOR:
`extcodesize` of a deploying contract is `0`, so a check reading code-size or
just `origin == sender` passes while a contract calls.

```solidity
contract Tricky {
    constructor(address t) { Target(t).go(); }   // extcodesize == 0 during construction
}
```

## The auth-by-origin table

| Check | The bypass |
|---|---|
| `tx.origin != msg.sender` | a contract in the middle |
| `tx.origin == msg.sender` | a constructor call (extcodesize 0) — but origin==sender still; the EOA check that pairs it with codesize is the real target |
| `tx.origin == <address>` | only that EOA — or a contract they call |
| `owner = tx.origin` | any contract call records the origin — a Phish forwards |
| `msg.sender != tx.origin` for an "anti-bot" | a real contract satisfies it |

## The phishing distinction

In a real-world attack, `tx.origin` is the PHISHING primitive — trick an EOA
into calling your contract, and the contract forwards to a target that trusts
`tx.origin`. In CTF the supplied caller is both the origin and the attacker —
the Phish contract exists to put a contract in the middle of the call, not to
trick a third party.

## The paired check — `extcodesize`

`tx.origin == msg.sender` alone can't distinguish a contract constructor from
an EOA — both have `origin == sender`. The real "EOA-only" check is
`extcodesize(caller) == 0`, which the constructor ALSO passes (code-size 0
during deploy). The two checks pair: a `tx.origin == msg.sender &&
extcodesize(caller) == 0` is defeated by a constructor call.

## The evidence

`cast call $CH "owner()(address)"` = the caller after `Phish.attack`; the Phish
contract's deploy + the `attack` tx are the chain. The `cast tx` shows
`tx.origin` in the receipt context.
