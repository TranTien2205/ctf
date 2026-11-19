# Token standards — ERC-20 / 721 / 777 / 1155 bug surfaces

## ERC-20 surface

| Bug | The shape |
|---|---|
| integer wrap (pre-0.8) | `balances[me] - amt` underflows — the `Token`/`Ethernaut Token` shape |
| missing `transferFrom` allowance check | `transferFrom(from, to, amt)` without `allowance` check → move anyone's tokens |
| the `approve` race | `approve` A→B, owner front-runs `increaseAllowance` → both allowances spendable |
| decimals mismatch | the vault assumes `decimals=18`, the token is `6` — the rate is off by 1e12 |
| a `transfer` that doesn't check `to != 0` | burn via transfer to `address(0)`, or a mint the contract missed |
| a fee-on-transfer / rebasing token | the contract's accounting assumes `amount == received` — a fee/rebase desyncs it |
| `transfer` returns false not revert | the contract ignores the return — a failed transfer still credits |

## ERC-721 / 1155 surface

| Bug | The shape |
|---|---|
| `onERC721Received`/`onERC1155Received` hook | the recipient's hook re-enters the sender — the hook-reentrancy |
| a `safeTransfer` that checks the receiver's return | a forged return value, or a receiver that doesn't implement the hook |
| a `mint`/`tokenURI` that's callable | the unprotected mint |
| the approval/operator surface | `setApprovalForAll` left open, an operator that transfers |

## ERC-777 hook surface

`tokensReceived` — the token calls the recipient's hook mid-transfer →
reentrancy into the SENDER (the contract that initiated the transfer). The
same bug as `call`-reentrancy but entered through the token's hook. A
`tokensToSend` hook on the sender is the pre-transfer variant.

## The non-standard token trap

A "token" that isn't a standard ERC-20 — a custom `balanceOf`/`transfer` whose
semantics differ (returns data, no return, a different signature). The contract
assumes standard ERC-20 semantics that the token doesn't honor — a `transfer`
that returns false-vs-reverts, a `balanceOf` that lies.

## The detection fingerprint

- `balanceOf`/`transfer`/`transferFrom`/`approve`/`allowance`/`mint`/`burn`
- `totalSupply`/`decimals`/`name`/`symbol`
- `onERC*Received`/`tokensReceived`/`safeTransfer`
- **falsifier**: the token is a standard audited impl with no custom path, and
  the consuming contract's accounting can't be desynced

## The token-in-the-chain role

The token is rarely the bug alone — it's a component the challenge contract
trusts. A `vault` that assumes `deposit` moved `amount` tokens breaks on a
fee-on-transfer token; a `transferFrom` the challenge relies on to have checked
allowance. The exploit reads what the CHALLENGE contract assumes about the token
and finds the assumption the token violates.
