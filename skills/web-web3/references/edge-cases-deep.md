# Edge cases (deep) — the odd corners of the EVM

## The construction window

A contract's `extcodesize` is `0` during construction — a contract calling from
its constructor is indistinguishable from an EOA by code-size. The
`tx.origin == msg.sender && extcodesize(caller) == 0` "EOA-only" check is
bypassed by a constructor call.

```solidity
contract Tricky { constructor(address t) { Target(t).go(); } }
```

## The `blockhash` traps

- `blockhash(block.number)` is ALWAYS `0` — the current block has no hash yet
- `blockhash(n)` for `n` more than 256 blocks back is `0`
- a "random" from `blockhash` is `0`-based or predictable — `weak-randomness`

## The selfdestruct corners

- `selfdestruct` to a contract that reverts — the ether still lands (no code run)
- `selfdestruct` to ITSELF — the ether is burned/lost
- `selfdestruct` the same-tx-created contract vs a prior-tx one — the Cancun
  rule differs; the force-send works either way
- a contract that checks `address(this).balance` — force-feed breaks it

## The CREATE2 corners

- the address is `keccak256(0xff . deployer . salt . keccak256(initcode))[12:]` — predictable
- a contract can be deployed to a "known empty" address — a check that read
  `extcodesize == 0` earlier is bypassed
- a selfdestructed contract can resurrect at the same address

## The `receive`/`fallback` corners

- `call{value}("")` → `receive` (or `fallback` if no `receive`)
- `call{value}(0xdata)` → `fallback`
- no `receive`/`fallback` → the plain ether `call` reverts — but `selfdestruct`/
  `coinbase` still delivers
- a `payable fallback` that reverts can't stop a force-feed

## The `msg.value`/`msg.data` corners

- `msg.value` in a `delegatecall` is the ORIGINAL value — preserved, not re-sent
- `msg.data` in a `fallback` is the raw unmatched calldata — route it
- `msg.sig` = `msg.data[:4]` — the selector

## The arithmetic corners

- `type(uint256).max + 1` wraps to `0` (pre-0.8) / reverts (`>=0.8`)
- `0 - 1` wraps to `2**256-1` / reverts
- `x / 0` reverts regardless of pragma
- `int` overflow vs `uint` — signed wraps at `2**255`
- `unchecked { }` on `>=0.8` deliberately wraps

## The ABI-encoding corners

- `abi.encodePacked(a, b)` collides for differently-split dynamic args
- a `bytes`/`string` longer than 31 bytes uses `keccak256(slot)` for the data
- the selector is `keccak256(sig)[0:4]` — a `cast 4byte` resolves it
