# Reentrancy variants — every callback shape

## The `call` family variants

| The call | The re-entry |
|---|---|
| `call{value:}` — the ether send | the `receive` hook — gas for a re-enter |
| `call` — a data call | the `fallback` hook — gas for a re-enter |
| `call` with a gas cap | maybe — enough gas to re-enter? measure `gasleft()` |
| `.transfer`/`.send` | no — 2300 gas |
| `staticcall` | no state — a read-only reentrancy oracle |
| `delegatecall` | a different bug — storage-write |

## The function-shape variants

### Single-function (the classic)

```solidity
function withdraw() { call{value:balances[me]}(""); balances[me] = 0; }
```

`receive` re-enters `withdraw` — `balances` still reads the old value.

### Cross-function

```solidity
function withdraw() { call(...); balances[me] = 0; }
function transfer(to, amt) { balances[to] += amt; /* reads balances[me] mid-state */ }
```

`receive` calls `transfer` — the shared `balances` is mid-transition.

### Cross-contract

`receive` calls a DIFFERENT contract that reads the first's mid-state — a
sister contract sharing the unsettled storage, or an oracle reading it.

### Read-only reentrancy

`receive` calls a THIRD contract's `getPrice` — which `staticcall`s the first
contract's `balanceOf` — reads the mid-transition value → the oracle lies to
the third contract.

## The token-hook variants

| The hook | The re-entry |
|---|---|
| ERC-777 `tokensReceived` | the token calls the recipient mid-transfer → re-enter the sender |
| ERC-721 `onERC721Received` | the recipient's hook — re-enter the safeTransfer sender |
| ERC-1155 `onERC1155Received` | the same |
| a `safeTransfer`/`mint` that calls the receiver | the receiver's hook re-enters |

## The nonReentrant variants

| Guard | The status |
|---|---|
| `nonReentrant` on every shared-state function | closed |
| `nonReentrant` on SOME functions | cross-function reentrancy survives |
| a `locked` flag the callback reads/sets | mid-state — open |
| a `staticcall`-check guard | snapshot — the real state moved |
| no guard | open |

## The drain-completion variants

```solidity
receive() external payable {
    if (address(v).balance >= msg.value) v.withdraw(msg.value);
    // OR bound by a counter:
    // if (count++ < 10) v.withdraw(1 ether);
    // OR bound by gas:
    // if (gasleft() > 50000) v.withdraw(1 ether);
}
```

Bound the recursion — an unbounded `receive` runs out of gas and the whole
drain reverts.

## The variants' falsifier

The call is `.transfer`/`.send`, or a real `nonReentrant` on every
shared-state function → the class is closed — `falsifiers.md`.
