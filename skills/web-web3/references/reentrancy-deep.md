# Reentrancy (deep) — every re-entry shape

## The exact precondition

Reentrancy needs: an **external call to attacker code** (the `call` forwards
gas and runs `receive`/`fallback`) **before** the contract settles the state
the re-entered check reads. The bug is checks-effects-interactions violated —
the interaction (`call`) precedes the effect (the state write).

```solidity
// vulnerable: call BEFORE the update
(bool ok,) = msg.sender.call{value: amt}("");
balances[msg.sender] -= amt;              // settles AFTER — re-enter sees old balance
```

## The re-entry targets

### Single-function

`receive` calls the SAME function (`withdraw`) — the `balances[msg.sender]`
check passes again because the decrement hasn't landed. Drains until the
balance can't cover another call.

### Cross-function

`receive` calls a DIFFERENT function sharing the unsettled state —
`withdraw` → `transfer`/`donate`/`claim` while `balances` is mid-transition.
The shared-state function sees the pre-decrement balance.

### Cross-contract

The callback re-enters a SECOND contract that reads the first's state — a
sister contract sharing the unsettled storage or an oracle reading mid-state.

### Read-only reentrancy

A `staticcall`'d view function reads mid-transition state — a THIRD contract's
`getPrice`/`balanceOf` returns the stale value to a fourth contract that prices
on it. The reentrancy isn't into the vulnerable contract but into an oracle
that reads it mid-write.

## The ERC-777/721 hook shape

`tokensReceived` / `onERC721Received` — the TOKEN contract calls the recipient's
hook. A recipient that is attacker code re-enters the SENDER's function mid-
transfer — the same bug, entered through the token's hook rather than `call`.

## The nonReentrant guard shapes

```solidity
modifier nonReentrant() { require(!locked); locked = true; _; locked = false; }
```

- a real `nonReentrant` blocks re-entry — falsified
- a `staticcall`-only guard reads a snapshot — the real state changed mid-tx
- a per-function `locked` that a DIFFERENT function doesn't share → cross-function reentrancy survives
- `gasleft()`-gated re-entry — a `.transfer`'s 2300 gas is enough for a log but not a re-entering call → falsified

## The exploit contract's edge cases

```solidity
receive() external payable {
    if (gasleft() > 50000 && address(v).balance >= amt) v.withdraw(amt);
    // bound the recursion — an unbounded loop runs out of gas and reverts
}
```

- bound the recursion by the target's balance or a counter
- `receive` vs `fallback` — a `call{value}("")` triggers `receive` (empty data)
  or `fallback` (non-empty data); the exploit needs the right one
- a contract receiving ether needs `receive`/`fallback` `payable` or the
  funding `call` reverts

## The drain-completion case

`isSolved` may be `balance == 0` — re-enter until the contract can't pay another
full withdrawal, then a final partial withdrawal zeroes it. Or `isSolved` is a
flag on a count — re-enter to the count, not the full drain.

## The evidence

`cast balance $CH` → 0 (or `isSolved() → true`); the attack contract's deploy +
the `attack()` tx + the `receive`'s re-enter trace are the chain. `cast run
<txhash>` shows the recursive call stack.
