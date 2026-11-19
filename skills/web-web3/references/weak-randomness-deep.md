# Weak randomness (deep) — every predictable-source shape

## The source inventory in full

| Source | Value | Predictability |
|---|---|---|
| `block.timestamp` | the block's time | same-block identical; a validator skews a few seconds |
| `block.number` | the block height | public, deterministic |
| `blockhash(n)` | hash of block `n` | public; `0` for `n` = current or `n` > 256 back |
| `block.difficulty` | pre-merge: PoW; post-merge: the beacon randao | public per-block |
| `block.prevrandao` | the beacon's randao | public per-block |
| `block.coinbase` | the block proposer | public |
| `block.basefee` | the EIP-1559 base fee | public, deterministic |
| `tx.gasprice` | the tx's gas price | the caller picks it |
| `block.gaslimit` | the block's gas cap | public |
| `keccak256(public-state)` | a hash of known values | reproducible — not a secret |
| `private`/`internal` var | storage | readable via `cast storage` — not a secret |
| `address(this).balance`/`extcodesize` | public chain state | readable |

## The shapes

### Same-block prediction

```solidity
uint answer = uint(keccak256(abi.encode(blockhash(block.number-1), block.timestamp)));
require(guess == answer);
```

A Predict contract computes the SAME hash in the SAME transaction — the
`blockhash`/`timestamp` are identical to the contract's → the answer is exact.

### The always-0 blockhash

```solidity
uint answer = uint(blockhash(block.number));   // ALWAYS 0 — current block has no hash
```

A contract that reads `blockhash(block.number)` computes on `0` — the answer
is `keccak(0...)` or `0`-based, trivially predictable.

### The stale-block blockhash

`blockhash(n)` returns `0` for `n` older than 256 blocks — a contract that uses
a too-old block's hash computes on `0`.

### The private-seed shape

```solidity
bytes32 private seed;   // "secret"
uint answer = uint(keccak256(abi.encode(seed, counter)));
```

`cast storage` reads the `private` `seed` — the answer is computable off-chain.

## The commit-reveal boundary

`commit(keccak256(value)) → reveal(value)` hides the answer until committed —
the FIX, not the bug. The bug is only a same-block-predictable source or a
`private`-but-readable seed.

## The two-block shapes

| Shape | The exploit |
|---|---|
| the answer in block N, guess in block N+1 | a contract that reads block N's public data — compute and submit in N+1 |
| the answer committed then revealed | a `commit` that uses a weak hash, or a `blockhash` that's `0` |

## The evidence

`isSolved() → true` after the Predict contract's `attack` tx; the contract's
stored answer matches the computed one. The Predict deploy + the attack tx are
the chain.
