# Reentrancy map — the re-entry shapes indexed

## The call-type → the reentrancy viability

| The call | Re-enter-able? |
|---|---|
| `call{value:}` / `call` (all gas) | YES — forwards gas, runs the callee |
| `call` with a gas limit | maybe — enough gas to re-enter? |
| `.transfer` | NO — 2300 gas, no room |
| `.send` | NO — 2300 gas (and returns false on fail) |
| `staticcall` | reads only — the read-only-reentrancy (an oracle) |
| `delegatecall` | the callee code on caller storage — a different bug |
| a token's `transfer`/`transferFrom` | only if the token calls back (ERC-777/721 hooks) |

## The function-shape → the bug

| Shape | The bug |
|---|---|
| `call` BEFORE the state update | single-function reentrancy |
| `call` shares state with a DIFFERENT function | cross-function reentrancy |
| a `call` whose callback reads a mid-state oracle | read-only reentrancy |
| a `token.transfer` that calls the recipient | the hook-reentrancy |
| a `call` inside a loop | the drain-loop reentrancy |

## The guard-shape → the bypass

| Guard | The status |
|---|---|
| a real `nonReentrant` on EVERY function sharing the state | closed |
| a `nonReentrant` on only the called function | a different function re-enters — open |
| a `locked` flag the callback can read/set | the flag is mid-state — open |
| a `.transfer` | the guard is the gas — closed |
| a `staticcall` check | reads a snapshot — the real state moved |

## The drain-completion order

```solidity
receive() external payable {
    if (address(v).balance >= withdrawAmt) v.withdraw(withdrawAmt);
    // bound by the balance — or a counter, or gasleft() > threshold
}
```

Bound the recursion — an unbounded loop runs out of gas and reverts the drain.

## The variants-file pointers

- the primitive semantics: `evm-primitives.md`
- the deep shapes: `reentrancy-deep.md`
- the exploit contract: `payload-families.md`, `exploitation-catalogue.md`
- the falsifier: `falsifiers.md`, `per-falsifier.md`
