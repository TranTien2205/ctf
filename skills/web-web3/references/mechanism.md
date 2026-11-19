# Mechanism — the setup-contract + solved-predicate challenge shape

The web3 class is not a web bug in the usual sense — there is no request
parameter to inject. The challenge ships a **Solidity contract**, an **RPC
endpoint**, and a **solved predicate**. The win is driving the contract's state
to satisfy the predicate with a transaction **attributable to the caller the
challenge supplies**.

## The challenge contract

```
Setup.sol           — deploys the challenge contract, holds the solved predicate
Challenge.sol       — the contract to attack
solve() / isSolved()— a view function the checker calls to grade
RPC endpoint        — a private chain; the flag is on solve()
private key         — the caller the challenge supplies
```

The checker calls `setup.isSolved()` (or `challenge.solved()`). It is `true`
when the state the challenge's author made hard to reach — an owner you are
not, a balance the contract should hold, a storage slot the code never writes —
is reached anyway.

## The read order

**Read the solved condition FIRST.** It names the exact state to reach:

```solidity
function isSolved() public view returns (bool) {
    return challenge.owner() == tx.origin;          // become the owner
    return challenge.balance() == 0;                // drain it
    return challenge.solvedFlag();                  // flip the flag
    return address(challenge).balance == 0;         // zero the ether
    return challenge.locked() == false;             // unlock it
}
```

The predicate names the class:
- `owner() == X` → an access-control / ownership-takeover path
- `balance == 0` → a drain path (reentrancy, selfdestruct, arithmetic)
- `flag` / `solved` → a state-flip path (an unprotected setter, a storage write)
- `locked == false` → an unlock path

## The state-transition view

A contract is a state machine. `isSolved()` reads state; the exploit is the
transaction that changes it. The question is always:

> **Which reachable external call changes the state `isSolved()` reads?**

The bug classes are the ways a call changes state the author did not intend:
- a **missing access check** — anyone calls the setter
- a **`tx.origin` check** — a phishing contract in the middle
- a **delegatecall** — foreign code writes this contract's storage
- a **reentrancy** — the callback re-enters before the state settles
- an **arithmetic** path — the counter wraps or the accounting lies
- a **storage collision** — a write lands on the wrong slot
- an **uninitialized proxy** — the implementation's init is callable

## The attributable-transaction rule

The exploit must be a transaction **from the supplied caller** (or through a
contract that caller deploys). A solve on a local fork, a reverted transaction,
a simulation, or a solve on someone else's instance is not a solve — the
checker reads the live chain.

## The evidence

The solve is **on-chain**: the `isSolved()` predicate goes `false → true` and
the transaction receipt proves the attributable transaction was mined. Preserve
the calldata, the tx hash, and the receipt.
