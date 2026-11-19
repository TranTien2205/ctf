# tx.origin map — the origin/sender check shapes indexed

## The check → the bypass

| The check | The bypass |
|---|---|
| `require(tx.origin != msg.sender)` — "must come through a contract" | a Phish contract the caller calls |
| `require(tx.origin == msg.sender)` — "must be an EOA" | a contract's CONSTRUCTOR call (extcodesize 0) |
| `require(tx.origin == <addr>)` — "must be that EOA" | only that EOA — or a contract they call |
| `owner = tx.origin` | any contract call records the origin — a Phish forwards |
| `require(msg.sender == tx.origin && extcodesize(msg.sender) == 0)` | a constructor call (codesize-0 during deploy) |
| `require(msg.sender.code.length == 0)` | a constructor call |

## The call-chain shapes

```
EOA --call--> Contract A --call--> Target
inside Target: tx.origin = EOA, msg.sender = A

EOA --call--> Contract.A.constructor --call--> Target
inside Target: tx.origin = EOA, msg.sender = A, extcodesize(A) = 0
```

## The Phish contract family

```solidity
// the intermediary — puts a contract in the chain
contract Phish { function attack(address t) external { ITarget(t).go(); } }

// the constructor-EOA — calls from the constructor
contract Tricky { constructor(address t) { ITarget(t).go(); } }

// the forwarder — records the origin
contract Fwd { function attack(address t, address me) external {
    ITarget(t).changeOwner(me); } }
```

## The CTF-vs-real-world split

| The case | The shape |
|---|---|
| CTF: the supplied caller IS the origin | a Phish the caller calls — the origin is the caller |
| real-world: the victim's origin | trick the victim into calling your contract — the phish |

## The falsifier map

| The falsifier | Closes |
|---|---|
| the check uses `msg.sender` correctly | the origin-confusion |
| no contract can be placed in the chain | the contract-in-middle (rare — the caller always can) |

## The detection order

```bash
grep -n "tx.origin" Challenge.sol         # the check
# read the check's exact form — !=, ==, =, the pairing with extcodesize
```

`tx-origin.md`/`tx-origin-deep.md` for the full shapes.
